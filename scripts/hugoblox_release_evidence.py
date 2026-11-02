#!/usr/bin/env python3
"""Isolated HugoBlox release evidence only: byte freeze and Cloudflare GET.

NEVER deploys, writes DNS, runs Wrangler, pushes git, or updates a production file.
This module is safe to run only on an isolated, already-accepted merged static root.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tarfile
import urllib.request
from datetime import datetime, timezone
from urllib.parse import quote

PROJECT = {
    'SERDAR': ('serdararminsargut', 'https://serdararminsargut.com', 95, 155),
    'DURU': ('duru-mualla-sargut-site', 'https://durumuallasargut.com', 36, 115),
}


def require(ok, msg):
    if not ok:
        raise ValueError('NO_GO: ' + msg)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def verified_files(root):
    require(root.is_dir() and not root.is_symlink(), 'merged root missing or a symlink')
    paths = sorted(root.rglob('*'), key=lambda p: p.relative_to(root).as_posix())
    require(paths, 'empty release root')
    require(not any(p.is_symlink() for p in paths), 'symlink inside release root')
    files = [p for p in paths if p.is_file()]
    require(not any(not p.is_dir() and not p.is_file() for p in paths), 'unsupported file type')
    for p in files:
        relative = p.relative_to(root).as_posix()
        parts = Path(relative).parts
        require(not any(v.startswith('.') and v not in ('.nojekyll', '.well-known') for v in parts),
                'unapproved hidden file inside release root: ' + relative)
        require(not any(x in relative.lower() for x in ('/portfoy-guncel/', 'source-status.json', '__qa_', '.env')),
                'unapproved preview/diagnostic file: ' + relative)
    return files


def freeze(project, root, report, out, commit):
    project = project.upper()
    require(project in PROJECT, 'unsupported project')
    require(re.fullmatch(r'[a-f0-9]{40}', commit) is not None, 'full git commit required')
    project_slug, origin, url_count, preserved = PROJECT[project]
    root, report, out = root.resolve(), report.resolve(), out.resolve()
    require(report.is_file(), 'full merge gate report missing')
    r = json.loads(report.read_text(encoding='utf-8'))
    for key, expected in {
        'project': project, 'status': 'OFFLINE_FULL_MERGE_PASS',
        'production_published': False, 'production_publish_authorized': False,
        'baseline_sitemap_urls': url_count - 5, 'new_rehber_urls': 5,
        'offline_merged_sitemap_urls': url_count, 'local_http_200': 5,
        'original_files_hash_preserved': preserved,
        'preview_data_excluded': True,
    }.items():
        require(r.get(key) == expected, 'gate report mismatch: ' + key)
    require(len(r.get('html_checks', [])) == 5, 'five HTML checks missing')
    require(not out.exists() or (out.is_dir() and not any(out.iterdir())),
            'output directory is not new/empty')
    require(out not in root.parents and root not in out.parents and
            out not in report.parents and report not in out.parents,
            'input/output directory overlap')
    files = verified_files(root)
    require((root/'rehber/index.html').is_file() and (root/'sitemap.xml').is_file(),
            'missing guide or sitemap')
    if project == 'SERDAR':
        require((root/'sitemap-google.xml').is_file(), 'Google sitemap missing')
    else:
        require(len(list((root/'comp-card').glob('*/index.html'))) == 26, '26 HTML lost')
        require(len(list((root/'comp-card').rglob('*.pdf'))) == 26, '26 PDF lost')
    manifest = []
    for p in files:
        relative = p.relative_to(root).as_posix()
        content = p.read_bytes()
        manifest.append({'path': relative, 'size_bytes': len(content), 'sha256': sha(content)})
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f'{project.lower()}-full-static-{commit[:12]}.tar.gz'
    # Sorted names, constant mtime / owner and deterministic gzip header.
    with archive.open('wb') as handle:
        with gzip.GzipFile(fileobj=handle, mode='wb', filename='', mtime=0, compresslevel=6) as gz:
            with tarfile.open(fileobj=gz, mode='w|') as tar:
                for p in files:
                    name = p.relative_to(root).as_posix()
                    data = p.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.mode = 0o644
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    info.mtime = 0
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
    # Reopen and verify every single archived byte against a recorded source hash.
    expected = {r['path']: r for r in manifest}
    seen = set()
    with tarfile.open(archive, mode='r:gz') as tar:
        for member in tar:
            require(member.isfile() and member.name in expected and member.name not in seen,
                    'unexpected archive member: ' + member.name)
            data = tar.extractfile(member).read()
            require(sha(data) == expected[member.name]['sha256'],
                    'archive data differs from source: ' + member.name)
            seen.add(member.name)
    require(seen == set(expected), 'archive missing source files')
    metadata = {
        'kind': 'IMMUTABLE_OFFLINE_RELEASE_EVIDENCE_NOT_DEPLOYED',
        'project': project, 'site': origin, 'cloudflare_project': project_slug,
        'staging_commit': commit, 'production_publish_authorized': False,
        'production_published': False, 'new_rehber_pages': 5,
        'merged_sitemap_urls': url_count, 'old_files_preserved': preserved,
        'file_count': len(manifest),
        'archive': archive.name, 'archive_bytes': archive.stat().st_size,
        'archive_sha256': sha(archive.read_bytes()),
        'files': manifest,
    }
    write_json(out / (project.lower() + '-static-manifest.json'), metadata)
    print(f'{project}_IMMUTABLE_FULLROOT_EVIDENCE_PASS: {len(files)} files; '
          f'{url_count} sitemap URLs; SHA256={metadata["archive_sha256"]}; NO DEPLOY')
    return metadata


def fetch_cloudflare(url, token):
    # Explicitly GET only. Do not add POST/PUT/PATCH/DELETE or leak the token.
    request = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }, method='GET')
    with urllib.request.urlopen(request, timeout=20) as response:
        result = json.load(response)
    require(result.get('success') is True, 'Cloudflare returned success=false')
    return result.get('result')


def cloudflare_readonly(project, output):
    project = project.upper()
    require(project in PROJECT, 'unsupported project')
    slug = PROJECT[project][0]
    account = os.environ.get('CLOUDFLARE_ACCOUNT_ID','').strip()
    matches = re.search(r'dash\.cloudflare\.com/([a-fA-F0-9]{32})',account)
    if matches:
        account = matches.group(1)
    require(re.fullmatch('[a-fA-F0-9]{32}', account) is not None,
            'Cloudflare account ID missing/malformed')
    token = os.environ.get('CLOUDFLARE_API_TOKEN','')
    require(bool(token), 'Cloudflare API token unavailable')
    base = ('https://api.cloudflare.com/client/v4/accounts/' + account +
            '/pages/projects/' + quote(slug, safe=''))
    project_info = fetch_cloudflare(base, token)
    require(project_info.get('name') == slug, 'wrong Cloudflare project')
    require(project_info.get('production_branch') == 'main', 'production branch is not main')
    deployments = fetch_cloudflare(base + '/deployments?env=production&per_page=15', token)
    require(isinstance(deployments, list), 'production deployment list missing')
    production = [d for d in deployments if d.get('environment') == 'production']
    require(production, 'no production deployment returned')
    production.sort(key=lambda d: d.get('created_on',''), reverse=True)
    candidates = []
    for d in production:
        metadata = (d.get('deployment_trigger') or {}).get('metadata') or {}
        branch = metadata.get('branch')
        require(not branch or branch == 'main', 'non-main deployment returned as production')
        candidates.append({
            'deployment_id': d.get('id'),
            'created_on': d.get('created_on'),
            'url': d.get('url'),
            'environment': d.get('environment'),
            'stage_status': (d.get('latest_stage') or {}).get('status'),
            'branch': branch,
            'commit_hash': metadata.get('commit_hash'),
        })
    latest = candidates[0]
    require(bool(latest['deployment_id']), 'latest production deployment ID missing')
    good = next((d for d in candidates if d['stage_status']=='success'), None)
    require(good is not None, 'no successful production rollback candidate returned')
    record = {
        'kind': 'READ_ONLY_CLOUDFLARE_PRODUCTION_BASELINE',
        'project': project,
        'cloudflare_pages_project': slug,
        'observed_at_utc': datetime.now(timezone.utc).isoformat(),
        'production_branch': 'main',
        'latest_production_deployment': latest,
        'rollback_candidate_production': good,
        'number_of_returned_production_deployments': len(candidates),
        'note': 'Read-only API GET. This record alone does not authorize deployment or rollback.',
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, record)
    print(f'{project}_CLOUDFLARE_READONLY_BASELINE_PASS: latest production and rollback IDs recorded; NO DEPLOY')
    return record


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='mode',required=True)
    a=sub.add_parser('freeze')
    a.add_argument('--project', choices=PROJECT, required=True)
    a.add_argument('--merged-root', type=Path, required=True)
    a.add_argument('--report', type=Path, required=True)
    a.add_argument('--output-dir', type=Path, required=True)
    a.add_argument('--staging-commit', required=True)
    b=sub.add_parser('cloudflare')
    b.add_argument('--project', choices=PROJECT, required=True)
    b.add_argument('--output', type=Path, required=True)
    args=ap.parse_args()
    if args.mode=='freeze':
        freeze(args.project,args.merged_root,args.report,args.output_dir,args.staging_commit)
    else:
        cloudflare_readonly(args.project,args.output)


if __name__=='__main__':
    main()