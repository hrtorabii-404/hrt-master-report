#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, zipfile
from pathlib import Path
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}; q=lambda n:f'{{{W}}}{n}'
FA=re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
BULLET_CHARS=('•','','●','◦')
REQ_STYLES={'TextbodyRYM','Title1RYM','Title2RYM','Title3RYM','Title4RYM','Title5RYM'}
LEGACY_HEADER_TERMS=('منطقه ویژه اقتصادی خلیج فارس','سایت اسید فسفوریک')

def parse_args():
    p=argparse.ArgumentParser(description='HRT Master Report V3.2.4 structural/fidelity QA')
    p.add_argument('file',type=Path); p.add_argument('--mode',choices=['report','template'],default='report')
    p.add_argument('--json',type=Path)
    p.add_argument('--expected-filename',type=str,default=None,help='Optional exact basename expected from dynamic naming')
    return p.parse_args()

def txt(el): return ''.join(el.xpath('.//w:t/text()',namespaces=NS))
def xmlroot(parts,n):
    return etree.fromstring(parts[n]) if n in parts and n.endswith('.xml') else None

def style_map(styles):
    return {s.get(q('styleId')):s for s in styles.xpath('//w:style',namespaces=NS)}

def get_numpr(style):
    np=style.find('./w:pPr/w:numPr',namespaces=NS)
    if np is None: return None,None
    il=np.find(q('ilvl')); ni=np.find(q('numId'))
    return (il.get(q('val')) if il is not None else None, ni.get(q('val')) if ni is not None else None)

def run_font_info(r):
    rp=r.find(q('rPr'))
    if rp is None: return None,None,False,False
    rf=rp.find(q('rFonts')); cs=rf.get(q('cs')) if rf is not None else None
    hansi=rf.get(q('hAnsi')) if rf is not None else None
    rtl=rp.find(q('rtl')) is not None
    lg=rp.find(q('lang')); bidi=(lg is not None and lg.get(q('bidi'))=='fa-IR')
    return cs,hansi,rtl,bidi

def add(findings,severity,code,message,**extra):
    findings.append({'severity':severity,'code':code,'message':message,**extra})

def style_font_tuple(style):
    rp=style.find('./w:rPr',namespaces=NS)
    if rp is None: return (None,None,None,None,None)
    rf=rp.find(q('rFonts')); sz=rp.find(q('sz')); b=rp.find(q('b'))
    return (rf.get(q('ascii')) if rf is not None else None,
            rf.get(q('hAnsi')) if rf is not None else None,
            rf.get(q('cs')) if rf is not None else None,
            sz.get(q('val')) if sz is not None else None,
            b is not None)

def main():
    a=parse_args(); findings=[]
    with zipfile.ZipFile(a.file) as z: parts={n:z.read(n) for n in z.namelist()}
    roots={n:etree.fromstring(b) for n,b in parts.items() if n.endswith('.xml') and (n.startswith('word/') or n=='[Content_Types].xml')}
    doc=roots.get('word/document.xml'); styles=roots.get('word/styles.xml'); numbering=roots.get('word/numbering.xml')
    if doc is None or styles is None or numbering is None:
        add(findings,'error','missing_core','Missing document/styles/numbering XML')
    else:
        sm=style_map(styles)
        missing=sorted(REQ_STYLES-set(sm))
        if missing: add(findings,'error','missing_styles','Required Golden Master styles missing',styles=missing)

        # V3.2.3 TOC/list typography: B Nazanin only.
        toc_specs={'TOC1':('24',True),'TOC2':('24',False),'TOC3':('24',False),'TableofFigures':('22',False)}
        for sid,(size_twips,bold_expected) in toc_specs.items():
            st=sm.get(sid)
            if st is None:
                add(findings,'error','toc_style_missing',f'{sid} style missing')
                continue
            ascii_f,hansi_f,cs_f,szv,boldv=style_font_tuple(st)
            if (ascii_f,hansi_f,cs_f)!=('B Nazanin','B Nazanin','B Nazanin'):
                add(findings,'error','toc_font',f'{sid} is not fully B Nazanin',ascii=ascii_f,hAnsi=hansi_f,cs=cs_f)
            if szv!=size_twips:
                add(findings,'error','toc_size',f'{sid} size differs from V3.2.3',actual=szv,expected=size_twips)
            if boldv!=bold_expected:
                add(findings,'error','toc_bold',f'{sid} bold state differs from V3.2.3',actual=boldv,expected=bold_expected)

        # Heading hierarchy + no H2 shading.
        expected={'Title1RYM':('0','1'),'Title2RYM':('1','1'),'Title3RYM':('2','1')}
        for sid,exp in expected.items():
            if sid in sm and get_numpr(sm[sid])!=exp:
                add(findings,'error','heading_numbering',f'{sid} numbering differs from V3.2',actual=get_numpr(sm[sid]),expected=exp)
        if 'Title2RYM' in sm and sm['Title2RYM'].find('./w:pPr/w:shd',namespaces=NS) is not None:
            add(findings,'error','title2_style_shading','Title2_RYM style contains shading')
        for i,p in enumerate(doc.xpath('//w:p',namespaces=NS),1):
            ps=p.find('./w:pPr/w:pStyle',namespaces=NS)
            if ps is not None and ps.get(q('val'))=='Title2RYM' and p.find('./w:pPr/w:shd',namespaces=NS) is not None:
                add(findings,'error','title2_para_shading','Level-2 paragraph contains direct shading',paragraph=i,text=txt(p)[:100])

        # Numbering format exact for numId 1.
        nums=numbering.xpath('//w:num[@w:numId="1"]',namespaces=NS)
        if not nums: add(findings,'error','numbering_num1','numId 1 missing')
        else:
            aid=nums[0].find(q('abstractNumId')).get(q('val'))
            absn=numbering.xpath(f'//w:abstractNum[@w:abstractNumId="{aid}"]',namespaces=NS)
            pats=['%1-','%1-%2-','%1-%2-%3-']
            if not absn: add(findings,'error','numbering_abstract','Abstract numbering for numId 1 missing')
            else:
                lvls=absn[0].findall(q('lvl'))
                for i,pat in enumerate(pats):
                    if i>=len(lvls): add(findings,'error','numbering_level',f'Heading numbering level {i} missing'); continue
                    lt=lvls[i].find(q('lvlText')); actual=lt.get(q('val')) if lt is not None else None
                    if actual!=pat: add(findings,'error','numbering_pattern',f'Level {i} pattern wrong',actual=actual,expected=pat)
                    if actual and any(ch in actual for ch in ('\u200e','\u200f','\u202a','\u202b','\u202c','\u2066','\u2067','\u2068','\u2069')):
                        add(findings,'error','numbering_direction_mark','Direction-control character found in heading numbering pattern',level=i,actual=repr(actual))

        # Structural + semantic RTL tables.
        all_tables=[]
        for n,r in roots.items():
            if n.startswith('word/document') or n.startswith('word/header'):
                for t in r.xpath('//w:tbl',namespaces=NS): all_tables.append((n,t))
        for ti,(part,t) in enumerate(all_tables,1):
            # Only audit tables containing Persian or Header tables as RTL tables.
            ttext=txt(t)
            if FA.search(ttext) or part.startswith('word/header'):
                if t.find('./w:tblPr/w:bidiVisual',namespaces=NS) is None:
                    add(findings,'error','table_rtl',f'Persian table missing bidiVisual',part=part,table=ti)
                # If a row contains ردیف, it must be first XML cell.
                for ri,tr in enumerate(t.findall(q('tr')),1):
                    cells=tr.findall(q('tc')); vals=[txt(c).strip() for c in cells]
                    if any(v=='ردیف' for v in vals) and (not vals or vals[0] != 'ردیف'):
                        add(findings,'error','semantic_rtl_row_number','ردیف is not first logical/XML cell',part=part,table=ti,row=ri,cells=vals)
                # Every cell must be horizontally + vertically centered.
                for ci,tc in enumerate(t.xpath('.//w:tc',namespaces=NS),1):
                    va=tc.find('./w:tcPr/w:vAlign',namespaces=NS)
                    if va is None or va.get(q('val'))!='center':
                        add(findings,'error','table_vertical_center','Table cell is not vertically centered',part=part,table=ti,cell=ci)
                    for pidx,pp in enumerate(tc.xpath('.//w:p',namespaces=NS),1):
                        jc=pp.find('./w:pPr/w:jc',namespaces=NS)
                        if jc is None or jc.get(q('val'))!='center':
                            add(findings,'error','table_horizontal_center','Table cell paragraph is not horizontally centered',part=part,table=ti,cell=ci,paragraph=pidx,text=txt(pp)[:80])
                    # V3.2.3 table font/size gate applies to report-body tables only.
                    # Header tables intentionally have their own approved typography (14/11/10 pt etc.).
                    if part.startswith('word/document'):
                        for ridx,rr in enumerate(tc.xpath('.//w:r',namespaces=NS),1):
                            rt=txt(rr)
                            if not rt.strip():
                                continue
                            rp=rr.find(q('rPr')); rf=rp.find(q('rFonts')) if rp is not None else None
                            sz=rp.find(q('sz')) if rp is not None else None; szcs=rp.find(q('szCs')) if rp is not None else None
                            fonts=((rf.get(q('ascii')) if rf is not None else None),(rf.get(q('hAnsi')) if rf is not None else None),(rf.get(q('cs')) if rf is not None else None))
                            if fonts!=('B Nazanin','B Nazanin','B Nazanin'):
                                add(findings,'error','table_font','Visible body-table run is not fully B Nazanin',part=part,table=ti,cell=ci,run=ridx,text=rt[:80],fonts=fonts)
                            if sz is None or sz.get(q('val'))!='22' or szcs is None or szcs.get(q('val'))!='22':
                                add(findings,'error','table_size','Visible body-table run is not 11 pt',part=part,table=ti,cell=ci,run=ridx,text=rt[:80],sz=(sz.get(q('val')) if sz is not None else None),szCs=(szcs.get(q('val')) if szcs is not None else None))
            # Revision History semantic schema: right/first XML = status, middle = people, left = date.
            if 'تاریخچه گزارش' in ttext:
                rows=t.findall(q('tr'))
                if len(rows)>=2:
                    vals=[txt(c).strip() for c in rows[1].findall(q('tc'))]
                    exp=['شرح/وضعیت','کارشناسان/ افراد','تاریخ']
                    if vals!=exp:
                        add(findings,'error','revision_history_semantic_rtl','Revision History Header semantic order is wrong',actual=vals,expected=exp)
                for ri,tr in enumerate(rows[2:7],3):
                    vals=[txt(c).strip() for c in tr.findall(q('tc'))]
                    if len(vals)==3 and vals[0] and vals[0] not in ('تدوین نسخه اول','تدوین نسخه دوم','تدوین نسخه سوم','تأییدیه','ویراستاری'):
                        add(findings,'error','revision_history_status_column','Revision History status/description is not in first/right XML cell',row=ri,cells=vals)
            # Identity table semantic check by label.
            if 'شناسنامه گزارش' in ttext and 'عنوان پروژه' in ttext:
                rows=t.findall(q('tr'))
                for ri,tr in enumerate(rows[1:],2):
                    vals=[txt(c).strip() for c in tr.findall(q('tc'))]
                    if 'عنوان پروژه' in vals and vals[0] != 'عنوان پروژه':
                        add(findings,'error','identity_semantic_rtl','عنوان پروژه is not first logical/right-side label cell',row=ri,cells=vals)

        # Cached TOC/list result typography and BiDi separator control.
        for pi,p in enumerate(doc.xpath('//w:p',namespaces=NS),1):
            ps=p.find('./w:pPr/w:pStyle',namespaces=NS); sid=ps.get(q('val')) if ps is not None else None
            if sid in ('TOC1','TOC2','TOC3','TableofFigures'):
                ptxt=txt(p)
                if '\u200e' in ptxt or '\u200f' in ptxt:
                    add(findings,'error','toc_direction_mark','LRM/RLM remains in TOC/list cached result; V3.2.3 approved output uses no direction marks',paragraph=pi,text=ptxt[:120])
                for r in p.xpath('.//w:r',namespaces=NS):
                    rt=txt(r)
                    if not rt: continue
                    cs,hansi,rtl,bidi=run_font_info(r)
                    # Page fields/runs are also normalized to B Nazanin in HRT lists.
                    rp=r.find(q('rPr')); rf=rp.find(q('rFonts')) if rp is not None else None
                    ascii_f=rf.get(q('ascii')) if rf is not None else None
                    if (ascii_f,hansi,cs)!=('B Nazanin','B Nazanin','B Nazanin'):
                        add(findings,'error','toc_cached_font','TOC/list cached run is not B Nazanin',paragraph=pi,style=sid,text=rt[:80],ascii=ascii_f,hAnsi=hansi,cs=cs)

        # Typed bullets and Persian body run font/script.
        for pi,p in enumerate(doc.xpath('//w:p',namespaces=NS),1):
            ptxt=txt(p)
            if any(ch in ptxt for ch in BULLET_CHARS): add(findings,'error','typed_bullet','Typed bullet glyph found',paragraph=pi,text=ptxt[:120])
            ps=p.find('./w:pPr/w:pStyle',namespaces=NS); sid=ps.get(q('val')) if ps is not None else None
            if sid=='TextbodyRYM':
                for r in p.findall(q('r')):
                    rtxt=txt(r)
                    if not FA.search(rtxt): continue
                    cs,hansi,rtl,bidi=run_font_info(r)
                    if cs!='B Nazanin' or not (rtl or bidi):
                        add(findings,'error','persian_body_run','Persian body run lacks B Nazanin complex-script/RTL',text=rtxt[:80],cs=cs,hAnsi=hansi,rtl=rtl,bidi=bidi)

        # Header Persian font.
        for n,r in roots.items():
            if not n.startswith('word/header'): continue
            for rr in r.xpath('//w:r',namespaces=NS):
                rt=txt(rr)
                if not FA.search(rt): continue
                cs,hansi,rtl,bidi=run_font_info(rr)
                if cs!='B Nazanin': add(findings,'error','header_font','Persian Header run is not B Nazanin complex script',part=n,text=rt[:80],cs=cs,hAnsi=hansi)

        # Fields. TOC and list fields are always required by the master.
        # SEQ fields are required only when that caption type is actually used in the report.
        field_text=' '.join(doc.xpath('//w:fldSimple/@w:instr',namespaces=NS))+' '+' '.join(doc.xpath('//w:instrText/text()',namespaces=NS))
        if 'TOC' not in field_text: add(findings,'error','missing_field','Missing required field: TOC')
        if '\\c "جدول"' not in field_text and "\\c 'جدول'" not in field_text: add(findings,'error','missing_list_tables','List of Tables field not found')
        if '\\c "تصویر"' not in field_text and "\\c 'تصویر'" not in field_text: add(findings,'error','missing_list_images','List of Images field not found')
        caption_paras=[]
        for p in doc.xpath('//w:p',namespaces=NS):
            ps=p.find('./w:pPr/w:pStyle',namespaces=NS)
            sid=ps.get(q('val')) if ps is not None else None
            if sid=='Caption': caption_paras.append(txt(p).strip())
        uses_table_caption=any(x.startswith('جدول') for x in caption_paras)
        uses_image_caption=any(x.startswith('تصویر') for x in caption_paras)
        if uses_table_caption and 'SEQ جدول' not in field_text: add(findings,'error','missing_field','Table captions exist but SEQ جدول is missing')
        if uses_image_caption and 'SEQ تصویر' not in field_text: add(findings,'error','missing_field','Image captions exist but SEQ تصویر is missing')

        # Unresolved tokens.
        alltext=' '.join(txt(r) for n,r in roots.items() if n.startswith('word/document') or n.startswith('word/header'))
        toks=sorted(set(re.findall(r'\{\{[^}]+\}\}',alltext)))
        if a.mode=='report' and toks: add(findings,'error','unresolved_tokens','Unresolved HRT tokens remain',tokens=toks)

        # Legacy header text.
        htext=' '.join(txt(r) for n,r in roots.items() if n.startswith('word/header'))
        bad=[x for x in LEGACY_HEADER_TERMS if x in htext]
        if bad: add(findings,'error','legacy_header_text','Legacy project-specific Header text remains',terms=bad)

        # Footer default empty.
        for n,r in roots.items():
            if n.startswith('word/footer') and txt(r).strip(): add(findings,'warning','footer_content','Footer is not empty',part=n,text=txt(r)[:100])

    errors=[f for f in findings if f['severity']=='error']; warnings=[f for f in findings if f['severity']=='warning']
    
    if a.expected_filename and a.file.name != a.expected_filename:
        add(findings,'error','output_filename',f'Output filename does not match expected HRT dynamic name',actual=a.file.name,expected=a.expected_filename)
    errors=[f for f in findings if f['severity']=='error']; warnings=[f for f in findings if f['severity']=='warning']
    result={'file':str(a.file),'version':'3.2.4','status':'PASS' if not errors else 'FAIL','errors':errors,'warnings':warnings,'checks':{'error_count':len(errors),'warning_count':len(warnings)}}
    if a.json:
        a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)

if __name__=='__main__': main()
