#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
SEPS = re.compile(r'[\s\-_]+')
GENERIC = {"output","final","hrt_report","hrt_master_report_output"}

def clean_token(value: str) -> str:
    value = (value or "").strip()
    value = INVALID.sub("_", value)
    value = SEPS.sub("_", value)
    value = value.strip(" ._")
    return value

def build_name(domain: str, document_type: str, project_name: str,
               scope: str | None = None, revision: str | None = None,
               ext: str = "docx", user_filename: str | None = None) -> str:
    if user_filename:
        p = Path(user_filename)
        stem = clean_token(p.stem)
        suffix = clean_token(p.suffix.lstrip('.')) or clean_token(ext) or 'docx'
        if not stem:
            raise ValueError('User filename has no usable basename')
        return f"{stem}.{suffix.lower()}"
    required = {
        'domain': clean_token(domain),
        'document_type': clean_token(document_type),
        'project_name': clean_token(project_name),
    }
    missing = [k for k,v in required.items() if not v]
    if missing:
        raise ValueError('Missing required naming components: ' + ', '.join(missing))
    parts = ['HRT', required['domain'], required['document_type'], required['project_name']]
    if scope and clean_token(scope): parts.append(clean_token(scope))
    if revision and clean_token(revision): parts.append(clean_token(revision))
    suffix = clean_token(ext).lower() or 'docx'
    name = '_'.join(parts) + '.' + suffix
    if Path(name).stem.lower() in GENERIC:
        raise ValueError('Generic output filename is forbidden')
    return name

def main():
    p=argparse.ArgumentParser(description='HRT V3.2.4 dynamic output filename resolver')
    p.add_argument('--domain', required=True)
    p.add_argument('--document-type', required=True)
    p.add_argument('--project-name', required=True)
    p.add_argument('--scope')
    p.add_argument('--revision')
    p.add_argument('--ext', default='docx')
    p.add_argument('--user-filename')
    p.add_argument('--json', action='store_true')
    a=p.parse_args()
    name=build_name(a.domain,a.document_type,a.project_name,a.scope,a.revision,a.ext,a.user_filename)
    if a.json:
        print(json.dumps({'filename':name},ensure_ascii=False))
    else:
        print(name)
if __name__=='__main__': main()
