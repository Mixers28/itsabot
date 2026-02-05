# Invariants (Non-Negotiables)

- Use only public Reddit data via the official Data API.
- Enforce Reddit API limits (100 QPM per OAuth client id) and honor rate-limit headers.
- OAuth credentials are server-side secrets and never exposed to clients.
- No definitive “bot / not bot” labeling; only likelihood scoring with confidence/coverage.
- No identity inference, doxxing, or attribution of who is behind an account.
- No mass targeting, automated reporting, harassment, or surveillance use.
- Scores must be explainable with evidence links and coverage transparency.
- Coordination likelihood in v0.1 is a single-account proxy only (no cross-account clustering).
- Persist snapshots for auditability and history.

Last reviewed: 2026-02-04
