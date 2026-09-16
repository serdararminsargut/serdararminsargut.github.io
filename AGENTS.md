# AGENTS.md

## Project

**Project:** Serdar Armin Sargut — Child Actor & Commercial Model Portfolio  
**Primary production URL:** https://serdararminsargut.pages.dev/  
**Repository:** serdararminsargut/serdararminsargut.github.io  
**Primary deployment branch:** `main`  
**Deployment target:** Cloudflare Pages

## Mandatory URL Verification and Search-Engine Submission Gate

This rule is mandatory for every AI agent, including ChatGPT, Codex, Claude and Copilot.

### NEVER GUESS A URL

A route must never be inferred from naming conventions, another language route, a sitemap assumption, conversational memory or an SEO plan.

Before a URL is treated as real, verify the exact source path on GitHub `main`.

Example of a rejected assumption from 16 September 2026:

`/tr/erkek-cocuk-modeli/`

This route was tested in Google Search Console before its repository path was verified. Google Live URL Test returned 404. This must not be repeated.

### Mandatory verification chain

For every existing or proposed page, follow this order without skipping steps:

```text
GitHub main exact source path
↓
Build/deployment inclusion
↓
Exact production URL
↓
Live HTTP status
↓
Canonical
↓
Hreflang (when applicable)
↓
Sitemap membership (when applicable)
↓
Google Search Console Live URL Test
↓
Request indexing only when justified and the live test succeeds
```

### GitHub file does NOT mean production is live

A file existing on `main` proves only that the source file exists. It does not prove that Cloudflare Pages deployed it or that the expected production route returns HTTP 200.

Use only these page states:

- **TESTED AND LIVE** — source path verified, deployment verified, production HTTP 200, canonical correct, applicable hreflang/SEO checks passed.
- **READY BUT NOT PUBLISHED / NOT VERIFIED** — source exists but production verification is incomplete.
- **NO FILE** — no matching source exists on GitHub `main`; do not behave as if the URL exists and do not submit it to search engines.

### 404 stop rule

If a URL returns 404:

- do not request indexing;
- do not repeatedly run GSC indexing attempts;
- do not submit it to IndexNow;
- do not add it to the sitemap;
- first verify whether an exact corresponding source file exists on GitHub `main` and whether deployment includes it.

A 404 is a stop condition until the source/deployment mismatch is understood.

### Google Search Console rule

For manual indexing:

1. Verify repository source path.
2. Verify production HTTP 200 and technical SEO prerequisites.
3. Run **Test Live URL**.
4. Use **Request Indexing** only when the live test succeeds and a request is actually justified.

Do not waste GSC quota by repeatedly submitting failed, unknown or already-indexed unchanged URLs.

### Sitemap rule

Do not repeatedly resubmit or modify `sitemap.xml` merely because Search Console reports a delayed or failed state.

Before changing the sitemap, verify:

- sitemap HTTP status;
- valid XML;
- every included URL is a real production route;
- included URLs return the expected HTTP status;
- canonical consistency;
- deployment state.

Never include a known 404 URL.

### Multilingual route rule

Never infer `/en/`, `/ar/`, `/ru/`, `/az/`, `/kk/`, `/uz/`, `/ky/`, `/fa/`, `/tk/`, `/tr/` or any other language route from another language's structure. Verify each repository path and live route independently.

Hreflang targets must resolve to verified live URLs.

### Production safety workflow

```text
OBSERVE
↓
VERIFY SOURCE
↓
PLAN
↓
USER APPROVAL
↓
PRE-PRODUCTION TEST
↓
COMMIT
↓
DEPLOY
↓
LIVE HTTP + SEO TEST
↓
SEARCH-ENGINE ACTION (ONLY IF JUSTIFIED)
↓
EVIDENCE REPORT
```

No production experiment is allowed merely to test a hypothesis when a non-destructive/source-level check can answer it first.

### Evidence record

For critical URL work, record where applicable:

```text
Date:
GitHub path:
Branch:
Commit:
Deployment:
Production URL:
HTTP status:
Canonical:
Hreflang:
Sitemap:
GSC Live Test:
Result:
Open risk / external wait:
```

Never state `fixed`, `live`, `successful`, `Google can see it`, or equivalent without supporting evidence.

## Core Operating Principle

Evidence before edits. Source before route. Live verification before search-engine submission.

Do not make speculative changes. Preserve working production components unless a verified defect exists.

For every production-critical task:

1. Identify and verify the exact problem.
2. Distinguish source, deployment, Cloudflare, HTTP, search-engine, cache and crawler causes.
3. Change only the minimum necessary files after explicit user approval.
4. Test before production.
5. Verify production after deployment.
6. Report evidence and unresolved external processes separately.

## Production-critical components

Do not change these without a verified defect and explicit approval:

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

## Deployment model

```text
GitHub main
↓
Cloudflare Pages
↓
https://serdararminsargut.pages.dev/
```

Never assume a GitHub commit is live. Verify the relevant commit/deployment and the actual production URL separately.

## SEO / GEO / AEO safety

Preserve and validate, where applicable:

- one primary H1;
- logical headings;
- unique title and meta description;
- canonical;
- crawlable internal links;
- descriptive image alt text;
- sitemap and robots integrity;
- structured data validity;
- mobile usability;
- HTTP 200 for intended indexable pages.

Do not create doorway pages, hidden keyword blocks, fake credits, fake reviews, fake partnerships, spammy location pages or keyword stuffing.

Schema must be supported by visible, verified content.

## Identity and privacy

Use only project-approved identity/profile information. Do not invent measurements, credits, agencies, partnerships or contact information. Variable measurements must be reconfirmed immediately before new publication where project rules require it.

Do not publish personal phone numbers, home/school addresses, precise daily location or other unnecessary sensitive information about a child.

## Agent coordination and continuity

Before technical work, inspect current repository state and relevant continuity files, including when present:

- `AGENTS.md`
- `docs/PRODUCTION_STATUS.md`
- `NEXT_ACTIONS.md`
- `CHANGELOG.md`
- recent Git history

Do not assume conversational memory is authoritative when repository/live evidence can be checked.

After meaningful work, update the appropriate continuity/evidence record so another agent does not repeat failed tests or revive rejected assumptions.

## Conflict priority

When instructions conflict, use this order:

1. latest explicit user instruction;
2. child safety/privacy and production safety;
3. verified live evidence;
4. approved project source/instructions;
5. `AGENTS.md`;
6. repository implementation;
7. older documentation;
8. assumptions.

Never prefer an assumption over verified source/live evidence.

## Definition of Done

A production change is complete only when the approved source change exists, the correct branch/commit is known, deployment succeeds, live production is tested, relevant URLs return expected results, critical SEO/link/mobile checks pass, and a short evidence report is produced.

If verification shows no defect, do not change production.
