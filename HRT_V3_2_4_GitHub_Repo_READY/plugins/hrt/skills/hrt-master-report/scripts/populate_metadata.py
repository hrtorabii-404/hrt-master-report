#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, zipfile
from pathlib import Path
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
CUST='http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
VT='http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
qn=lambda ns,n:f'{{{ns}}}{n}'

FIELDS={
'CoverTitle1','CoverTitle2','CoverStageTitle','CoverSubtitle','CoverDateLine',
'ProjectTitle','ReportTitle','ReportCode','VolumeNo','ProjectManager','ProjectControl',
'KeyContributors','OtherTeam','AdditionalTeam','SupportTeam','CopyCount','IssueDate',
'TransmittalNo','PreparedBy','HeaderProjectTitle','HeaderReportTitle','Classification'
}

def parse_args():
    p=argparse.ArgumentParser(description='Populate HRT Master Report V3.2 metadata into a new DOCX without rebuilding layout.')
    p.add_argument('input',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--metadata-json',type=Path); p.add_argument('--set',action='append',default=[])
    return p.parse_args()

def load_values(a):
    vals={k:'' for k in FIELDS}
    if a.metadata_json:
        data=json.loads(a.metadata_json.read_text(encoding='utf-8'))
        if not isinstance(data,dict): raise ValueError('metadata JSON must be an object')
        for k,v in data.items():
            if k in FIELDS: vals[k]='' if v is None else str(v)
    for item in a.set:
        if '=' not in item: raise ValueError('--set requires KEY=VALUE')
        k,v=item.split('=',1); k=k.strip()
        if k not in FIELDS: raise ValueError(f'Unknown metadata key: {k}')
        vals[k]=v
    vals['ClassificationInline']=f"({vals['Classification']})" if vals.get('Classification','').strip() else ''
    return vals

def xmlbytes(root): return etree.tostring(root,encoding='utf-8',xml_declaration=True,standalone='yes')

def replace_tokens(data, vals):
    try: root=etree.fromstring(data)
    except etree.XMLSyntaxError: return data
    for t in root.iter(qn(W,'t')):
        if not t.text: continue
        for k,v in vals.items(): t.text=t.text.replace('{{'+k+'}}',v)
    return xmlbytes(root)

def add_custom_props(parts, vals):
    name='docProps/custom.xml'
    if name in parts: root=etree.fromstring(parts[name])
    else: root=etree.Element(qn(CUST,'Properties'),nsmap={None:CUST,'vt':VT})
    existing={p.get('name'):p for p in root.findall(qn(CUST,'property'))}
    maxpid=max([int(p.get('pid','1')) for p in existing.values()] or [1])
    for k,v in vals.items():
        if k=='ClassificationInline': continue
        p=existing.get(k)
        if p is None:
            maxpid+=1; p=etree.SubElement(root,qn(CUST,'property'),fmtid='{D5CDD505-2E9C-101B-9397-08002B2CF9AE}',pid=str(maxpid),name=k)
        for ch in list(p): p.remove(ch)
        etree.SubElement(p,qn(VT,'lpwstr')).text=v
    parts[name]=xmlbytes(root)

def ensure_custom_plumbing(parts):
    # Content type
    ct=etree.fromstring(parts['[Content_Types].xml'])
    if not any(x.get('PartName')=='/docProps/custom.xml' for x in ct):
        etree.SubElement(ct,qn(CT,'Override'),PartName='/docProps/custom.xml',ContentType='application/vnd.openxmlformats-officedocument.custom-properties+xml')
    parts['[Content_Types].xml']=xmlbytes(ct)
    # root relationship
    relname='_rels/.rels'; rr=etree.fromstring(parts[relname])
    typ='http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties'
    if not any(x.get('Type')==typ for x in rr):
        used=[]
        for x in rr:
            m=re.match(r'rId(\d+)$',x.get('Id',''))
            if m: used.append(int(m.group(1)))
        rid=f'rId{max(used or [0])+1}'
        etree.SubElement(rr,qn(REL,'Relationship'),Id=rid,Type=typ,Target='docProps/custom.xml')
    parts[relname]=xmlbytes(rr)

def main():
    a=parse_args(); src=a.input.resolve(); out=a.output.resolve()
    if src==out: raise SystemExit('Refusing to overwrite master input')
    vals=load_values(a)
    with zipfile.ZipFile(src) as z: parts={n:z.read(n) for n in z.namelist()}
    for n in ['word/document.xml','word/header5.xml','word/header6.xml']:
        if n in parts: parts[n]=replace_tokens(parts[n],vals)
    if 'word/settings.xml' in parts:
        s=etree.fromstring(parts['word/settings.xml']); u=s.find(qn(W,'updateFields'))
        if u is None: u=etree.SubElement(s,qn(W,'updateFields'))
        u.set(qn(W,'val'),'true'); parts['word/settings.xml']=xmlbytes(s)
    add_custom_props(parts,vals); ensure_custom_plumbing(parts)
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_suffix('.tmp.docx')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in parts.items(): z.writestr(n,b)
    os.replace(tmp,out)
    print(out)
if __name__=='__main__': main()
