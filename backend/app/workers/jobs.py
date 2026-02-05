from __future__ import annotations

from typing import Dict

from sqlalchemy import select

from app.collectors.reddit import collect_user
from app.config import settings
from app.features import compute_features
from app.scoring.rules_v1 import score
from app.store.db import get_session
from app.store.models import Account, FeatureSet, Item, ItemKind, Platform, Score, Snapshot


def analyze_reddit_user(username_or_url: str) -> Dict[str, object]:
    profile, items = collect_user(username_or_url, settings.reddit_max_items)
    features = compute_features(items)
    score_payload, _ = score(features, profile.__dict__, items)

    post_count = len([i for i in items if i.get("kind") == "post"])
    comment_count = len([i for i in items if i.get("kind") == "comment"])
    span_days = int(features.get("timing", {}).get("span_days", 0) or 0)

    with get_session() as session:
        account = session.execute(
            select(Account).where(Account.platform == Platform.reddit, Account.handle == profile.username)
        ).scalar_one_or_none()
        if account is None:
            account = Account(platform=Platform.reddit, handle=profile.username)
            session.add(account)
            session.flush()

        snapshot = Snapshot(
            account_id=account.id,
            post_count=post_count,
            comment_count=comment_count,
            data_coverage_days=span_days,
            collector_version=settings.collector_version,
        )
        session.add(snapshot)
        session.flush()

        for item in items:
            session.add(
                Item(
                    snapshot_id=snapshot.id,
                    kind=ItemKind.post if item.get("kind") == "post" else ItemKind.comment,
                    item_id=item.get("item_id") or "",
                    created_utc=item.get("created_utc"),
                    subreddit=item.get("subreddit"),
                    permalink=item.get("permalink"),
                    body_text=item.get("body_text"),
                    url=item.get("url"),
                    link_id=item.get("link_id"),
                    parent_id=item.get("parent_id"),
                )
            )

        session.add(FeatureSet(snapshot_id=snapshot.id, json=features))
        session.add(
            Score(
                snapshot_id=snapshot.id,
                automation_score=score_payload["automation_score"],
                coordination_score=score_payload["coordination_score"],
                confidence=score_payload["confidence"],
                reasons=score_payload["reasons"],
                explanations=score_payload["explanations"],
            )
        )

        session.flush()

        return {
            "snapshot_id": snapshot.id,
            "username": profile.username,
            "scores": score_payload,
        }
