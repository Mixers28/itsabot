# NOW - Working Memory (WM)

> This file captures the current focus / sprint.
> It should always describe what we're doing right now.

<!-- SUMMARY_START -->
**Current Focus (auto-maintained by Agent):**
- Stand up the v0.1 Reddit analysis pipeline: collect, score, and report a single account.
- Implement core storage and rate-limited collection with worker jobs.
- Deliver a minimal UI that shows score, reasons, evidence, history, and a coordination proxy.
<!-- SUMMARY_END -->

---

## Current Objective

Ship a v0.1 end-to-end Reddit account analyzer with explainable scoring and history.

---

## Active Branch

- `main`

---

## What We Are Working On Right Now

- [ ] Scaffold repo layout for `backend/`, `frontend/`, and `infra/` per spec.
- [ ] Implement Reddit collector (posts/comments/profile) with local rate limiter + cache.
- [ ] Define Postgres schema + migrations for accounts, snapshots, items, features, scores.
- [ ] Build feature extraction (timing, repetition, content shape) with coverage flags.
- [ ] Implement rules-based scoring + reasons/evidence generation (automation + coordination proxy).
- [ ] Build API endpoints (`/api/analyze`, `/api/jobs`, `/api/report`, `/api/history`).
- [ ] Minimal UI pages: Search, Report, History.

---

## Next Small Deliverables

- Database schema + migration script for v0.1 tables.
- Working collector with cached responses and rate-limit compliance.
- First end-to-end JSON report for a test account.

---

## Drift Guards (keep NOW fresh)

- Keep NOW to 5–12 active tasks; remove completed items.
- Refresh summary blocks every session.
- Move stable decisions into PROJECT_CONTEXT.

---

## Notes / Scratchpad

- Add an internal OAuth credential health check endpoint/page early to avoid token approval surprises.
