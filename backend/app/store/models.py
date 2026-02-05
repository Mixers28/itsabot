from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Platform(enum.Enum):
    reddit = "reddit"


class ItemKind(enum.Enum):
    post = "post"
    comment = "comment"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[Platform] = mapped_column(Enum(Platform), index=True)
    handle: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    snapshots: Mapped[List["Snapshot"]] = relationship(back_populates="account")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    post_count: Mapped[int] = mapped_column(Integer)
    comment_count: Mapped[int] = mapped_column(Integer)
    data_coverage_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    collector_version: Mapped[str] = mapped_column(String(32))

    account: Mapped["Account"] = relationship(back_populates="snapshots")
    items: Mapped[List["Item"]] = relationship(back_populates="snapshot", cascade="all, delete-orphan")
    features: Mapped[Optional["FeatureSet"]] = relationship(
        back_populates="snapshot", cascade="all, delete-orphan", uselist=False
    )
    scores: Mapped[Optional["Score"]] = relationship(
        back_populates="snapshot", cascade="all, delete-orphan", uselist=False
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshots.id"), index=True)
    kind: Mapped[ItemKind] = mapped_column(Enum(ItemKind))
    item_id: Mapped[str] = mapped_column(String(32), index=True)
    created_utc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    subreddit: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    permalink: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    snapshot: Mapped["Snapshot"] = relationship(back_populates="items")


class FeatureSet(Base):
    __tablename__ = "features"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshots.id"), unique=True)
    json: Mapped[dict] = mapped_column(JSON)

    snapshot: Mapped["Snapshot"] = relationship(back_populates="features")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshots.id"), unique=True)
    automation_score: Mapped[int] = mapped_column(Integer)
    coordination_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reasons: Mapped[dict] = mapped_column(JSON)
    explanations: Mapped[dict] = mapped_column(JSON)

    snapshot: Mapped["Snapshot"] = relationship(back_populates="scores")
