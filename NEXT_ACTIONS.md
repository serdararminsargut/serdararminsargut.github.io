# Next Actions — Serdar Armin Sargut

**Last updated:** 2026-09-11

This file records unresolved work so Claude, Codex, Copilot and other AI agents can continue without relying on conversational memory.

## Priority 1 — Search Console Sitemap Verification

Current state: unresolved.

Next safe action:

1. Re-check Google Search Console sitemap status when quota/access is available.
2. Do **not** immediately edit or resubmit the sitemap.
3. First verify the current production state:
   - `https://serdararminsargut.pages.dev/sitemap.xml`
   - HTTP status
   - redirect chain
   - final URL
   - `Content-Type`
   - XML validity
   - every `<loc>` URL
   - canonical consistency
   - `robots.txt`
   - relevant `X-Robots-Tag` / cache headers
   - Googlebot accessibility where testable
4. Compare source repository state with Cloudflare production.
5. Only change a file if a reproducible defect is identified.
6. Record test evidence and result in `docs/PRODUCTION_STATUS.md` and `CHANGELOG.md`.

## Priority 2 — Crawler Policy Verification

Verify the effective production crawler policy for:

- Googlebot
- Bingbot
- GPTBot
- ClaudeBot
- PerplexityBot

Do not report exact allow/block status unless the live `robots.txt`, headers and/or HTTP behaviour have actually been verified.

## Priority 3 — Commercial-Intent SEO

After technical stability is confirmed, continue Turkish commercial-intent SEO aimed at direct manufacturer/brand discovery, especially:

- sportswear
- suits / formalwear
- kidswear
- footwear
- catalogue
- e-commerce
- product/commercial photography

Any new keyword or content recommendation must be evaluated for search intent, relevance to Serdar's profile and spam risk before production use.

## Recommendation Gate

When proposing an alternative tool, configuration, SEO tactic, crawler rule or deployment approach:

- Prefer options already tested successfully in this repository.
- Otherwise verify against current authoritative documentation and, where safe, a non-destructive test.
- State clearly whether the option is VERIFIED, SUPPORTED or UNVERIFIED.
- Explain expected benefit, risk and rollback path.
- Do not apply an UNVERIFIED alternative to production merely because it is theoretically possible.

## Completion Rule

When an item is resolved:

- update this file
- update `docs/PRODUCTION_STATUS.md`
- add a short entry to `CHANGELOG.md`
- include commit/date/test evidence
