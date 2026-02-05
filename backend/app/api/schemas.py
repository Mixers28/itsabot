from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    username: str
    force_refresh: bool = False


class AnalyzeResponse(BaseModel):
    job_id: Optional[str]
    status: str
    report_url: Optional[str] = None
    report: Optional[dict] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result_url: Optional[str] = None
    progress: Optional[float] = None


class ReportResponse(BaseModel):
    username: str
    snapshot_id: int
    scores: dict
    features: dict
    reasons: list
    explanations: dict


class HistoryItem(BaseModel):
    snapshot_id: int
    collected_at: str
    automation_score: int
    coordination_score: Optional[int]
    confidence: Optional[float]


class HistoryResponse(BaseModel):
    username: str
    snapshots: list[HistoryItem]
