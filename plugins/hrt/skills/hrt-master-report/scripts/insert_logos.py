#!/usr/bin/env python3
from __future__ import annotations
import argparse, io, os, zipfile
from pathlib import Path
from PIL import Image

SLOTS={
 'client': [('word/media/hrt_client_cover.png','PNG'),('word/media/hrt_client_header.jpg','JPEG')],
 'consultant': [('word/media/hrt_consultant_logo.jpg','JPEG'),('word/media/hrt_consultant_logo_fallback.jpeg','JPEG')],
}

def fit(src:Path,target_bytes:bytes,fmt:str):
    target=Image.open(io.BytesIO(target_bytes)); tw,th=target.size
    im=Image.open(src).convert('RGBA')
    canvas=Image.new('RGBA',(tw,th),(255,255,255,0 if fmt=='PNG' else 255))
    im.thumbnail((max(1,int(tw*.88)),max(1,int(th*.88))),Image.Resampling.LANCZOS)
    canvas.alpha_composite(im,((tw-im.width)//2,(th-im.height)//2))
    out=io.BytesIO()
    if fmt=='PNG': canvas.save(out,'PNG')
    else: canvas.convert('RGB').save(out,'JPEG',quality=95)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description='Replace HRT V3.1 semantic logo image parts while preserving cover/Header geometry.')
    p.add_argument('input',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--client-logo',type=Path); p.add_argument('--consultant-logo',type=Path)
    a=p.parse_args()
    if a.input.resolve()==a.output.resolve(): raise SystemExit('Refusing to overwrite input')
    with zipfile.ZipFile(a.input) as z: parts={n:z.read(n) for n in z.namelist()}
    replaced=0
    for key,src in [('client',a.client_logo),('consultant',a.consultant_logo)]:
        if not src: continue
        for part,fmt in SLOTS[key]:
            if part in parts:
                parts[part]=fit(src,parts[part],fmt); replaced+=1
    tmp=a.output.with_suffix('.tmp.docx')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in parts.items(): z.writestr(n,b)
    os.replace(tmp,a.output)
    print(a.output); print('replacements=',replaced)
if __name__=='__main__': main()
