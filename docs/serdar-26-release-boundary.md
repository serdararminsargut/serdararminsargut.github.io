# Serdar 26-language Comp Card — release boundary

## Baseline
- Portfolio: Serdar Armin Sargut only
- Production baseline: `main` @ `810c24cef3646f339cdcbb4248fff5f200903138`
- Test candidate branch: `test/serdar-26-comp-card-candidate-20261024`
- Test candidate base: the production baseline above

## Verified candidate scope
The candidate branch adds only isolated generators, validators and a Cloudflare Pages **noindex** preview workflow.
It does **not** alter any production source route, production PDF, sitemap, robots rule, redirect, Cloudflare production configuration, or Duru file.

Latest candidate gate (2026-10-25):
- 26/26 static locale/privacy checks
- 52/52 mobile matrix checks at 390 px and 430 px
- 26/26 generated A4 PDF checks
- noindex preview HTML and locale-PDF route checks

## Promotion guard
This branch must not be merged as a shortcut to a production release: it contains test tooling, not the 26 production Comp Card source pages.

A separate, reviewable production release package must:
1. Preserve the approved four-language Comp Card structure, including navigation, photo grid, optional-measure policy, PDF download behaviour and parent-managed contact.
2. Add the other 22 HTML sources and produce 26 locale-matched PDFs under `/downloads/`.
3. Update the language selector, hreflang reciprocity, x-default, sitemap routes, attachment headers and clean-route redirects together.
4. Pass preview and live acceptance before any production completion claim.

## Protected boundaries
- No Duru asset, route, copy, email, sitemap entry or Cloudflare project may be included.
- No phone, school, home address or unapproved personal data may be added.
- A translation is editorial presentation only; it is not a claim that Serdar speaks that language.
