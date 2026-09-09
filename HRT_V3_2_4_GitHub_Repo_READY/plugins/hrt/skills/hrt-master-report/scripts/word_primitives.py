"""OOXML primitives for HRT Master Report V3.2.3.
Use when appending Persian content to a copied Golden Master.
Enforces complex-script B Nazanin runs, structural/semantic RTL tables, centered table cells, Word bullets,
TOC/numbering fidelity primitives, and no Level-2 heading shading.
"""
from __future__ import annotations
from copy import deepcopy
import re
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}; q=lambda n:f'{{{W}}}{n}'
FA=re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF۰-۹]')
LAT=re.compile(r'[A-Za-z0-9]')

def clear_para_keep_ppr(p):
    pPr=p.find(q('pPr'))
    for ch in list(p):
        if ch is not pPr: p.remove(ch)
    if pPr is None: pPr=etree.Element(q('pPr')); p.insert(0,pPr)
    return pPr

def split_script(text):
    out=[]; cur=''; kind=None
    for ch in text:
        k='fa' if FA.search(ch) else ('en' if LAT.search(ch) else kind or 'fa')
        if kind is None: kind=k
        if k!=kind and cur: out.append((kind,cur)); cur=ch; kind=k
        else: cur+=ch; kind=k
    if cur: out.append((kind or 'fa',cur))
    return out

def add_run(p,text,kind='fa',bold=False,size_pt=None,color=None):
    r=etree.SubElement(p,q('r')); rp=etree.SubElement(r,q('rPr')); rf=etree.SubElement(rp,q('rFonts'))
    if kind=='fa':
        rf.set(q('ascii'),'B Nazanin'); rf.set(q('hAnsi'),'B Nazanin'); rf.set(q('cs'),'B Nazanin')
        etree.SubElement(rp,q('rtl')); lg=etree.SubElement(rp,q('lang')); lg.set(q('bidi'),'fa-IR')
    else:
        rf.set(q('ascii'),'Times New Roman'); rf.set(q('hAnsi'),'Times New Roman'); rf.set(q('cs'),'Times New Roman')
        lg=etree.SubElement(rp,q('lang')); lg.set(q('val'),'en-US')
    if bold:
        etree.SubElement(rp,q('b')); etree.SubElement(rp,q('bCs'))
    if size_pt:
        s=etree.SubElement(rp,q('sz')); s.set(q('val'),str(int(size_pt*2)))
        sc=etree.SubElement(rp,q('szCs')); sc.set(q('val'),str(int(size_pt*2)))
    if color:
        c=etree.SubElement(rp,q('color')); c.set(q('val'),color)
    t=etree.SubElement(r,q('t')); t.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); t.text=text

def set_style(p,style_id):
    pPr=p.find(q('pPr'))
    if pPr is None: pPr=etree.Element(q('pPr')); p.insert(0,pPr)
    ps=pPr.find(q('pStyle'))
    if ps is None: ps=etree.Element(q('pStyle')); pPr.insert(0,ps)
    ps.set(q('val'),style_id)
    if pPr.find(q('bidi')) is None: etree.SubElement(pPr,q('bidi'))
    if style_id=='Title2RYM':
        shd=pPr.find(q('shd'))
        if shd is not None: pPr.remove(shd)
    return pPr

def set_persian_paragraph(p,text,style_id='TextbodyRYM',bullet=False):
    pPr=clear_para_keep_ppr(p); set_style(p,style_id)
    if bullet:
        num=pPr.find(q('numPr'))
        if num is None: num=etree.SubElement(pPr,q('numPr'))
        for ch in list(num): num.remove(ch)
        il=etree.SubElement(num,q('ilvl')); il.set(q('val'),'0')
        ni=etree.SubElement(num,q('numId')); ni.set(q('val'),'11')
    else:
        # Heading numbering is style-linked; only clear direct body numbering.
        num=pPr.find(q('numPr'))
        if style_id=='TextbodyRYM' and num is not None: pPr.remove(num)
    for kind,seg in split_script(text): add_run(p,seg,kind)
    return p

def clone_paragraph(template,text,style_id='TextbodyRYM',bullet=False):
    p=deepcopy(template); return set_persian_paragraph(p,text,style_id,bullet)

def ensure_table_rtl(tbl):
    """Add structural RTL. Does not reorder legacy cells by itself."""
    tblPr=tbl.find(q('tblPr'))
    if tblPr is None: tblPr=etree.Element(q('tblPr')); tbl.insert(0,tblPr)
    bv=tblPr.find(q('bidiVisual'))
    if bv is None:
        bv=etree.Element(q('bidiVisual')); tblPr.insert(0,bv)
    bv.set(q('val'),'1')
    return tbl

def reverse_row_cells(tr):
    """Normalize an imported LTR-ordered legacy row when semantic order is reversed.
    Use only after inspecting source semantics. With bidiVisual, first XML cell is the
    first logical Persian column and appears on the visual right in Microsoft Word.
    """
    cells=tr.findall(q('tc'))
    for tc in cells: tr.remove(tc)
    for tc in reversed(cells): tr.append(tc)
    return tr

def semantic_row_cells(tr):
    """Return cells in HRT semantic order: first item is the right-most logical column."""
    return tr.findall(q('tc'))

def center_cell_content(tc):
    """Center a table cell horizontally and vertically while preserving RTL semantics."""
    tcPr=tc.find(q('tcPr'))
    if tcPr is None:
        tcPr=etree.Element(q('tcPr')); tc.insert(0,tcPr)
    va=tcPr.find(q('vAlign'))
    if va is None: va=etree.SubElement(tcPr,q('vAlign'))
    va.set(q('val'),'center')
    for p in tc.xpath('.//w:p',namespaces=NS):
        pPr=p.find(q('pPr'))
        if pPr is None: pPr=etree.Element(q('pPr')); p.insert(0,pPr)
        jc=pPr.find(q('jc'))
        if jc is None: jc=etree.SubElement(pPr,q('jc'))
        jc.set(q('val'),'center')
        if pPr.find(q('bidi')) is None: etree.SubElement(pPr,q('bidi'))
    return tc

def normalize_revision_history(tbl):
    """Normalize HRT revision-history semantic RTL order.
    First XML cell = visual right = شرح/وضعیت; middle = کارشناسان/ افراد; left = تاریخ.
    """
    ensure_table_rtl(tbl)
    rows=tbl.findall(q('tr'))
    for ri,tr in enumerate(rows,1):
        cells=tr.findall(q('tc'))
        if len(cells)!=3: continue
        vals=[''.join(c.xpath('.//w:t/text()',namespaces=NS)).strip() for c in cells]
        if ri==2:
            if vals and vals[0]=='تاریخ': reverse_row_cells(tr); cells=tr.findall(q('tc'))
            set_cell_text(cells[0],'شرح/وضعیت',bold=True,size_pt=11)
            set_cell_text(cells[1],'کارشناسان/ افراد',bold=True,size_pt=11)
            set_cell_text(cells[2],'تاریخ',bold=True,size_pt=11)
        else:
            vals=[''.join(c.xpath('.//w:t/text()',namespaces=NS)).strip() for c in cells]
            if (vals and re.search(r'\d{2}/\d{2}/\d{4}',vals[0] or '')) or any((vals[2] or '').startswith(x) for x in ('تدوین نسخه','تأییدیه','ویراستاری','-')):
                reverse_row_cells(tr)
        for tc in tr.findall(q('tc')): center_cell_content(tc)
    return tbl

def set_cell_text(tc,text,bold=False,size_pt=11):
    p=tc.find('.//'+q('p'))
    if p is None: p=etree.SubElement(tc,q('p'))
    set_persian_paragraph(p,text,'TextbodyRYM',False)
    for rp in p.xpath('./w:r/w:rPr',namespaces=NS):
        # Table default 11 pt unless the caller explicitly passes None.
        if size_pt:
            for tag in ('sz','szCs'):
                old=rp.find(q(tag))
                if old is not None: rp.remove(old)
                x=etree.SubElement(rp,q(tag)); x.set(q('val'),str(int(size_pt*2)))
        if bold:
            if rp.find(q('b')) is None: etree.SubElement(rp,q('b'))
            if rp.find(q('bCs')) is None: etree.SubElement(rp,q('bCs'))
    center_cell_content(tc)
    return tc

def set_semantic_rtl_row(tr, values, *, bold=False, size_pt=11):
    """Populate a row using values in Persian logical order (right -> left).
    Requires/recommends the parent table to have bidiVisual. It intentionally does NOT
    reverse `values`: first value goes to the first XML cell, which is the right-most
    logical column in Word when bidiVisual is active.
    """
    cells=semantic_row_cells(tr)
    if len(cells)!=len(values):
        raise ValueError(f'cell/value count mismatch: {len(cells)} != {len(values)}')
    for tc,val in zip(cells,values): set_cell_text(tc,str(val),bold=bold,size_pt=size_pt)
    return tr
