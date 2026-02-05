import json
from typing import Any, Optional

from app.utils.redis_client import get_redis


class RedisCache:
    def __init__(self, prefix: str = "cache"):
        self.prefix = prefix
        self.redis = get_redis()

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    def get_json(self, key: str) -> Optional[dict]:
        try:
            value = self.redis.get(self._key(key))
        except Exception:
            return None
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, payload: dict, ttl_seconds: int) -> None:
        value = json.dumps(payload)
        try:
            self.redis.setex(self._key(key), ttl_seconds, value)
        except Exception:
            return

    def get(self, key: str) -> Optional[str]:
        try:
            value = self.redis.get(self._key(key))
        except Exception:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        try:
            self.redis.setex(self._key(key), ttl_seconds, value)
        except Exception:
            return
