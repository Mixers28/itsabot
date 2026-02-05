from __future__ import annotations

import math
from typing import Dict, List


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    k = (len(values_sorted) - 1) * pct
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values_sorted[int(k)]
    d0 = values_sorted[int(f)] * (c - k)
    d1 = values_sorted[int(c)] * (k - f)
    return d0 + d1


def _coefficient_of_variation(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance) / mean


def compute_timing_features(items: List[dict]) -> Dict[str, float | int | list]:
    timestamps = [i.get("created_utc") for i in items if i.get("created_utc")]
    timestamps = sorted([float(ts) for ts in timestamps if ts is not None])
    total_items = len(items)
    if timestamps:
        span_seconds = max(timestamps) - min(timestamps)
        span_days = max(span_seconds / 86400, 1.0)
    else:
        span_days = 1.0

    posts = [i for i in items if i.get("kind") == "post"]
    comments = [i for i in items if i.get("kind") == "comment"]
    posts_per_day = len(posts) / span_days
    comments_per_day = len(comments) / span_days

    hours = [0] * 24
    for ts in timestamps:
        hour = int((ts % 86400) // 3600)
        hours[hour] += 1

    gaps = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
    gap_hours = [g / 3600 for g in gaps if g > 0]
    sleep_gap_hours_p95 = _percentile(gap_hours, 0.95) if gap_hours else 0.0
    burstiness_index = _coefficient_of_variation(gaps) if gaps else 0.0
    regularity_score = 1 / (1 + burstiness_index) if burstiness_index else 0.0

    timestamp_completeness = len(timestamps) / total_items if total_items else 0.0

    return {
        "posts_per_day": posts_per_day,
        "comments_per_day": comments_per_day,
        "active_hours_histogram": hours,
        "sleep_gap_hours_p95": sleep_gap_hours_p95,
        "burstiness_index": burstiness_index,
        "regularity_score": regularity_score,
        "span_days": span_days,
        "total_items": total_items,
        "timestamp_completeness": timestamp_completeness,
    }
