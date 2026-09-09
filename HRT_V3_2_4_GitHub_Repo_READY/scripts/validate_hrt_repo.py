#!/usr/bin/env python3
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
errs=[]
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errs.append(f"JSON invalid {p}: {e}"); return {}
mp = root/'.agents/plugins/marketplace.json'
pj = root/'plugins/hrt/.codex-plugin/plugin.json'
for p in [mp,pj]:
    if not p.exists(): errs.append(f"Missing {p}")
market=load(mp) if mp.exists() else {}
man=load(pj) if pj.exists() else {}
if man.get('name')!='hrt': errs.append('plugin name must be hrt')
if man.get('version')!='3.2.4': errs.append('plugin version must be 3.2.4')
if man.get('interface',{}).get('displayName')!='HRT': errs.append('displayName must be HRT')
if not re.fullmatch(r'\d+\.\d+\.\d+', man.get('version','')): errs.append('version must be semver')
sk = root/'plugins/hrt/skills/hrt-master-report/SKILL.md'
if not sk.exists(): errs.append('SKILL.md missing')
for rel in [man.get('interface',{}).get('composerIcon'), man.get('interface',{}).get('logo')]:
    if rel and not (root/'plugins/hrt'/rel).exists(): errs.append(f'missing asset {rel}')
# no unresolved app id in active manifest
if 'apps' in man:
    ap = root/'plugins/hrt/.app.json'
    if not ap.exists(): errs.append('plugin declares apps but .app.json missing')
    else:
        txt=ap.read_text(encoding='utf-8')
        if 'REPLACE' in txt: errs.append('.app.json contains placeholder')
# Confirm approved typography rules exist in skill
if sk.exists():
    txt=sk.read_text(encoding='utf-8')
    for token in ['B Nazanin', '11 pt', '12 pt', 'Dynamic output naming', 'Semantic RTL']:
        if token.lower() not in txt.lower(): errs.append(f'SKILL missing expected rule: {token}')
print('HRT repo validation:', 'PASS' if not errs else 'FAIL')
for e in errs: print('-',e)
raise SystemExit(1 if errs else 0)
