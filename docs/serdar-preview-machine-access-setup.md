# Serdar Armin Sargut — read-only machine Preview access

Project-specific, **test-branch-only** GitHub Actions workflow. No production, DNS, deploy, Cloudflare settings, or existing Access policies are modified. No pull-request secret exposure.

## Required Cloudflare setup (manual, once)

1. Create a new Cloudflare Access **Service Token** named `serdar-preview-qa`; do not post the Client Secret in a chat or a GitHub issue.
2. In the Access application protecting only `*.serdararminsargut.pages.dev`, add a **Service Auth** policy with **Include → Service Token → serdar-preview-qa**. Do not remove the existing user Allow policy. If the Access application does not exist yet, stop and assess its scope before creating it.
3. GitHub repository Settings → Secrets and variables → Actions:
   - Secrets `SERDAR_CF_ACCESS_CLIENT_ID`, `SERDAR_CF_ACCESS_CLIENT_SECRET` (Client ID and Client Secret separately).
   - Variable `SERDAR_PREVIEW_URL` = an existing **Cloudflare-protected, project-specific Preview URL**, e.g., https://<deployment-id>.serdararminsargut.pages.dev/. Never the `.com` production site or the base pages.dev production alias.
4. Re-run the GitHub job from this test branch after adding these settings.

## Verification

- Missing credentials/URL = `NOT_VERIFIED`, **not PASS**.
- Request any URL outside the assigned project's `*.serdararminsargut.pages.dev` Preview subdomains = **FAIL**.
- Login redirects, denied credentials, missing `noindex`, malformed `robots.txt` or XML = **FAIL**.
- The program never writes to any website or logs the token pair.
- `PASS_LOCAL_CI_HTTP` means **authenticated GitHub Actions HTTP** passed; it does not prove ChatGPT Work's own visual browser is authenticated or remove Cloudflare's browser challenges.
- The script intentionally does not change indexable content or deployment configuration. Any failing Preview index policy must be remediated in an independently reviewed staging change.

Official reference: https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/
