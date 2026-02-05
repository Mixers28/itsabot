v0.1 Spec — Bot-Likelihood Analyzer (Reddit first)
0) What you’re building

A web dashboard + backend that takes a Reddit username (and optionally a post/thread URL), fetches recent public activity via the Data API, computes an automation likelihood score (0–100), and returns explanations + evidence.

Key constraints to design around:

Reddit free-eligible Data API limit: 100 queries/min per OAuth client id.

Reddit has introduced an approval requirement for new OAuth tokens under its “Responsible Builder Policy” flow.

1) Goals and non-goals
Goals

Analyze a single account (and later: compare multiple accounts) with:

Score (0–100) for “automation likelihood”

“Top reasons” (explainability)

Evidence panel (links to posts/comments that triggered signals)

Snapshot history (scores over time)

Non-goals (v0.1)

No definitive “bot / not bot” labeling.

No identity inference (“who is behind the account”).

No automation for reporting, mass targeting, harassment, or surveillance.

2) User experience (dashboard)
Pages

Home / Search

Input: reddit_username or reddit_url

Buttons: “Analyze”, “Re-run”, “Compare (later)”

Account Report

Score gauges: Automation likelihood, Coordination likelihood (optional)

Coverage: “Based on last N posts + M comments”

Reasons list (ranked)

Evidence list (clickthrough to permalinks)

History

Past snapshots of the same user (score + coverage deltas)

3) High-level architecture

Frontend

React / Next.js (simple SSR or SPA)

Backend

API: Python FastAPI (or equivalent)

Worker: Celery/RQ for background jobs

Storage: Postgres (snapshots, features, results)

Cache/Queue: Redis (rate-limit coordination, job queue, API response cache)

Why worker jobs?

Keeps UI fast, respects rate limits, and avoids request timeouts.

4) Data access plan (Reddit)
Inputs

Username: u/{name}

Optional: thread/post URL (extract author(s) and context)

Collection (v0.1)

Pull:

Recent items (last N total, default 200, roughly split submissions/comments)

Basic profile metadata (age, karma, etc.)

Rate limiting

Enforce a local limiter to stay under 100 QPM per OAuth client id.

Also read/obey the API rate-limit response headers (X-Ratelimit-Used, Remaining, Reset).

Token/approval handling

Treat OAuth credentials as server secrets (never shipped to clients).

Build an internal “credentials health” page that confirms token validity, since new token approval can be required.

5) Data model (Postgres)
Tables (minimum)

accounts

id (pk)

platform (enum: reddit)

handle (text, unique by platform)

created_at

snapshots

id (pk)

account_id (fk)

collected_at (timestamp)

post_count, comment_count

data_coverage_days (int)

collector_version (text)

items (optional to store raw-ish normalized posts/comments)

id (pk)

snapshot_id (fk)

kind (post|comment)

item_id (platform id)

created_utc

subreddit

permalink

body_text (nullable)

url (nullable)

features

snapshot_id (fk, unique)

json (jsonb) — all computed features

scores

snapshot_id (fk, unique)

automation_score (0–100)

coordination_score (0–100, nullable)

reasons (jsonb: ordered list)

explanations (jsonb: evidence pointers)

6) Feature set (v0.1)

Compute features from last N posts + M comments:

A) Timing / rhythm

posts_per_day, comments_per_day

active_hours_histogram (UTC)

sleep_gap_hours_p95 (proxy for human sleep)

burstiness_index (e.g., coefficient of variation of inter-arrival times)

regularity_score (how “metronomic” the posting is)

B) Repetition / templating

near_duplicate_rate (SimHash/MinHash over text)

top_phrase_reuse (n-gram reuse)

link_domain_concentration (top domain share)

C) Content shape

avg_comment_length, median_comment_length

url_rate (% items with URLs)

subreddit_entropy (very low entropy can indicate single-purpose spam; very high can indicate spray-and-pray)

D) Interaction quality (lightweight)

reply_depth_mean (if available)

unique_threads_replied_to

All features should be computed even if some are missing; store coverage_flags to keep scoring honest.

E) Coordination proxy (single-account, v0.1)

coordination_proxy_score inputs: duplicate rate + domain concentration + low subreddit entropy

7) Scoring (rules-first, explainable)
Output

automation_score 0–100

confidence 0–1 derived from coverage (not the same as score)

Simple v0.1 rubric (example)

Start at 0, add weighted points, cap at 100:

Timing signals

Very high activity (posts+comments/day above threshold): +8 to +25

Cadence regularity (gap CV low): +8 to +15

Very low sleep gap (e.g. no gap > 4h over coverage window): +8 to +15

Repetition

Near-duplicate rate high: +8 to +30

Same link domain dominates: +8 to +15

Subreddit concentration high: +8 to +10

Content shape

Very short, generic comments at scale: +10

URL-heavy posting: +5 to +15

Account-age interaction

New-account high activity: +6 to +10

Interaction quality

Low thread diversity: +8

Reasons format (what the UI shows)

Each reason:

title: “Unusually regular posting cadence”

impact: +18

evidence: list of item permalinks or histogram snippets

details: short explanation in plain language

Confidence (v0.1)

compute_confidence() uses saturating functions of item volume + time span + timestamp completeness, with an explicit penalty for < 30 items.

Scoring defaults (v0.1)

Thresholds/weights implemented in backend/app/scoring/rules_v1.py:

Activity: 8–25 pts

Cadence regularity (gap CV): 8–15 pts

Low max gap (“sleep gap”): 8–15 pts

Duplicate rate: 8–30 pts

Domain concentration: 8–15 pts

Subreddit concentration: 8–10 pts

Short/generic comments: 10 pts

New-account high activity: 6–10 pts

Low thread diversity: 8 pts

8) Backend API design
Endpoints

POST /api/analyze/reddit

body: { "username": "name", "force_refresh": false }

returns: { "job_id": "...", "status": "queued" }

GET /api/jobs/{job_id}

returns status + progress + link to result when done

GET /api/report/reddit/{username}?snapshot=latest

returns final report json: score, reasons, evidence, coverage

GET /api/history/reddit/{username}

returns list of snapshot ids + summary scores

Job flow

Validate username

Check cache:

If snapshot < X hours old and not force_refresh, return cached report

Collect posts/comments under rate limits

Compute features

Score + reasons + evidence pointers

Persist snapshot + results

9) Frontend requirements
Components

Search bar + “Analyze”

Report view:

Score card

Coverage card

Coordination likelihood (proxy)

Reasons accordion

Evidence list with permalinks

History list (timestamp + score)

Minimal visuals

No fancy design needed; clarity and traceability matter more.

10) Operational concerns
Caching strategy

Cache raw API responses in Redis keyed by (username, listing, params) for short TTL

Cache computed report for (username, snapshot_id) for longer TTL

Always store snapshots in Postgres for audit/history

Abuse prevention

Per-IP request throttling to avoid turning it into a mass-scanning service

Require login (optional v0.1) or at least a per-user API key for your own use

11) Repo layout (suggested)
bot-likelihood-dashboard/
  backend/
    app/
      api/
      collectors/
        reddit.py
      features/
        timing.py
        repetition.py
        content.py
      scoring/
        rules_v1.py
      store/
        models.py
        db.py
      workers/
        jobs.py
    tests/
  frontend/
    pages/
    components/
  infra/
    docker-compose.yml
  docs/spec.md
  README.md

12) Sprint plan (tight, shippable)
Sprint 1 — Collector + storage

Reddit collector (posts + comments)

Postgres schema + snapshot persistence

Basic rate limiter aligned with 100 QPM guidance

Sprint 2 — Feature extraction

Timing + repetition + link concentration

Store features JSON

Sprint 3 — Scoring + explainability

Rules-based scoring

Reasons/evidence generation

Sprint 4 — UI + history + polish

Search/report/history pages

Force refresh + cached results

Export report as JSON

Backlog — Observability & Diagnostics

Add logging configuration in main.py (stdout, INFO).

Log job enqueue in routes.py with job.id and username.

Log job status polling in job_status.

Wrap analyze_reddit_user in try/except and log exceptions + timing in jobs.py.

Add optional job.meta["progress"] updates and return them in /api/jobs/{job_id}.

In index.js, surface job_id and log status changes.

13) Roadmap to X then Facebook (design now, implement later)

Keep collectors/ interface consistent: collect(handle) -> normalized_items + metadata.

X: per-endpoint rate limits and windowing; design your queue/limiter to be endpoint-aware.

Facebook: likely constrained to Pages/public sources; plan for stricter eligibility and less granular user-level content.
