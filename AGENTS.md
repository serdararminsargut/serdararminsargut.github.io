# AGENTS.md

## Project

**Project:** Serdar Armin Sargut — Child Actor & Commercial Model Portfolio  
**Primary production URL:** https://serdararminsargut.pages.dev/  
**Repository:** serdararminsargut/serdararminsargut.github.io  
**Primary deployment branch:** `main`  
**Deployment target:** Cloudflare Pages  
**Purpose:** Professional casting, commercial modelling, kidswear, sportswear, e-commerce, catalogue and international portfolio visibility.

---

## Core Operating Principle

Treat the current working production site as the source of truth.

Do not make speculative changes.

Before modifying any production-critical file:

1. Identify the exact problem.
2. Verify that the problem exists.
3. Determine whether the issue is in source code, deployment, Cloudflare, search engine indexing, cache, headers or crawler behaviour.
4. Change only the minimum necessary files.
5. Test before and after deployment.
6. Record the result clearly.

**Never change a working component merely because an alternative implementation looks cleaner.**

---

## 1. Production Safety Rules

These rules are mandatory for Claude, Codex, Copilot and any other AI agent working on this repository.

Do not change the following unless a verified defect exists:

- `robots.txt`
- `sitemap.xml`
- canonical URLs
- production routes
- multilingual URLs
- redirects
- structured data
- analytics scripts
- Yandex Metrica
- GA4
- Cloudflare-related configuration
- search-engine verification tags

If a file is currently valid and production is working, preserve it.

---

## 2. Deployment Model

Expected deployment flow:

```text
GitHub main
    ↓
Cloudflare Pages
    ↓
https://serdararminsargut.pages.dev/
```

Do not assume a GitHub commit is live.

After every relevant commit, verify production separately.

Check:

- GitHub commit exists
- commit is on `main`
- Cloudflare Pages deployment completed
- production URL serves the new version
- no stale cache is masking the result

---

## 3. Version Control Rules

Every production change must be traceable.

Before editing:

- inspect current files
- inspect recent commits
- determine whether another agent already changed the same component

Prefer small, focused commits.

Avoid combining unrelated changes.

Recommended commit naming:

```text
fix: correct robots crawler rule
fix: repair sitemap URL
seo: improve Turkish commercial model metadata
schema: update structured data
content: update portfolio copy
analytics: add or repair tracking
perf: optimize asset loading
```

Do not use vague commit names such as:

```text
update
changes
fix stuff
final
new version
```

---

## 4. Existing Production Structure

Preserve the current approved site structure unless explicitly instructed otherwise.

Primary sections include:

- Hero / Cover
- About
- Physical Characteristics
- Film & TV Experience
- Showreel & Videos
- Advertising & Brand Work
- Sports Skills
- Portfolio Features
- Collaboration Opportunities
- Contact

Additional assets may include:

- Comp Card
- Casting Card
- Showreel
- Blog
- multilingual pages
- structured data
- downloadable PDF assets

---

## 5. Identity Data

Use the following approved identity information unless the repository contains a newer explicitly approved value.

**Name:** Serdar Armin Sargut  
**Birth year:** 2014  
**Do not use:** “12 years old” as a permanent identity field  
**Height:** 162 cm  
**Weight:** 46 kg  
**Shoe:** EU 37  
**Clothing:** 12–14 years  
**Eyes:** Green  
**Hair:** Blonde, wavy  
**Skin:** Fair  
**Location:** Istanbul, Türkiye

Skills:

- swimming
- basketball
- football

Do not invent missing physical measurements.

Do not infer chest, waist, hips, inseam, collar or precise clothing measurements unless an approved value exists in the repository or current user instructions.

---

## 6. Positioning

The site is not primarily intended to attract casting agencies.

The strategic SEO objective is broader commercial discovery, including:

- apparel manufacturers
- kidswear brands
- sportswear manufacturers
- suit manufacturers
- footwear companies
- e-commerce brands
- catalogue producers
- product photographers
- advertising producers
- casting teams
- production companies

Important commercial intent themes include:

- boy commercial model
- child commercial model
- kidswear model
- sportswear model
- suit model
- catalogue model
- e-commerce model
- product photography model
- blonde boy model
- green-eyed boy model
- European-looking child model
- Istanbul child model

Do not keyword-stuff. Keywords must be incorporated naturally into meaningful content.

---

## 7. SEO Rules

Preserve and validate:

- one primary H1
- logical H2/H3 hierarchy
- unique page title
- unique meta description
- canonical
- crawlable links
- descriptive image alt text
- descriptive filenames
- sitemap integrity
- robots integrity
- structured data validity
- mobile usability
- HTTP 200 production pages

Avoid:

- hidden keyword blocks
- doorway pages
- duplicated pages created only for keywords
- spammy city/location pages
- fake reviews
- fake credits
- fake press references

---

## 8. Sitemap Rules

`sitemap.xml` is production-critical.

Before modifying it, verify:

- valid XML
- correct `Content-Type`
- HTTP 200
- every `<loc>` resolves
- no invalid redirect chains
- no broken URL
- canonical URL consistency

Do not rebuild the sitemap simply because Google Search Console reports `Couldn't fetch`, `Getirilemedi` or `Unknown`.

Search Console errors may be delayed, cached or external to the XML itself.

First distinguish between:

- source problem
- deployment problem
- Cloudflare problem
- HTTP header problem
- Google crawler problem
- Search Console stale state

Do not repeatedly resubmit or modify the sitemap without evidence.

---

## 9. robots.txt Rules

`robots.txt` is production-critical.

Never introduce accidental blocking for:

- Googlebot
- Bingbot
- GPTBot
- ClaudeBot
- PerplexityBot

unless explicitly instructed.

Verify crawler policy before editing.

Expected SEO/GEO direction:

- search crawlers: allowed
- useful AI search crawlers: generally allowed
- training-only crawlers may be treated separately if explicitly requested

Do not assume Cloudflare bot protection is responsible for a crawler problem without HTTP evidence.

---

## 10. GEO / AEO Rules

The site should remain accessible to legitimate search and answer engines.

GEO/AEO work may include:

- clear entity description
- Person structured data
- WebPage structured data
- VideoObject where applicable
- FAQ where genuinely useful
- unambiguous professional biography
- clear location
- commercial intent
- structured portfolio information
- consistent entity naming
- authoritative internal linking

Do not create fabricated FAQs solely for SEO.

Do not claim partnerships, clients or work credits that are not verified.

---

## 11. Structured Data

Existing valid schema must be preserved.

Possible schema types include:

- Person
- WebSite
- WebPage
- VideoObject
- BreadcrumbList
- FAQPage

Do not add schema unsupported by visible page content.

Do not add Review, AggregateRating, Organization claims, fake awards or fake job credits without verified supporting content.

After schema changes, validate syntax.

---

## 12. Multilingual Rules

Priority languages include:

- TR
- EN
- AR
- RU

Other languages may exist.

Each language should have, where practical:

- natural translation
- unique title
- unique meta description
- appropriate headings
- consistent entity data
- correct canonical behaviour
- correct language linking

Avoid machine-translated keyword stuffing.

Do not mix multiple languages in the same SEO title unless explicitly required.

---

## 13. Analytics

Existing analytics implementations must be preserved unless broken.

Known analytics systems may include:

- Google Analytics 4
- Yandex Metrica

Before removing or replacing analytics:

1. confirm the existing ID
2. confirm whether it is firing
3. verify duplicate tags
4. verify consent/privacy implications
5. preserve existing event tracking where possible

Existing tracked interactions may include:

- Instagram clicks
- email/contact clicks
- showreel plays

---

## 14. Social Links

Important project destination:

**Instagram:** https://www.instagram.com/serdararminsargutt/

Do not silently replace the current active account with an old or hacked account.

Validate outbound links after changes.

---

## 15. Video

Known Vimeo content may include:

- 1218441688
- 1218544534
- 1220869927

Do not remove working video assets unless explicitly requested.

For embedded video:

- maintain responsive layout
- avoid excessive page-weight impact
- use lazy loading where appropriate
- preserve VideoObject schema where valid

---

## 16. Performance

Performance improvements must not damage visual quality or SEO.

Prefer:

- correctly sized images
- modern formats
- lazy loading below the fold
- minimal JavaScript
- reduced unused CSS
- deferred non-critical scripts
- stable layout dimensions

Avoid:

- aggressive image compression that harms portfolio quality
- breaking hero images
- removing important metadata
- client-side rendering for critical text when static HTML is available

---

## 17. Cloudflare Safety

Do not change Cloudflare-related behaviour based only on assumption.

Potential areas requiring careful verification:

- redirects
- Transform Rules
- WAF
- Bot Fight Mode
- AI crawler controls
- cache
- headers
- HSTS
- CSP
- X-Robots-Tag
- security rules

Before recommending a Cloudflare change, distinguish between:

- Cloudflare Pages hostname behaviour
- custom-domain zone behaviour
- browser behaviour
- crawler behaviour
- Cloudflare dashboard settings

Do not assume `pages.dev` behaves exactly like a custom Cloudflare-managed domain.

---

## 18. Search Engine Verification

Relevant platforms may include:

- Google Search Console
- Bing Webmaster Tools
- Yandex Webmaster

Do not remove existing verification tags unless the replacement method has already been verified.

Search-console state must not be treated as instant truth. Indexing systems may lag behind production.

---

## 19. Testing Requirements

For production-critical changes, test at least:

- `/`
- `robots.txt`
- `sitemap.xml`
- important language pages
- casting card / comp card
- important external links
- canonical
- metadata
- schema

Where applicable, check:

- HTTP status
- redirect chain
- Content-Type
- final URL
- canonical
- robots directives
- X-Robots-Tag
- cache behaviour

---

## 20. Definition of Done

A change is not complete merely because the source code was edited.

A production change is complete only when:

1. source change is correct
2. commit exists
3. commit is on the correct branch
4. deployment succeeds
5. live production is tested
6. relevant URLs return expected HTTP results
7. no regression is detected
8. short result report is produced

---

## 21. Required Change Report

After meaningful production work, report:

```text
Version / commit:
Date:
Files changed:
Reason:
Before:
After:
Deployment:
Live test:
HTTP status:
SEO impact:
Known risks:
Remaining action:
```

Do not claim deployment success without live verification.

---

## 22. Agent Coordination

Claude, Codex, Copilot and other agents must inspect repository state before editing.

Do not assume another agent's conversational memory is available.

Repository files and Git history are the shared source of truth.

Before beginning work:

1. read this `AGENTS.md`
2. read `docs/PRODUCTION_STATUS.md`
3. read `NEXT_ACTIONS.md`
4. inspect recent commits
5. inspect relevant files
6. verify production where needed

After meaningful work, update the appropriate continuity files so the next AI agent can continue from the same state.

If another agent has already implemented a valid solution, preserve it.

Avoid reverting other agents' work unless the regression is verified.

---

## 23. Conflict Resolution

When project instructions conflict, use this priority order:

1. Explicit latest user instruction
2. Production safety
3. Verified live behaviour
4. `AGENTS.md`
5. Repository implementation
6. Older documentation
7. Assumptions

Never prefer assumption over live evidence.

---

## 24. Forbidden Actions

Do not:

- delete working production files without justification
- rewrite the entire site for a minor SEO issue
- change URL structure casually
- mass-rename pages
- remove analytics without verification
- remove verification tags blindly
- block search engines accidentally
- generate fake portfolio credits
- create fake testimonials
- fabricate brand collaborations
- publish personal phone numbers
- expose private information
- introduce keyword stuffing
- use black-hat SEO
- add unnecessary redirects
- change sitemap repeatedly without evidence
- deploy untested changes

---

## 25. Preferred Working Method

Use this workflow:

```text
OBSERVE
↓
VERIFY
↓
DIAGNOSE
↓
MINIMAL CHANGE
↓
LOCAL / SOURCE CHECK
↓
COMMIT
↓
DEPLOY
↓
LIVE TEST
↓
REPORT
```

If verification shows no defect:

```text
DO NOT CHANGE PRODUCTION
```

---

## 26. Current Strategic Priority

Current priority order:

1. Production stability
2. Google crawl/index reliability
3. Sitemap and robots integrity
4. Commercial-intent SEO
5. GEO / AEO discoverability
6. International visibility
7. Portfolio conversion
8. Social traffic growth

Technical stability takes priority over experimental optimization.

---

## 27. Final Rule

**Evidence before edits.**

If production is working and there is no verified defect, preserve the current implementation.

All AI agents working on this repository must treat stability, reversibility, traceability and live verification as mandatory.

---

## 28. Verified Recommendations and Alternatives

Recommendations, alternatives and proposed fixes must be evidence-based.

Classify important technical findings and alternatives using one of these states:

- **VERIFIED** — directly tested or confirmed from authoritative/current evidence.
- **SUPPORTED** — strongly supported by evidence but not fully reproduced in the current environment.
- **UNVERIFIED** — plausible but not yet tested or confirmed.
- **REJECTED** — tested and found false, ineffective, unsafe or unsuitable for this project.

When recommending an alternative tool, configuration, SEO tactic, crawler rule, deployment method or technical fix:

1. Prefer solutions already tested successfully in this repository.
2. Otherwise verify current authoritative documentation before recommending implementation.
3. Where safe, perform a non-destructive test before production use.
4. State the evidence level clearly.
5. Explain expected benefit, risk and rollback path.
6. Never present an `UNVERIFIED` theory as a confirmed root cause.
7. Never apply an `UNVERIFIED` production change merely because it is theoretically possible.
8. If evidence is incomplete, say so explicitly instead of guessing.

For Search Console, sitemap, robots, crawler and Cloudflare issues in particular, separate hypotheses from verified causes.

---

## 29. Shared Project State and Handoff

All AI agents must use repository files—not assumed conversational memory—to understand where the project stopped.

The shared continuity files are:

- `docs/PRODUCTION_STATUS.md` — latest known production/project state and evidence labels
- `NEXT_ACTIONS.md` — unresolved tasks and next safe actions
- `CHANGELOG.md` — human-readable record of meaningful changes
- Git history — immutable implementation evidence

Before starting a technical task, read these files together with `AGENTS.md`.

After meaningful work:

- update `docs/PRODUCTION_STATUS.md` when the known state changes
- update `NEXT_ACTIONS.md` when a task is completed, blocked or replaced
- update `CHANGELOG.md` for meaningful project/process changes
- include commit/date/test evidence where applicable

This handoff process exists so Claude, Codex, Copilot and other AI agents can continue from the same verified project state without repeating old tests, reintroducing rejected ideas or treating previous hypotheses as facts.
