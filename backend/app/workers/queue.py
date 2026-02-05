from rq import Queue

from app.utils.redis_client import get_redis


def get_queue(name: str = "default") -> Queue:
    redis = get_redis()
    return Queue(name, connection=redis)
