from __future__ import annotations

import math
import time
from typing import Dict, List, Tuple


def _scale_points(value: float, low: float, high: float, min_points: int, max_points: int) -> int:
    if value <= low:
        return 0
    if value >= high:
        return max_points
    ratio = (value - low) / (high - low)
    return int(round(min_points + ratio * (max_points - min_points)))


def _inverse_scale_points(value: float, low: float, high: float, min_points: int, max_points: int) -> int:
    if value >= high:
        return 0
    if value <= low:
        return max_points
    ratio = (high - value) / (high - low)
    return int(round(min_points + ratio * (max_points - min_points)))


def compute_confidence(features: Dict[str, dict]) -> float:
    timing = features.get("timing", {})
    total_items = timing.get("total_items", 0) or 0
    span_days = timing.get("span_days", 0) or 0
    completeness = timing.get("timestamp_completeness", 0) or 0

    volume_factor = min(1.0, total_items / 200)
    span_factor = min(1.0, span_days / 30)
    completeness_factor = min(1.0, completeness)

    base = 0.5 * volume_factor + 0.3 * span_factor + 0.2 * completeness_factor
    penalty = 0.3 if total_items < 30 else 0.0
    return max(0.0, min(1.0, base - penalty))


def score(features: Dict[str, dict], profile: dict, items: List[dict]) -> Tuple[dict, List[dict]]:
    timing = features.get("timing", {})
    repetition = features.get("repetition", {})
    content = features.get("content", {})
    interaction = features.get("interaction", {})

    reasons: List[dict] = []
    explanations: List[dict] = []

    posts_per_day = timing.get("posts_per_day", 0) or 0
    comments_per_day = timing.get("comments_per_day", 0) or 0
    activity_per_day = posts_per_day + comments_per_day

    # Activity score
    activity_points = _scale_points(activity_per_day, low=20, high=200, min_points=8, max_points=25)
    if activity_points:
        reasons.append(
            {
                "title": "Very high activity volume",
                "impact": activity_points,
                "evidence": _sample_permalinks(items, 3),
                "details": f"Average activity {activity_per_day:.1f}/day across collected span.",
            }
        )

    # Cadence regularity (low CV)
    burstiness = timing.get("burstiness_index", 0) or 0
    cadence_points = _inverse_scale_points(burstiness, low=0.1, high=1.0, min_points=8, max_points=15)
    if cadence_points:
        reasons.append(
            {
                "title": "Unusually regular posting cadence",
                "impact": cadence_points,
                "evidence": [],
                "details": f"Inter-arrival CV {burstiness:.2f} suggests regular timing.",
            }
        )

    # Sleep gap
    sleep_gap = timing.get("sleep_gap_hours_p95", 0) or 0
    sleep_points = _inverse_scale_points(sleep_gap, low=3, high=8, min_points=8, max_points=15)
    if sleep_points:
        reasons.append(
            {
                "title": "Low extended idle time",
                "impact": sleep_points,
                "evidence": [],
                "details": f"95th percentile gap {sleep_gap:.1f} hours.",
            }
        )

    # Duplicate rate
    dup_rate = repetition.get("near_duplicate_rate", 0) or 0
    dup_points = _scale_points(dup_rate, low=0.1, high=0.6, min_points=8, max_points=30)
    if dup_points:
        reasons.append(
            {
                "title": "High near-duplicate rate",
                "impact": dup_points,
                "evidence": _sample_permalinks(items, 3),
                "details": f"Duplicate rate {dup_rate:.2f}.",
            }
        )

    # Domain concentration
    domain_concentration = repetition.get("link_domain_concentration", 0) or 0
    domain_points = _scale_points(domain_concentration, low=0.3, high=0.8, min_points=8, max_points=15)
    if domain_points:
        reasons.append(
            {
                "title": "Single domain dominates",
                "impact": domain_points,
                "evidence": _sample_permalinks(items, 3),
                "details": f"Top domain share {domain_concentration:.2f}.",
            }
        )

    # Subreddit concentration
    subreddit_entropy = repetition.get("subreddit_entropy", 1) or 1
    subreddit_concentration = 1 - subreddit_entropy
    subreddit_points = _scale_points(subreddit_concentration, low=0.4, high=0.9, min_points=8, max_points=10)
    if subreddit_points:
        reasons.append(
            {
                "title": "Subreddit concentration",
                "impact": subreddit_points,
                "evidence": [],
                "details": f"Subreddit concentration {subreddit_concentration:.2f}.",
            }
        )

    # Short / generic comments
    short_comment_rate = _short_comment_rate(items)
    short_points = 10 if short_comment_rate >= 0.6 else 0
    if short_points:
        reasons.append(
            {
                "title": "Many very short comments",
                "impact": short_points,
                "evidence": _sample_permalinks([i for i in items if i.get("kind") == "comment"], 3),
                "details": f"Short comment rate {short_comment_rate:.2f}.",
            }
        )

    # URL-heavy posting
    url_rate = content.get("url_rate", 0) or 0
    url_points = _scale_points(url_rate, low=0.3, high=0.8, min_points=5, max_points=15)
    if url_points:
        reasons.append(
            {
                "title": "URL-heavy posting",
                "impact": url_points,
                "evidence": _sample_permalinks([i for i in items if i.get("url")], 3),
                "details": f"URL rate {url_rate:.2f}.",
            }
        )

    # New account high activity
    account_age_days = _account_age_days(profile)
    new_account_points = 0
    if account_age_days is not None and account_age_days < 30 and activity_per_day > 50:
        new_account_points = _scale_points(activity_per_day, low=50, high=200, min_points=6, max_points=10)
        reasons.append(
            {
                "title": "High activity on a new account",
                "impact": new_account_points,
                "evidence": _sample_permalinks(items, 3),
                "details": f"Account age {account_age_days:.0f} days.",
            }
        )

    # Low thread diversity
    comments = [i for i in items if i.get("kind") == "comment"]
    thread_count = interaction.get("unique_threads_replied_to", 0) or 0
    thread_diversity = thread_count / max(len(comments), 1)
    thread_points = 8 if len(comments) > 20 and thread_diversity < 0.2 else 0
    if thread_points:
        reasons.append(
            {
                "title": "Low thread diversity",
                "impact": thread_points,
                "evidence": _sample_permalinks(comments, 3),
                "details": f"Thread diversity ratio {thread_diversity:.2f}.",
            }
        )

    automation_score = min(100, sum(r["impact"] for r in reasons))

    coordination_score = _coordination_proxy_score(dup_rate, domain_concentration, subreddit_entropy)

    confidence = compute_confidence(features)

    explanations = {
        "coverage": features.get("coverage_flags", {}),
        "confidence": confidence,
    }

    return {
        "automation_score": automation_score,
        "coordination_score": coordination_score,
        "confidence": confidence,
        "reasons": reasons,
        "explanations": explanations,
    }, reasons


def _coordination_proxy_score(dup_rate: float, domain_concentration: float, subreddit_entropy: float) -> int:
    concentration = 1 - subreddit_entropy
    score = (dup_rate * 0.4 + domain_concentration * 0.3 + concentration * 0.3) * 100
    return int(max(0, min(100, round(score))))


def _short_comment_rate(items: List[dict]) -> float:
    comments = [i for i in items if i.get("kind") == "comment" and i.get("body_text")]
    if not comments:
        return 0.0
    short = [i for i in comments if len(i.get("body_text", "")) < 20]
    return len(short) / len(comments)


def _account_age_days(profile: dict) -> float | None:
    created = profile.get("created_utc")
    if not created:
        return None
    return (time.time() - float(created)) / 86400


def _sample_permalinks(items: List[dict], limit: int) -> List[str]:
    links = [i.get("permalink") for i in items if i.get("permalink")]
    return links[:limit]
