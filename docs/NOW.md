# NOW - Working Memory (WM)

> This file captures the current focus / sprint.
> It should always describe what we're doing right now.

<!-- SUMMARY_START -->
**Current Focus (auto-maintained by Agent):**
- Deploy the updated observability build (API + worker + frontend) and validate end-to-end.
- Verify Railway service settings for API/worker and frontend deployment path.
- Use new job logs/progress to debug stuck “queued” requests.
<!-- SUMMARY_END -->

---

## Current Objective

Deploy and validate the v0.1 end-to-end Reddit account analyzer with logging and job progress.

---

## Active Branch

- `main`

---

## What We Are Working On Right Now

- [x] Scaffold repo layout for `backend/`, `frontend/`, and `infra/` per spec.
- [x] Implement Reddit collector (posts/comments/profile) with local rate limiter + cache.
- [x] Define Postgres schema for accounts, snapshots, items, features, scores.
- [x] Build feature extraction (timing, repetition, content shape) with coverage flags.
- [x] Implement rules-based scoring + reasons/evidence generation (automation + coordination proxy).
- [x] Build API endpoints (`/api/analyze`, `/api/jobs`, `/api/report`, `/api/history`).
- [x] Minimal UI pages: Search, Report, History.
- [ ] Configure Railway services for API, worker, and frontend with env vars.
- [ ] Deploy updated logging/progress changes to Railway.
- [ ] Validate API startup, worker processing, and frontend data flow in deployment.
- [ ] Confirm job status transitions (queued → started → finished) and report rendering.

---

## Next Small Deliverables

- Railway deployment green for API + worker + frontend.
- First end-to-end JSON report in prod/staging with cached results.
- Credentials health endpoint returns OK.

---

## Drift Guards (keep NOW fresh)

- Keep NOW to 5–12 active tasks; remove completed items.
- Refresh summary blocks every session.
- Move stable decisions into PROJECT_CONTEXT.

---

## Notes / Scratchpad

- Add an internal OAuth credential health check endpoint/page early to avoid token approval surprises.
