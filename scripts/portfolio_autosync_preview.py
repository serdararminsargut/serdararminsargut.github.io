#!/usr/bin/env python3
"""Read-only site-to-HugoBlox Preview sync for Serdar and Duru. Never publish."""
from __future__ import annotations
import argparse,hashlib,html,json,re
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen

SITES={
 "serdar":("https://serdararminsargut.com/","casting-card/tr.html","Serdar Armin Sargut"),
 "duru":("https://durumuallasargut.com/","comp-card/tr/","Duru Mualla Sargut")}
VIDEO_HOSTS={"vimeo.com","www.vimeo.com","player.vimeo.com","youtube.com","www.youtube.com","www.youtube-nocookie.com","youtube-nocookie.com","youtu.be"}
class Parser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.photos=[];self.videos=[];self.locales=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="link" and "alternate" in (a.get("rel") or "") and a.get("hreflang"):
   self.locales.append(a["hreflang"])
  if tag=="img" and a.get("src"):self.photos.append(a["src"])
  if a.get("data-video") and re.fullmatch(r"\d{7,13}",a["data-video"]):
   self.videos.append("https://vimeo.com/"+a["data-video"])
  if tag in ("a","iframe","video","source"):
   self.videos += [a[k] for k in ("href","src") if a.get(k)]
def fetch(url):
 p=urlparse(url)
 if p.scheme!="https" or p.hostname not in ("serdararminsargut.com","durumuallasargut.com"):
  raise ValueError("unapproved source domain")
 with urlopen(Request(url,headers={"User-Agent":"PortfolioSyncPreview/1.0","Accept":"text/html"}),timeout=18) as r:
  if r.status!=200 or "text/html" not in r.headers.get("Content-Type",""):
   raise RuntimeError("source did not return HTML 200")
  raw=r.read(2500001)
  if len(raw)>2500000:raise ValueError("HTML too large")
  return raw.decode("utf-8")
def unique(items,limit=40):
 return list(dict.fromkeys(items))[:limit]
def facts(markup):
 markup=html.unescape(markup)
 patterns=[
  r"<(?:span|dt)[^>]*>\s*Boy\s*</(?:span|dt)>\s*<(?:strong|dd)[^>]*>\s*(\d{2,3})\s*cm",
  r'"height"\s*:\s*{\s*"@type"\s*:\s*"QuantitativeValue"\s*,\s*"value"\s*:\s*(\d{2,3})']
 height=next((int(m.group(1)) for p in patterns if (m:=re.search(p,markup,re.I|re.S))),None)
 shoe=re.search(r"<(?:span|dt)[^>]*>\s*Ayakkab[ıi](?: Numaras[ıi])?\s*</(?:span|dt)>\s*<(?:strong|dd)[^>]*>\s*(\d{1,2}(?:[-–]\d{1,2})?)\s*EU",markup,re.I|re.S)
 return {"height_cm":height,"shoe_eu":shoe.group(1) if shoe else None}
def filtered(links,origin,media):
 host=urlparse(origin).hostname
 result=[]
 for link in links:
  if link.startswith(("data:","javascript:","#")):continue
  full=urljoin(origin,link);p=urlparse(full)
  if p.scheme!="https":continue
  if media=="photo" and p.hostname==host and p.path.startswith("/assets/"):result.append(full)
  if media=="video" and p.hostname in VIDEO_HOSTS:result.append(full)
 return unique(result,18)
def run(project,root):
 origin,card,name=SITES[project]
 sources={};errors=[]
 for key,path in (("home",""),("casting",card)):
  try:sources[key]=fetch(urljoin(origin,path))
  except Exception as ex:errors.append(key+": "+str(ex)[:120])
 parser=Parser()
 for page in sources.values():parser.feed(page)
 details=facts(sources.get("casting",""))
 if details["height_cm"] is None: details=facts(sources.get("home",""))
 urls=filtered(parser.videos,origin,"video")
 photos=filtered(parser.photos,origin,"photo")
 langs=unique(parser.locales)
 observations={"height_cm":details["height_cm"],"shoe_eu":details["shoe_eu"],
  "videos":urls,"photos":photos,"hreflang":langs}
 fingerprint=hashlib.sha256(json.dumps(observations,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 status="SOURCE_UNAVAILABLE" if not sources else "PARTIAL_SOURCE" if errors else "OBSERVED_PREVIEW_ONLY"
 # Fail closed: missing source is NOT a real removal or update. Do not replace last healthy Preview.
 if status != "OBSERVED_PREVIEW_ONLY":
  raise SystemExit("AUTOSYNC_BLOCKED_"+project.upper()+": source unavailable/partial; preserve previous Preview; details="+", ".join(errors))
 result={"project":project,"source":origin,"status":status,
  "checked_at_utc":datetime.now(timezone.utc).isoformat(),
  "observation_sha256":fingerprint,**observations,"errors":errors,
  "never_auto_publish":True,"measurements_require_parent_approval":True}
 output=root/"rehber"/"portfoy-guncel";output.mkdir(parents=True,exist_ok=True)
 (output/"source-status.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 esc=lambda v:html.escape(str(v),quote=True)
 def linkitems(items):return "".join('<li><a rel="noopener noreferrer" href="'+esc(u)+'">'+esc(u)+'</a></li>' for u in items[:12])
 content=('<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow,noarchive">'
 '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio Auto-Sync Preview</title></head>'
 '<body style="font:16px/1.5 system-ui;max-width:800px;margin:auto;padding:24px">'
 '<h1>'+esc(name)+' — Önizleme eşitleme</h1><p>Yalnızca test, veri gözlemidir; yayın onayı değildir.</p>'
 '<p>Kaynak: '+esc(origin)+'</p><p>Durum: '+esc(status)+'</p>'
 '<p>Boy (sitede gözlenen): '+esc(details["height_cm"] if details["height_cm"] is not None else "doğrulanamadı")+'</p>'
 '<p>Ayakkabı: '+esc(details["shoe_eu"] or "doğrulanamadı")+'</p>'
 '<p>Dil kodları: '+esc(", ".join(langs))+'</p>'
 '<h2>Videolar</h2><ul>'+linkitems(urls)+'</ul><h2>Fotoğraflar</h2><ul>'+linkitems(photos)+'</ul></body></html>')
 (output/"index.html").write_text(content,encoding="utf-8")
 print("AUTOSYNC_"+project.upper()+"_"+status+" preview snapshot only; no production changes",flush=True)
 if errors:print("SOURCE CHECK WARNING: "+", ".join(errors),flush=True)

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--project",choices=sorted(SITES),required=True)
 ap.add_argument("--root",type=Path,required=True)
 args=ap.parse_args();run(args.project,args.root)
