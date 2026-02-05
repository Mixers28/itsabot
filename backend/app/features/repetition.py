from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List
from urllib.parse import urlparse


_WORD_RE = re.compile(r"[a-z0-9]+")


def _normalize_text(text: str) -> str:
    tokens = _WORD_RE.findall(text.lower())
    return " ".join(tokens)


def _ngrams(tokens: List[str], n: int) -> List[str]:
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _entropy(values: List[int]) -> float:
    total = sum(values)
    if total == 0:
        return 0.0
    entropy = 0.0
    for v in values:
        p = v / total
        if p > 0:
            entropy -= p * math.log(p)
    return entropy


def compute_repetition_features(items: List[dict]) -> Dict[str, float | str | dict]:
    texts = [i.get("body_text") for i in items if i.get("body_text")]
    normalized = [_normalize_text(t) for t in texts if t]
    total_texts = len(normalized)
    unique_texts = len(set(normalized))
    near_duplicate_rate = 0.0
    if total_texts:
        near_duplicate_rate = max(0.0, 1 - (unique_texts / total_texts))

    phrase_counts: Counter[str] = Counter()
    for text in normalized:
        tokens = text.split()
        phrase_counts.update(_ngrams(tokens, 3))
    top_phrase_reuse = 0.0
    if phrase_counts:
        top_phrase, top_count = phrase_counts.most_common(1)[0]
        top_phrase_reuse = top_count / max(len(normalized), 1)

    domains: List[str] = []
    for item in items:
        url = item.get("url")
        if not url:
            continue
        parsed = urlparse(url)
        if parsed.netloc:
            domains.append(parsed.netloc.lower())
    domain_counts = Counter(domains)
    link_domain_concentration = 0.0
    top_domain = None
    if domain_counts:
        top_domain, top_count = domain_counts.most_common(1)[0]
        link_domain_concentration = top_count / max(sum(domain_counts.values()), 1)

    subreddit_counts = Counter([i.get("subreddit") for i in items if i.get("subreddit")])
    entropy = _entropy(list(subreddit_counts.values()))
    max_entropy = math.log(len(subreddit_counts)) if subreddit_counts else 1.0
    subreddit_entropy = entropy / max_entropy if max_entropy else 0.0

    return {
        "near_duplicate_rate": near_duplicate_rate,
        "top_phrase_reuse": top_phrase_reuse,
        "link_domain_concentration": link_domain_concentration,
        "top_domain": top_domain,
        "subreddit_entropy": subreddit_entropy,
    }
