# Production Status — Serdar Armin Sargut

**Purpose:** Shared current-state record for Claude, Codex, Copilot and other AI agents.

**Last updated:** 2026-09-12

## Production

- Primary production URL: https://serdararminsargut.pages.dev/
- Repository: `serdararminsargut/serdararminsargut.github.io`
- Production branch: `main`
- Deployment target: Cloudflare Pages

## Shared AI Coordination

The repository now uses:

- `AGENTS.md` — primary shared operating policy
- `CLAUDE.md` — Claude entry instructions referencing `AGENTS.md`
- `.github/copilot-instructions.md` — Copilot entry instructions referencing `AGENTS.md`
- `docs/PRODUCTION_STATUS.md` — latest known production/project state
- `NEXT_ACTIONS.md` — unresolved work and next steps
- `CHANGELOG.md` — documented project/process changes

Repository files and Git history are the shared source of truth between AI agents. Do not assume cross-agent conversational memory.

## Current Known Technical State

### Sitemap / Search Console

Last observed project state:

- `sitemap.xml` and `robots.txt` have previously been tested as reachable/valid in project checks.
- Google Search Console has shown a sitemap state such as `Couldn't fetch / Getirilemedi / Unknown` with zero discovered pages in prior checks.
- The exact root cause of the Search Console sitemap state has **not been proven**.
- A prior test deployment or test publication has been discussed as a possible cause, but this is **not a verified root cause** and must not be presented as fact.
- Do not modify `sitemap.xml` merely because Search Console shows a stale/error state.
- Before any sitemap change, verify source, deployment, HTTP status, Content-Type, XML validity, `<loc>` URLs, redirects, crawler access and relevant headers.

### Production Safety

- Do not change working production files without evidence of a defect.
- Do not infer that a GitHub commit is live until production is verified.
- Preserve existing SEO metadata, canonical URLs, structured data, analytics and multilingual routes unless a verified issue requires a change.

## Performance Verification

- On 12 September 2026, mobile PageSpeed Insights laboratory measurements were rerun after production performance adjustments.
- Commit `c428e7830de83f4b85239b160f259ded1b46f42b` changed only `index.html`: the LCP hero image now uses `decoding="sync"`; existing GA4 and Yandex scripts use `defer` so parsing is not blocked.
- Live source verification and W3C Nu validation completed: 0 errors, 0 warnings (71 informational void-element notices).
- PageSpeed Insight test runs were materially variable: one run reported LCP 2.5 s / performance 96; a second run reported LCP 4.6 s / performance 83. Treat the 2.5 s result as an observed laboratory run, not a guaranteed or stable field result.
- The experimental body-end analytics placement was reverted in commit `ee2bf06217636b985b367d5894f1bbfeb70fb94c` because it did not demonstrate an additional repeatable benefit. The current production implementation remains the verified low-risk deferred-head version.

## Current Strategic Direction

Primary commercial SEO objective is not limited to agencies. The site should also be discoverable by manufacturers, brands and production teams searching for child models for:

- kidswear
- sportswear
- suits / formalwear
- footwear
- catalogue photography
- e-commerce photography
- commercial/product shoots

Avoid keyword stuffing and speculative SEO changes.

## Verification Labels

All future findings and recommendations should be labelled internally using one of these evidence states:

- **VERIFIED** — directly tested or confirmed from authoritative/current evidence.
- **SUPPORTED** — strongly supported by evidence but not fully reproduced in the current environment.
- **UNVERIFIED** — plausible but not yet tested or confirmed.
- **REJECTED** — tested and found false, ineffective, unsafe or unsuitable for this project.

Never present `UNVERIFIED` information as a confirmed cause or recommended production change.

## Handoff Rule

Before starting any new technical task, every AI agent should read:

1. `AGENTS.md`
2. `docs/PRODUCTION_STATUS.md`
3. `NEXT_ACTIONS.md`
4. recent Git commits

After meaningful work, update the relevant status/history file so the next agent can continue from the same point.
