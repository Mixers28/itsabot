import time

from app.config import settings
from app.utils.redis_client import get_redis


class RateLimiter:
    def __init__(self, key: str, limit_per_minute: int | None = None) -> None:
        self.key = key
        self.limit = limit_per_minute or settings.rate_limit_qpm
        self.redis = get_redis()

    def wait_for_slot(self) -> None:
        try:
            current = self.redis.incr(self.key)
            if current == 1:
                self.redis.expire(self.key, 60)
            if current > self.limit:
                ttl = self.redis.ttl(self.key)
                sleep_for = max(ttl, 1)
                time.sleep(sleep_for)
        except Exception:
            return


def backoff_from_headers(headers: dict) -> None:
    remaining = headers.get("X-Ratelimit-Remaining")
    reset = headers.get("X-Ratelimit-Reset")
    if remaining is None or reset is None:
        return
    try:
        remaining_val = float(remaining)
        reset_val = float(reset)
    except ValueError:
        return
    if remaining_val <= 1:
        time.sleep(max(reset_val, 1))
