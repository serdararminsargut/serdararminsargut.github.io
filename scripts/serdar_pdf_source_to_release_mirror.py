#!/usr/bin/env python3
"""Rehearse the complete Serdar PDF release build from production-shaped source.

ISOLATED PREPRODUCTION ONLY. No deployment, no mutation of dist, no git/network.
Builds watermarked test -> clean PDF -> metadata-clean PDF -> temp mirror.
The explicit production switch intentionally does not exist.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import fitz

LANGS=("TR","EN","AR","RU")
PREFIX="Serdar-Armin-Sargut-Comp-Card-"

def demand(condition, message):
    if not condition:
        raise AssertionError("SERDAR_SOURCE_TO_RELEASE_NO_GO: "+message)

def h(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(root):
    return {p.relative_to(root).as_posix():h(p) for p in root.rglob("*") if p.is_file()}

def link_set(page):
    return sorted((int(x["kind"]),str(x.get("uri","")),
                   tuple(round(float(v),3) for v in x["from"]))
                  for x in page.get_links())

def run(src:Path,dst:Path):
    src=src.resolve(strict=True)
    dst=dst.resolve()
    demand(src.is_dir() and not src.is_symlink(),"source missing or symlink")
    demand(not dst.exists() and src!=dst and src not in dst.parents and dst not in src.parents,
           "fresh independent output only")
    demand(not any(part in dst.parts for part in ("dist","public","downloads")),
           "output cannot be a publishing directory")
    project=Path(__file__).resolve().parents[1]
    scripts=[
        project/"scripts/serdar_comp_card_pdf_layout_preview.py",
        project/"scripts/serdar_clean_candidate_staging.py",
        project/"scripts/serdar_pdf_metadata_preprod.py",
    ]
    demand(all(p.is_file() for p in scripts),"missing required source-bound layout scripts")
    before=inventory(src)
    names={lang:"downloads/"+PREFIX+lang+".pdf" for lang in LANGS}
    for lang,rel in names.items():
        demand(rel in before,f"{lang}: original generated PDF missing")
    for lang in LANGS:
        p=src/"casting-card"/(lang.lower()+".html")
        demand(p.is_file() and ('data-download-url="/'+names[lang]+'"') in p.read_text(encoding="utf-8"),
               f"{lang}: HTML indirme adresi eski dosya adıyla eşleşmiyor")
    dst.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="serdar-source-to-release-",dir=dst.parent) as scratch:
        tmp=Path(scratch)
        layout=tmp/"layout"
        clean=tmp/"clean"
        ready=tmp/"ready"
        commands=[
            [sys.executable,str(scripts[0]),"--source-root",str(src),"--output-dir",str(layout)],
            [sys.executable,str(scripts[1]),"--input-dir",str(layout),"--output-dir",str(clean)],
            [sys.executable,str(scripts[2]),"--input-root",str(clean),"--output-root",str(ready)],
        ]
        environment=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for command in commands:
            subprocess.run(command,cwd=project,check=True,timeout=120,env=environment)
        proof=json.loads((ready/"SERDAR_METADATA_PREPROD_SHA256.json").read_text(encoding="utf-8"))
        demand(proof.get("project")=="SERDAR_ONLY" and proof.get("publish_authorized") is False,
               "invalid staging source")
        by_lang={r["language"]:r for r in proof["results"]}
        demand(set(by_lang)==set(LANGS),"four languages required")
        shutil.copytree(src,dst,symlinks=False)
        for lang in LANGS:
            candidate=ready/by_lang[lang]["filename"]
            replacement=dst/names[lang]
            demand(h(candidate)==by_lang[lang]["sha256"],f"{lang}: candidate SHA mismatch")
            shutil.copyfile(candidate,replacement)
            demand(h(replacement)==h(candidate),f"{lang}: overlay SHA mismatch")
            with fitz.open(replacement) as doc:
                demand(len(doc)==2,f"{lang}: must have two A4 pages")
                demand(doc.metadata.get("title")==f"Serdar Armin Sargut | Comp Card | {lang}",
                       f"{lang}: PDF metadata incorrect")
                links=link_set(doc[1])
                demand(any(x[1]=="https://serdararminsargut.com/" for x in links),
                       f"{lang}: portfolio link missing")
                demand(any(x[1].startswith("mailto:") for x in links),
                       f"{lang}: email missing")
        after=inventory(dst)
        changed={name for name in before if before[name]!=after.get(name)}
        demand(set(before)==set(after),"unexpected file added/removed in release mirror")
        demand(changed==set(names.values()),"only four PDFs may differ")
        demand(inventory(src)==before,"original dist modified; forbidden")
        result={"project":"SERDAR_ONLY","isolation":"NON_PRODUCTION_TEMP_COPY",
                "deployment_performed":False,"source_files":len(before),
                "changed_files":sorted(changed),
                "unchanged_files":len(before)-4,
                "sha256":{lang:after[names[lang]] for lang in LANGS},
                "source_sha256":{lang:before[names[lang]] for lang in LANGS},
                "result":"SOURCE_TO_PRODUCTION_SHAPED_RELEASE_MIRROR_PASS"}
    output=dst.parent/"SERDAR_SOURCE_TO_RELEASE_MIRROR_NO_DEPLOY.json"
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SERDAR_SOURCE_TO_RELEASE_MIRROR_PASS: 4/4 PDFs, no other file changed, NO DEPLOY",flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",type=Path,required=True)
    parser.add_argument("--output-root",type=Path,required=True)
    a=parser.parse_args()
    run(a.source_root,a.output_root)
