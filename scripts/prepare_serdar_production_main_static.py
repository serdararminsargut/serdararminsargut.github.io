#!/usr/bin/env python3
"""Extract and run ONLY the pinned main workflow's harmless static-copy build step.

Never executes any deploy, Cloudflare, secret, git push or network operations.
The user-provided main workflow is pinned externally by Git SHA and Git blob SHA.
"""
import argparse
from pathlib import Path
import subprocess

STEP='      - name: Prepare static site bundle'
END='      - name: Build and verify four Serdar Comp Card PDFs (A4, local-only)'

def prepare(root):
    root=root.resolve()
    source=(root/'.github/workflows/deploy-cloudflare-pages.yml').read_text(encoding='utf-8')
    assert source.count(STEP)==source.count(END)==1,'Unexpected production workflow step count'
    block=source.split(STEP,1)[1].split(END,1)[0]
    assert block.count('        run: |')==1, 'No single shell build step'
    shell_block=block.split('        run: |',1)[1].strip('\n')
    lines=shell_block.splitlines()
    assert lines and all(x.startswith('          ') or not x.strip() for x in lines),'Unexpected YAML block indentation'
    script='\n'.join(x[10:] if x else '' for x in lines)+'\n'
    assert script.lstrip().startswith('set -euo pipefail'),'Missing strict build shell'
    assert 'mkdir -p dist' in script and 'for item in' in script and 'cp -R' in script,'Static copy contract changed'
    for forbidden in ('wrangler','pages deploy','CLOUDFLARE','--branch=main','curl ','gh api'):
        assert forbidden not in script,'Unexpected external operation in copy step: '+forbidden
    subprocess.run(['bash','-e','-c',script],cwd=root,check=True,timeout=90)
    assert (root/'dist/index.html').is_file(), 'Missing homepage after production-static step'
    return script

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--production-source',type=Path,required=True)
    args=ap.parse_args()
    prepare(args.production_source)
    print('SERDAR_PINNED_MAIN_STATIC_COPY_PASS (NO DEPLOY)')