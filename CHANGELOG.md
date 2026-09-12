# Changelog — Serdar Armin Sargut

This file records meaningful project and AI-coordination changes. It is not a substitute for Git history; it is a human-readable handoff layer for Claude, Codex, Copilot and other agents.

## 2026-09-12

### Mobile LCP loading adjustment

- Commit `c428e7830de83f4b85239b160f259ded1b46f42b` updates only `index.html`: LCP hero image decoding is synchronous and GA4/Yandex bootstrap scripts are deferred.
- The hero preload, responsive sources, fetch priority, visible copy, SEO metadata and analytics IDs remain unchanged.
- Live source check confirmed the intended loading attributes; W3C Nu validation returned 0 errors and 0 warnings.
- A short experimental body-end analytics placement was reverted in `ee2bf06217636b985b367d5894f1bbfeb70fb94c` because PageSpeed lab results did not show a repeatable additional gain.
- Mobile PageSpeed Insights lab measurements varied (LCP 2.5 s and 4.6 s); no stable field-data conclusion is claimed.

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

- Linked `/blog/cocuk-model-portfoyu/` to the product-model guide in commit `3585470`; live verification confirmed the link, updated Article dateModified value and HTTP 200 responses for the source, target and blog hub.
