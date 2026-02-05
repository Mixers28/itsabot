import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth

from app.config import settings
from app.utils.cache import RedisCache
from app.utils.rate_limit import RateLimiter, backoff_from_headers


TOKEN_CACHE: dict[str, float | str] = {}


@dataclass
class RedditProfile:
    username: str
    created_utc: Optional[float]
    link_karma: Optional[int]
    comment_karma: Optional[int]


class RedditClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.reddit_user_agent})
        self.cache = RedisCache(prefix="reddit")
        self.rate_limiter = RateLimiter("rate:reddit")

    def _get_token(self) -> str:
        cached_token = TOKEN_CACHE.get("access_token")
        expires_at = TOKEN_CACHE.get("expires_at", 0)
        if cached_token and isinstance(expires_at, float) and time.time() < expires_at:
            return str(cached_token)

        if not settings.reddit_client_id or not settings.reddit_client_secret:
            raise RuntimeError("Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET")

        auth = HTTPBasicAuth(settings.reddit_client_id, settings.reddit_client_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": settings.reddit_user_agent}
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        token = payload["access_token"]
        expires_in = payload.get("expires_in", 3600)
        TOKEN_CACHE["access_token"] = token
        TOKEN_CACHE["expires_at"] = time.time() + float(expires_in) - 60
        return token

    def _get(self, url: str, params: Optional[dict] = None) -> dict:
        self.rate_limiter.wait_for_slot()
        token = self._get_token()
        headers = {"Authorization": f"bearer {token}", "User-Agent": settings.reddit_user_agent}
        response = self.session.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 429:
            time.sleep(5)
            response = self.session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        backoff_from_headers(response.headers)
        return response.json()

    def fetch_profile(self, username: str) -> RedditProfile:
        cache_key = f"profile:{username}"
        cached = self.cache.get_json(cache_key)
        if cached:
            return RedditProfile(**cached)

        url = f"https://oauth.reddit.com/user/{username}/about"
        payload = self._get(url)
        data = payload.get("data", {})
        profile = RedditProfile(
            username=username,
            created_utc=data.get("created_utc"),
            link_karma=data.get("link_karma"),
            comment_karma=data.get("comment_karma"),
        )
        self.cache.set_json(cache_key, profile.__dict__, ttl_seconds=3600)
        return profile

    def fetch_listing(self, username: str, listing: str, limit: int) -> List[dict]:
        items: List[dict] = []
        after: Optional[str] = None
        fetched = 0
        while fetched < limit:
            batch = min(100, limit - fetched)
            params = {"limit": batch}
            if after:
                params["after"] = after
            cache_key = f"listing:{username}:{listing}:{after}:{batch}"
            cached = self.cache.get_json(cache_key)
            if cached:
                payload = cached
            else:
                url = f"https://oauth.reddit.com/user/{username}/{listing}"
                payload = self._get(url, params=params)
                self.cache.set_json(cache_key, payload, ttl_seconds=300)
            data = payload.get("data", {})
            children = data.get("children", [])
            if not children:
                break
            for child in children:
                items.append(child.get("data", {}))
            after = data.get("after")
            fetched = len(items)
            if not after:
                break
        return items[:limit]


def parse_username(input_value: str) -> str:
    if "reddit.com" in input_value:
        parsed = urlparse(input_value)
        parts = parsed.path.strip("/").split("/")
        if "user" in parts:
            idx = parts.index("user")
        elif "u" in parts:
            idx = parts.index("u")
        else:
            raise ValueError("Unable to parse Reddit username from URL")
        return parts[idx + 1]
    return input_value.lstrip("u/")


def normalize_items(submissions: List[dict], comments: List[dict]) -> List[dict]:
    items: List[dict] = []
    for post in submissions:
        items.append(
            {
                "kind": "post",
                "item_id": post.get("name"),
                "created_utc": post.get("created_utc"),
                "subreddit": post.get("subreddit"),
                "permalink": f"https://www.reddit.com{post.get('permalink', '')}",
                "body_text": post.get("selftext") or None,
                "url": post.get("url"),
                "link_id": None,
                "parent_id": None,
            }
        )
    for comment in comments:
        items.append(
            {
                "kind": "comment",
                "item_id": comment.get("name"),
                "created_utc": comment.get("created_utc"),
                "subreddit": comment.get("subreddit"),
                "permalink": f"https://www.reddit.com{comment.get('permalink', '')}",
                "body_text": comment.get("body") or None,
                "url": None,
                "link_id": comment.get("link_id"),
                "parent_id": comment.get("parent_id"),
            }
        )
    return items


def collect_user(username_or_url: str, max_items: Optional[int] = None) -> Tuple[RedditProfile, List[dict]]:
    username = parse_username(username_or_url)
    client = RedditClient()
    profile = client.fetch_profile(username)
    max_items = max_items or settings.reddit_max_items
    submission_limit = max_items // 2
    comment_limit = max_items - submission_limit
    submissions = client.fetch_listing(username, "submitted", submission_limit)
    comments = client.fetch_listing(username, "comments", comment_limit)
    items = normalize_items(submissions, comments)
    return profile, items
