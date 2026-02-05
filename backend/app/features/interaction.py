from __future__ import annotations

from typing import Dict, List


def compute_interaction_features(items: List[dict]) -> Dict[str, float | int]:
    comments = [i for i in items if i.get("kind") == "comment"]
    thread_ids = [i.get("link_id") for i in comments if i.get("link_id")]
    unique_threads = len(set(thread_ids))
    reply_depth_mean = 0.0
    if comments:
        reply_depth_mean = 0.0
    return {
        "unique_threads_replied_to": unique_threads,
        "reply_depth_mean": reply_depth_mean,
    }
