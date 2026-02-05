from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from rq.job import Job
from sqlalchemy import select

from app.api.schemas import AnalyzeRequest, AnalyzeResponse, HistoryItem, HistoryResponse, JobStatusResponse, ReportResponse
from app.collectors.reddit import parse_username
from app.config import settings
from app.store.db import get_session
from app.store.models import Account, Platform, Score, Snapshot
from app.utils.cache import RedisCache
from app.utils.redis_client import get_redis
from app.workers.jobs import analyze_reddit_user
from app.workers.queue import get_queue


router = APIRouter(prefix="/api", tags=["api"])
logger = logging.getLogger("api")


def _get_latest_snapshot(account_id: int) -> Optional[Snapshot]:
    with get_session() as session:
        return (
            session.execute(
                select(Snapshot)
                .where(Snapshot.account_id == account_id)
                .order_by(Snapshot.collected_at.desc())
                .limit(1)
            ).scalar_one_or_none()
        )


def _build_report(snapshot: Snapshot) -> ReportResponse:
    scores = snapshot.scores
    features = snapshot.features
    account = snapshot.account
    return ReportResponse(
        username=account.handle,
        snapshot_id=snapshot.id,
        scores={
            "automation_score": scores.automation_score if scores else None,
            "coordination_score": scores.coordination_score if scores else None,
            "confidence": scores.confidence if scores else None,
        },
        features=features.json if features else {},
        reasons=scores.reasons if scores else [],
        explanations=scores.explanations if scores else {},
    )


@router.post("/analyze/reddit", response_model=AnalyzeResponse)
def analyze_reddit(request: AnalyzeRequest):
    username = parse_username(request.username)

    with get_session() as session:
        account = session.execute(
            select(Account).where(Account.platform == Platform.reddit, Account.handle == username)
        ).scalar_one_or_none()
        if account:
            snapshot = (
                session.execute(
                    select(Snapshot)
                    .where(Snapshot.account_id == account.id)
                    .order_by(Snapshot.collected_at.desc())
                    .limit(1)
                ).scalar_one_or_none()
            )
            if snapshot and not request.force_refresh:
                cutoff = datetime.utcnow() - timedelta(hours=settings.cache_hours)
                if snapshot.collected_at and snapshot.collected_at > cutoff:
                    report_url = f"/api/report/reddit/{username}?snapshot=latest"
                    return AnalyzeResponse(job_id=f"cached:{snapshot.id}", status="cached", report_url=report_url)

    queue = get_queue()
    job = queue.enqueue(analyze_reddit_user, username)
    logger.info("job_enqueue username=%s job_id=%s", username, job.id)
    return AnalyzeResponse(job_id=job.id, status="queued")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: str):
    if job_id.startswith("cached:"):
        return JobStatusResponse(
            job_id=job_id,
            status="cached",
            result_url=None,
        )

    redis = get_redis()
    try:
        job = Job.fetch(job_id, connection=redis)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    status = job.get_status()
    progress = job.meta.get("progress") if isinstance(job.meta, dict) else None
    logger.info("job_status job_id=%s status=%s progress=%s", job_id, status, progress)
    result_url = None
    result = job.return_value() if hasattr(job, "return_value") else job.result
    if status == "finished" and isinstance(result, dict):
        snapshot_id = result.get("snapshot_id")
        if snapshot_id:
            result_url = f"/api/report/reddit/{result.get('username')}?snapshot={snapshot_id}"

    return JobStatusResponse(job_id=job_id, status=status, result_url=result_url, progress=progress)


@router.get("/report/reddit/{username}", response_model=ReportResponse)
def get_report(username: str, snapshot: str = "latest"):
    cache = RedisCache(prefix="report")
    with get_session() as session:
        account = session.execute(
            select(Account).where(Account.platform == Platform.reddit, Account.handle == username)
        ).scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        query = select(Snapshot).where(Snapshot.account_id == account.id)
        if snapshot == "latest":
            query = query.order_by(Snapshot.collected_at.desc()).limit(1)
        else:
            query = query.where(Snapshot.id == int(snapshot))
        snapshot_obj = session.execute(query).scalar_one_or_none()
        if not snapshot_obj:
            raise HTTPException(status_code=404, detail="Snapshot not found")

        cache_key = f"{username}:{snapshot_obj.id}"
        cached = cache.get_json(cache_key)
        if cached:
            return cached

        _ = snapshot_obj.scores
        _ = snapshot_obj.features
        _ = snapshot_obj.account
        report = _build_report(snapshot_obj)
        cache.set_json(cache_key, report.model_dump(), ttl_seconds=3600)
        return report


@router.get("/history/reddit/{username}", response_model=HistoryResponse)
def history(username: str):
    with get_session() as session:
        account = session.execute(
            select(Account).where(Account.platform == Platform.reddit, Account.handle == username)
        ).scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        snapshots = session.execute(
            select(Snapshot).where(Snapshot.account_id == account.id).order_by(Snapshot.collected_at.desc())
        ).scalars()

        items = []
        for snapshot in snapshots:
            score = snapshot.scores
            items.append(
                HistoryItem(
                    snapshot_id=snapshot.id,
                    collected_at=snapshot.collected_at.isoformat() if snapshot.collected_at else "",
                    automation_score=score.automation_score if score else 0,
                    coordination_score=score.coordination_score if score else None,
                    confidence=score.confidence if score else None,
                )
            )

        return HistoryResponse(username=username, snapshots=items)


@router.get("/health/reddit-credentials")
def reddit_credentials_health():
    try:
        from app.collectors.reddit import RedditClient

        client = RedditClient()
        client._get_token()
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
