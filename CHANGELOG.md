# Changelog — Serdar Armin Sargut

This file records meaningful project and AI-coordination changes. It is not a substitute for Git history; it is a human-readable handoff layer for Claude, Codex, Copilot and other agents.

## 2026-09-11

### Added shared AI operating policy

- Added root `AGENTS.md` as the primary cross-agent policy.
- Added `CLAUDE.md` pointing Claude to `AGENTS.md`.
- Added `.github/copilot-instructions.md` pointing GitHub Copilot to `AGENTS.md`.

### Added cross-agent project continuity

- Added `docs/PRODUCTION_STATUS.md` for the latest known production/project state.
- Added `NEXT_ACTIONS.md` for unresolved work and the next safe steps.
- Added this `CHANGELOG.md` as a readable history layer.

### Added evidence discipline

- Search Console sitemap root cause remains unproven unless reproduced with evidence.
- Test deployments/publications must not be described as the cause of an indexing or sitemap issue unless verified.
- Alternatives and recommendations should be classified as VERIFIED, SUPPORTED, UNVERIFIED or REJECTED.
- UNVERIFIED alternatives must not be applied to production solely on theory.

### Production impact

These documentation/agent-instruction changes do not intentionally modify site content, `robots.txt`, `sitemap.xml`, analytics, canonical URLs or SEO markup.


### Verified commercial SEO content deployment

- Added manufacturer/brand-intent content to `/blog/erkek-cocuk-urun-modeli/` in commit `c581ca5`.
- Added the same guide to the Turkish blog hub and its structured `ItemList` in commit `a14b9ff`.
- Production verification: on 11 September 2026, the live blog hub returned HTTP 200 and exposed the new internal link; the guide and homepage also returned HTTP 200.
- No URL, canonical, sitemap, robots, analytics or structured-data route was changed.
