from __future__ import annotations

import statistics
from typing import Dict, List


def compute_content_features(items: List[dict]) -> Dict[str, float | int]:
    comments = [i for i in items if i.get("kind") == "comment"]
    comment_lengths = [len(i.get("body_text") or "") for i in comments]
    avg_comment_length = statistics.mean(comment_lengths) if comment_lengths else 0.0
    median_comment_length = statistics.median(comment_lengths) if comment_lengths else 0.0

    url_items = [i for i in items if i.get("url")]
    url_rate = len(url_items) / len(items) if items else 0.0

    return {
        "avg_comment_length": avg_comment_length,
        "median_comment_length": median_comment_length,
        "url_rate": url_rate,
    }
