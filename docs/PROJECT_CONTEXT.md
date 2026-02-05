# Project Context – Long-Term Memory (LTM)

> High-level design, tech decisions, constraints for this project.  
> This is the **source of truth** for agents and humans.

<!-- SUMMARY_START -->
**Summary (auto-maintained by Agent):**
- Building the Bot-Likelihood Analyzer: a web dashboard + backend that scores Reddit account automation likelihood with explainable evidence.
- v0.1 scope: single-account analysis, rules-first scoring, evidence links, snapshot history, and a coordination proxy score.
- Stack: Next.js frontend, FastAPI API, worker jobs (RQ), Postgres, Redis.
- Constraints: Reddit Data API limit 100 QPM/client, OAuth approval under Responsible Builder Policy, tokens stay server-side.
- Safety: no definitive bot labels, no identity inference, and no mass targeting/harassment.
 - Repo scaffolded with backend, frontend, and infra; basic API/worker/UI implemented for v0.1.
<!-- SUMMARY_END -->

---

## 1. Project Overview

- **Name:** bot-likelihood-analyzer
- **Owner:** TBD
- **Purpose:** Analyze public Reddit activity and return an automation-likelihood score with explainable reasons and evidence.
- **Primary Stack:** React/Next.js, FastAPI, Celery/RQ, Postgres, Redis.
- **Target Platforms:** Web dashboard + backend API/worker.
- **Primary Data Source:** Reddit Data API (public posts/comments).

---

## 2. Core Design Pillars

- Explainable, rules-first scoring with evidence links and coverage transparency.
- Respect platform limits/policies with rate limiting, caching, and token health checks.
- Persist snapshots for auditability and historical comparisons.
- Guard against abuse with throttling and access control.

---

## 3. Technical Decisions & Constraints

- Enforce Reddit Data API limit of 100 QPM per OAuth client id.
- Read and honor rate-limit headers (`X-Ratelimit-Used`, `X-Ratelimit-Remaining`, `X-Ratelimit-Reset`).
- OAuth credentials remain server-side only; never shipped to clients.
- Use worker jobs for collection/feature/scoring to keep UI responsive and avoid timeouts.
- Store snapshots, features, scores, and reasons in Postgres; cache API responses in Redis.
- v0.1 defaults: collect last ~200 items total (roughly split submissions/comments), confidence from item volume + span + timestamp completeness with penalty for < 30 items.
- Include a single-account coordination proxy score (duplicate rate + domain concentration + low subreddit entropy).
- Prohibit definitive “bot/not bot” labeling and identity inference.
- No automation for reporting, harassment, or surveillance.

---

## 4. Memory Hygiene (Drift Guards)

- Keep this summary block current and <= 300 tokens.
- Move stable decisions into the Change Log so they persist across sessions.
- Keep NOW to 5–12 active tasks; archive or remove completed items.
- Roll up SESSION_NOTES into summaries weekly (or every few sessions).

---

## 5. Architecture Snapshot

- **Frontend:** Next.js dashboard for search, report, evidence, and history views.
- **API:** FastAPI endpoints for analyze, job status, report, and history.
- **Worker:** Celery/RQ jobs for collection, feature extraction, and scoring.
- **Storage:** Postgres for snapshots/features/scores; Redis for cache/queue/rate limiting.

---

## 6. Links & Related Docs

- Spec: `docs/spec.md`
- Invariants: `docs/INVARIANTS.md`
- Working memory: `docs/NOW.md`
- Session log: `docs/SESSION_NOTES.md`

---

## 7. Change Log (High-Level Decisions)

Use this section for **big decisions** only:

- `2026-02-04` – Reframed the project as the Bot-Likelihood Analyzer for Reddit with rules-first scoring and evidence-based reporting.
- `2026-02-04` – Locked initial stack to Next.js + FastAPI + worker jobs + Postgres + Redis and codified Reddit API constraints.
- `2026-02-05` – Implemented v0.1 scaffold (backend API/worker, frontend UI, infra compose) and deployed readiness tasks.
