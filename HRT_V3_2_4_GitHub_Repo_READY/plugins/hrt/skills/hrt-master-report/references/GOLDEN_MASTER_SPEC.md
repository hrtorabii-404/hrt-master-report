# HRT Master Report V3.2.3 — Golden Master Fidelity Specification

## Scope

Generic reporting standard for passive defense/CIP, FS/PFS, investment studies, urban/regional planning, executive/management reports and proposals.

## Golden Master family

Primary visual/Word source: `KNG-HGS-0506-PD-REP-02-00-R01.docx`.
Extended structural reference: `مطالعات پدافندغیرعامل منطقه آزاد دوغارون.docx`.

V3.2.3 follows **clone-and-populate** for fixed Word structures.

## Body typography

`Textbody_RYM`: B Nazanin 12 pt for Persian complex-script runs; Times New Roman for Latin runs; RTL, Justified, 1.15 spacing, first-line indent ≈ 0.55 cm.

## Headings and numbering

- `Title1_RYM`: 16 pt
- `Title2_RYM`: 15 pt, **no shading/fill**
- `Title3_RYM`: 14 pt
- `Title4_RYM`: 13 pt
- `Title5_RYM`: 12 pt

Levels 1–3 use one multilevel numbering definition with **plain** patterns:

- `%1-`
- `%1-%2-`
- `%1-%2-%3-`

No LRM, RLM or Unicode direction-control character is permitted inside `w:lvlText`. The approved body numbering is not modified to solve TOC rendering.

## Tables

All Persian tables must contain `w:tblPr/w:bidiVisual`.

**Semantic RTL rule:** the XML cell sequence follows the logical Persian column sequence so the first logical column appears on the visual right in Microsoft Word. If a standard table has `ردیف`, it is the first logical/XML Header cell.

All report-body/content table cell content uses **B Nazanin 11 pt**, horizontally centered and vertically centered. Header cells are bold with `#D9D9D9` fill and thin black borders.

Revision history semantic order:

- first/right XML cell: `شرح/وضعیت`
- middle: `کارشناسان/ افراد`
- left: `تاریخ`

## TOC and fields

- TOC is Word-native and RTL.
- Lists use caption labels `جدول` and `تصویر`.
- Caption fields: `SEQ جدول`, `SEQ تصویر`.
- Cross-references: bookmark + `REF`.
- PAGE / NUMPAGES remain fields.

TOC direction/layout is controlled only at TOC paragraph/style/tab/field level. It must not change heading numbering definitions.

TOC/list fonts:

- TOC1: B Nazanin 12 pt bold
- TOC2: B Nazanin 12 pt
- TOC3: B Nazanin 12 pt
- Table of Figures: B Nazanin 11 pt

## Render note

LibreOffice headless does not faithfully reproduce every anchored cover object or Microsoft Word RTL table visual ordering. Structural OOXML checks are mandatory in addition to PNG review. Microsoft Word is the fidelity authority for those constructs.
