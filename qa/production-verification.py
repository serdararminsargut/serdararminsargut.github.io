"""Read-only release evidence: CF provider GET and narrow custom-domain GETs."""
import hashlib
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

cfg = json.loads(Path('qa/production-verification-config.json').read_text())
assert os.environ['GITHUB_REF_NAME'] == cfg['qa_branch']
account = os.environ['CF_ACCOUNT']
match = re.search(r'dash\.cloudflare\.com/([a-fA-F0-9]{32})', account)
if match:
    account = match[1]
assert re.fullmatch('[a-fA-F0-9]{32}', account)

def provider(path):
    assert path.startswith('/pages/projects/' + cfg['project'])
    req = urllib.request.Request('https://api.cloudflare.com/client/v4/accounts/' + account + path,
        headers={'Authorization': 'Bearer ' + os.environ['CF_TOKEN'], 'Accept': 'application/json'}, method='GET')
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
    assert result.get('success'), 'Provider read failed'
    return result['result']

class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonicals = []
        self.robots = []
        self.descriptions = []
        self.og = []
        self.alternates = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'canonical': self.canonicals.append(a.get('href'))
        if tag == 'link' and a.get('rel') == 'alternate' and a.get('hreflang'):
            self.alternates.append({'lang': a['hreflang'], 'href': a.get('href')})
        if tag == 'meta' and a.get('name') == 'robots': self.robots.append(a.get('content', ''))
        if tag == 'meta' and a.get('name') == 'description': self.descriptions.append(a.get('content'))
        if tag == 'meta' and a.get('property') == 'og:description': self.og.append(a.get('content'))

result = {'person': cfg['person'], 'recorded_at': datetime.now(ZoneInfo('Europe/Istanbul')).isoformat(timespec='seconds'),
          'method': 'Cloudflare Pages API GET plus narrow custom-domain HTTP GET; no deploy or setting mutation',
          'approved_application_source': cfg['approved_source'], 'main': cfg['main'],
          'prior_production_id': cfg['previous_production_id'], 'http': [],
          'normal_bundle_prior_measured': cfg['normal_bundle'],
          'provider_file_count': 'ölçülemedi', 'provider_total_bytes': 'ölçülemedi',
          'browser_or_Lighthouse_or_all_PDF_suite_repeated': False,
          'deployment_or_DNS_or_settings_write': False}
Path('work-release-evidence').mkdir(exist_ok=True)
try:
    project = provider('/pages/projects/' + cfg['project'])
    assert project['name'] == cfg['project'] and project['production_branch'] == 'main'
    canonical = project['canonical_deployment']
    deployment = provider('/pages/projects/' + cfg['project'] + '/deployments/' + canonical['id'])
    metadata = deployment.get('deployment_trigger', {}).get('metadata', {})
    assert deployment['environment'] == 'production', 'Wrong deployment environment'
    assert metadata.get('branch') == 'main' and metadata.get('commit_hash') == cfg['main'], 'Provider source mismatch'
    assert deployment['latest_stage']['status'] == 'success', 'Provider deployment not successful'
    raw_config = {k:project.get(k) for k in ('production_branch','build_config','source','deployment_configs','domains')}
    config_hash = hashlib.sha256(json.dumps(raw_config, sort_keys=True).encode()).hexdigest()
    result['provider'] = {'project': cfg['project'], 'environment': deployment['environment'],
        'deployment_id': deployment['id'], 'commit': metadata['commit_hash'], 'branch': metadata['branch'],
        'status': deployment['latest_stage']['status'], 'created_on': deployment['created_on'],
        'created_on_Istanbul': datetime.fromisoformat(deployment['created_on'].replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Istanbul')).isoformat(),
        'url': deployment.get('url'), 'canonical_deployment_id': canonical['id'],
        'config_sha256': config_hash, 'baseline_config_sha256': cfg['config_sha256'],
        'config_unchanged': config_hash == cfg['config_sha256'],
        'build_config': {k:(deployment.get('build_config') or {}).get(k) for k in ('build_command','destination_dir','root_dir')}}
    assert config_hash == cfg['config_sha256'], 'Provider project configuration differs from recorded baseline'
    try:
        logs = provider('/pages/projects/' + cfg['project'] + '/deployments/' + deployment['id'] + '/history/logs')
        text = '\n'.join(str(x.get('line') or '') for x in (logs.get('data') or []))
        totals = [int(x) for x in re.findall(r'Uploading[^\n]*\(\s*\d+\s*/\s*(\d+)\s*\)', text, re.I)]
        result['provider_build_log_indicators'] = {'lines': len(logs.get('data') or []),
            'upload_progress_total': max(totals) if totals else None,
            'reviewed_renderer_executed': 'DURU_PORTFOLIO_RENDERED' in text,
            'pdf_preservation_seen': 'PDF_PRESERV' in text or '26/26' in text}
        if totals: result['provider_file_count'] = max(totals)
    except Exception as exc:
        result['provider_build_log_indicators'] = {'unavailable': type(exc).__name__}
    for item in cfg['requests']:
        url = cfg['origin'] + item['route']
        req = urllib.request.Request(url, headers={'User-Agent':'Portfolio-Approved-Release-Verification/1.0'}, method='GET')
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read()
            entry = {'url': url, 'final_url': response.geturl(), 'status': response.status,
                'content_type': response.headers.get('Content-Type'), 'X-Robots-Tag': response.headers.get('X-Robots-Tag'),
                'CSP': response.headers.get('Content-Security-Policy'),
                'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
        result['http'].append(entry)
        assert entry['status'] == 200 and entry['final_url'] == url, 'Critical canonical URL redirected or failed'
        entry['raw_bundle_sha_match'] = entry['sha256'] == item['sha256']
        if item['kind'] == 'html':
            assert 'text/html' in (entry['content_type'] or '')
            assert 'noindex' not in (entry['X-Robots-Tag'] or '').lower(), 'Unexpected production noindex header'
            markup = body.decode('utf-8')
            head = Head(); head.feed(markup)
            entry.update(canonicals=head.canonicals, robots=head.robots, description=head.descriptions,
                         og_description=head.og, alternates=head.alternates)
            assert head.canonicals == [url], 'Missing/duplicate/wrong canonical'
            assert all('noindex' not in value.lower() for value in head.robots)
            if item.get('description'):
                assert head.descriptions == [item['description']] and head.og == [item['description']], 'Description mismatch'
            if item.get('alternate_count'):
                assert len(head.alternates) == item['alternate_count'] and len({x['lang'] for x in head.alternates}) == item['alternate_count']
            if item.get('absent_aria'):
                assert item['absent_aria'] not in markup, 'Obsolete CTA label survived'
        else:
            assert entry['raw_bundle_sha_match'], 'Static SEO/CSS response differs from accepted normal bundle'
            if item['kind'] == 'sitemap':
                assert 'xml' in (entry['content_type'] or '').lower()
                xml = ET.fromstring(body)
                locs = [x.text for x in xml.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
                assert locs and len(locs) == len(set(locs)) and all(x.startswith(cfg['origin'] + '/') for x in locs)
                entry['sitemap_URL_count'] = len(locs)
            if item['kind'] == 'robots':
                assert ('Sitemap: ' + cfg['origin'] + '/sitemap.xml') in body.decode('utf-8')
        entry['result'] = 'PASS'
    result['result'] = 'PASS'
except Exception as exc:
    result['result'] = 'FAIL'
    result['error_type'] = type(exc).__name__
    result['reason'] = str(exc) if isinstance(exc, AssertionError) else 'Read operation failed; credentials and response details withheld'
finally:
    Path('work-release-evidence/production-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'person': cfg['person'], 'result': result.get('result'), 'provider': result.get('provider'),
                      'HTTP_checked': len(result['http']), 'reason': result.get('reason')}, ensure_ascii=False))
if result['result'] != 'PASS': raise SystemExit(1)
