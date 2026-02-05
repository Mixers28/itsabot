import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/bot_likelihood",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "bot-likelihood-analyzer/0.1")
    reddit_max_items: int = int(os.getenv("REDDIT_MAX_ITEMS", "200"))
    collector_version: str = os.getenv("COLLECTOR_VERSION", "v0.1")
    cache_hours: int = int(os.getenv("CACHE_HOURS", "6"))
    rate_limit_qpm: int = int(os.getenv("REDDIT_QPM_LIMIT", "100"))
    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "*")


settings = Settings()
