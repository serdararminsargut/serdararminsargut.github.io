#!/usr/bin/env python3
"""Read-only Access-authenticated Preview HTTP checks. No production requests."""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

PROJECT = "Serdar Armin Sargut"
HOST_BASE = "serdararminsargut"
EXPECTED_BRANCH = "test/serdar-preview-machine-access-20261016"
REPORT = Path("qa-artifacts/preview-access-evidence.json")
HEADERS = ("content-type", "x-robots-tag", "strict-transport-security",
           "x-content-type-options", "referrer-policy", "content-security-policy")

def save(data):
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def preview_url(value):
    parsed = urllib.parse.urlsplit(value.strip())
    host = parsed.hostname or ""
    pattern = r"[a-z0-9-]+\." + re.escape(HOST_BASE) + r"\.pages\.dev"
    if (parsed.scheme != "https" or not re.fullmatch(pattern, host)
            or parsed.port is not None or parsed.username or parsed.password
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("Preview URL must be one exact HTTPS subdomain of the assigned Pages project")
    return "https://" + host

def out(name, value):
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as target:
        target.write(name + "=" + value + "\n")

def preflight():
    if os.environ.get("GITHUB_REF_NAME") != EXPECTED_BRANCH:
        raise SystemExit("Wrong GitHub branch; this gate MUST NOT run from main or production")
    url = os.getenv("PREVIEW_URL", "").strip()
    client_id = os.getenv("CF_ACCESS_CLIENT_ID", "")
    client_secret = os.getenv("CF_ACCESS_CLIENT_SECRET", "")
    if url:
        url = preview_url(url)
    ready = bool(url and client_id and client_secret)
    out("ready", "true" if ready else "false")
    proof = {"project": PROJECT, "scope": "READ_ONLY_PREVIEW",
             "status": "READY_FOR_PROBE" if ready else "NOT_VERIFIED",
             "productionChanges": False,
             "message": "Credentials and URL set; actual proof pending" if ready else
                        "Provide project-scoped Preview URL variable and two private Access secrets"}
    save(proof)
    print(PROJECT + " PREVIEW ACCESS: " + proof["status"])
    if not ready:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### " + PROJECT + " Preview Access: NOT_VERIFIED\n"
                    "No service-token request was made. Configure this project's "
                    "URL variable and two private secrets, then rerun this job.\n")

class DoNotRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class MetaRobots(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "meta":
            return
        values = dict(attrs)
        if values.get("name", "").lower() == "robots":
            self.robots.append(values.get("content", "").lower())

def fetch(opener, origin, path, token_id, token_secret, evidence):
    req = urllib.request.Request(origin + path, headers={
        "CF-Access-Client-Id": token_id,
        "CF-Access-Client-Secret": token_secret,
        "User-Agent": "Duru-Serdar-Preview-CI/1.0",
        "Accept": "*/*",
    })
    try:
        with opener.open(req, timeout=25) as response:
            status = response.status
            response_headers = {k: response.headers.get(k, "") for k in HEADERS}
            body = response.read(5 * 1024 * 1024 + 1)
    except urllib.error.HTTPError as exc:
        status = exc.code
        evidence["checks"].append({"path": path, "status": status,
                                   "result": "FAIL_AUTH_OR_HTTP"})
        raise ValueError("Preview HTTP " + str(status) +
                         " (302 login redirect / 401 / 403 are not authentication PASS)") from None
    if len(body) > 5 * 1024 * 1024:
        raise ValueError("Response body over 5 MB; refuse excessive data")
    evidence["checks"].append({"path": path, "status": status, "headers": response_headers})
    if status != 200:
        raise ValueError("Preview returned HTTP " + str(status) + " at " + path)
    return body, response_headers

def run_probe():
    url = preview_url(os.environ["PREVIEW_URL"])
    client_id = os.environ["CF_ACCESS_CLIENT_ID"]
    client_secret = os.environ["CF_ACCESS_CLIENT_SECRET"]
    evidence = {"project": PROJECT, "scope": "READ_ONLY_PREVIEW",
                "origin": url, "status": "NOT_VERIFIED",
                "productionChanges": False, "checks": [],
                "sourceBranch": EXPECTED_BRANCH}
    try:
        opener = urllib.request.build_opener(DoNotRedirect())
        html_bytes, headers = fetch(opener, url, "/", client_id, client_secret, evidence)
        html_text = html_bytes.decode("utf-8", errors="replace")
        if PROJECT.lower() not in html_text.lower() or "text/html" not in headers["content-type"].lower():
            raise ValueError("Expected portfolio HTML not found; may be a login page or incorrect deployment")
        meta = MetaRobots()
        meta.feed(html_text)
        noindex = ("noindex" in headers["x-robots-tag"].lower()
                   or any("noindex" in v for v in meta.robots))
        evidence["noindex"] = noindex
        if not noindex:
            raise ValueError("Preview noindex NOT_VERIFIED; protect the test deployment before accepting")
        robots_bytes, _ = fetch(opener, url, "/robots.txt", client_id, client_secret, evidence)
        lines = [v.strip() for v in robots_bytes.decode("utf-8", "replace").splitlines()
                 if v.strip() and not v.strip().startswith("#")]
        if chr(92) + "n" in robots_bytes.decode("utf-8", "replace"):
            raise ValueError("Literal backslash-n detected in robots.txt")
        if "User-agent: *" not in lines or "Disallow: /" not in lines:
            raise ValueError("Preview robots.txt does not deny crawler access")
        xml_bytes, _ = fetch(opener, url, "/sitemap.xml", client_id, client_secret, evidence)
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        xml = ET.fromstring(xml_bytes)
        if xml.tag != ns + "urlset":
            raise ValueError("Invalid sitemap XML root / namespace")
        locs = [v.text or "" for v in xml.findall(".//" + ns + "loc")]
        if not locs or len(locs) != len(set(locs)):
            raise ValueError("Missing or duplicate sitemap URLs")
        evidence["sitemapUrls"] = len(locs)
        evidence["status"] = "PASS_LOCAL_CI_HTTP"
        print(PROJECT + " Access-authenticated Preview: PASS (root, noindex, robots, XML sitemap)")
    except Exception as err:
        evidence["status"] = "FAIL"
        evidence["error"] = str(err)
        print(PROJECT + " Preview check failed: " + str(err), file=sys.stderr)
        raise SystemExit(1)
    finally:
        save(evidence)

if __name__ == "__main__":
    if sys.argv[1:] == ["--preflight"]:
        preflight()
    elif sys.argv[1:] == ["--probe"]:
        run_probe()
    else:
        raise SystemExit("Expected --preflight or --probe")
