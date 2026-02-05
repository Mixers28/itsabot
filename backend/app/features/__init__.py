from __future__ import annotations

from typing import Dict, List

from app.features.content import compute_content_features
from app.features.interaction import compute_interaction_features
from app.features.repetition import compute_repetition_features
from app.features.timing import compute_timing_features


def compute_features(items: List[dict]) -> Dict[str, dict]:
    timing = compute_timing_features(items)
    repetition = compute_repetition_features(items)
    content = compute_content_features(items)
    interaction = compute_interaction_features(items)

    coverage_flags = {
        "has_items": bool(items),
        "has_timestamps": timing.get("timestamp_completeness", 0) > 0,
        "has_comments": any(i.get("kind") == "comment" for i in items),
        "has_posts": any(i.get("kind") == "post" for i in items),
    }

    return {
        "timing": timing,
        "repetition": repetition,
        "content": content,
        "interaction": interaction,
        "coverage_flags": coverage_flags,
    }
