---
name: hrt-master-report
description: "Create, revise, or audit native editable Persian RTL Word reports with HRT Master Report V3.2.4. Use for passive-defense/CIP reports, FS/PFS, investment studies, urban and regional planning, executive/management reports, proposals, and formal technical reports. Treat HRT, HRT Master, HRT Report, قالب HRT, گزارش HRT, HRT Master Report, HRT Master V3.2.3, and the legacy phrase HR Master Report as explicit invocation cues for report/document tasks; no @ or $ prefix is required."
---

# HRT Master Report V3.2.4 — Numbering Regression Fix

HRT means **Hamid Reza Torabi**. This is a **generic master reporting framework**, not a passive-defense-only template.

Supported primary profiles:

- Passive Defense / CIP
- FS / PFS
- Investment Study
- Urban & Regional Planning
- Executive / Management Report
- Proposal / Technical Offer

## Core architecture

**Golden Master controls Word. Profile controls content.**

The report profile may change chapter logic, analytical modules, evidence checks and deliverables. It must not redesign the fixed Word layer. Cover, identity page, revision table, Header grid, page geometry, typography, table language, TOC/list bars, numbering and captions are Golden-Master structures.

## Required resources

Before generation or audit, read:

- `references/GOLDEN_MASTER_SPEC.md`
- `references/REPORT_RULES.yaml`
- `references/STYLE_MAP.yaml`
- `references/METADATA_SCHEMA.yaml`
- `references/QA_CHECKLIST.md`
- exactly one primary profile under `references/profiles/` when the report type is known

## Immutable assets

- `assets/HRT_Master_Report_V3_2_4_REFERENCE.docx` — automation Golden Master.
- `assets/HRT_Master_Report_V3_2_4.dotx` — manual Microsoft Word template.

Never overwrite either asset. Always create a report-specific DOCX.

## Fidelity constraints — non-negotiable

### 1. Front matter is clone-and-populate

For ordinary HRT output:

- Copy the reference DOCX.
- Populate metadata in the existing cover shapes and identity/revision cells.
- Preserve object positions, sizes, margins, merges, borders, fills and page geometry.
- Replace logos only in dedicated image slots; never replace a missing logo with text.
- If a logo is unavailable, leave the slot blank.

Do not rebuild the cover, identity page, revision table or Header from scratch.

### 2. Persian body typography

Main Persian prose:

- style: `Textbody_RYM`
- Persian font: **B Nazanin**
- size: **12 pt**
- RTL: true
- justified
- line spacing: 1.15
- first-line indent: Golden Master value (~0.55 cm)

A Persian run must be marked RTL/complex-script so Microsoft Word actually uses B Nazanin. Do not rely on right alignment or style name alone. Use `scripts/word_primitives.py` for newly generated content.

Latin/English runs inside Persian prose use Times New Roman and should be split from Persian runs when needed.

### 3. Header fidelity

The body Header is the Golden-Master three-column, three-row table. Do not recreate it.

- Header table: true RTL (`w:bidiVisual`)
- Persian project title: B Nazanin 14 pt bold
- Persian report/stage line: B Nazanin 11 pt
- authorized classification only: red, B Nazanin 11 pt bold
- report code: Times New Roman 10 pt bold
- issue date: B Nazanin 10 pt
- PAGE / NUMPAGES remain Word fields
- Footer remains empty by default

### 4. Tables require structural AND semantic RTL

Right-aligning cell text is not RTL.

Every Persian table must contain `w:tblPr/w:bidiVisual` **and** the XML cell order must follow the Persian logical order so the first logical column appears on the visual right in Microsoft Word.

Examples:

- a standard table with `ردیف` must store `ردیف` as the first logical/XML Header cell;
- the identity table must place semantic labels such as `عنوان پروژه` on the Persian right side;
- imported legacy tables with reversed cell order must be normalized before release.

For **all report-body/content table cells** (including identity and revision tables; excluding the page Header table):

- first logical column = right-most visual column
- font: **B Nazanin**
- size: **11 pt**
- Header: B Nazanin 11 pt bold, black, `#D9D9D9`
- all cell content: horizontal center + vertical center
- thin black borders
- repeat Header row where appropriate

For the revision-history table, semantic RTL is fixed as:

- right-most / first XML cell: `شرح/وضعیت`
- middle: `کارشناسان/ افراد`
- left-most: `تاریخ`

Rows such as `تدوین نسخه اول/دوم/سوم`، `تأییدیه` and `ویراستاری` must therefore be stored in the first XML cell.

Use semantic-RTL helpers from `scripts/word_primitives.py` instead of manually swapping alignments.

### 5. Bullets are Word numbering

Never type `•`, `` or other bullet glyphs.

Use Golden-Master bullet numbering (`numId 11`, level 0) with `Textbody_RYM`. Bullet and hanging indent must remain on the Persian/right side.

### 6. Headings: no decorative highlight

- Level 1: `Title1_RYM` — 16 pt
- Level 2: `Title2_RYM` — 15 pt
- Level 3: `Title3_RYM` — 14 pt
- Level 4: `Title4_RYM` — 13 pt
- Level 5: `Title5_RYM` — 12 pt

`Title2_RYM` has **no gray fill/highlight** by default.

Use one Golden-Master multilevel list:

- Level 1: `%1-`
- Level 2: `%1-%2-`
- Level 3: `%1-%2-%3-`

**V3.2.3 regression rule:** the multilevel-numbering definitions are plain. Do **not** insert LRM, RLM or any other Unicode direction-control character into `numbering.xml` / `w:lvlText`. The approved heading numbering inside the body must remain unchanged.

Do not type heading numbers or hyphens manually.

### 7. TOC, lists, captions and references are Word-native

Use real Word fields:

- TOC
- List of Tables by caption label `جدول`
- List of Images by caption label `تصویر`
- `SEQ جدول`
- `SEQ تصویر`
- bookmark + `REF`
- PAGE / NUMPAGES

The TOC is RTL. Heading number plus trailing hyphen must appear on the right of the title, Dot Leader must lead toward the page number on the left. Do not construct TOC rows manually.

**TOC-only BiDi rule:** solve TOC direction/layout through TOC paragraph/style/tab/field behavior only. Never change the approved body multilevel numbering to fix the TOC.

TOC and list typography is fixed:

- `TOC 1`: B Nazanin 12 pt, bold
- `TOC 2`: B Nazanin 12 pt, regular
- `TOC 3`: B Nazanin 12 pt, regular
- `Table of Figures` / lists of tables and images: B Nazanin 11 pt, regular
- the bars `فهرست مطالب`، `فهرست جدولها/جداول` and `فهرست تصاویر`: B Nazanin 12 pt bold
- B Titr or theme-derived fonts are forbidden in TOC/list rows.

No LRM/RLM is required or permitted in the approved heading-numbering patterns.

### 8. Dynamic output naming — mandatory

Never save a finished artifact with a generic fixed name such as `output.docx`, `HRT_Report.docx`, `final.docx`, or `HRT_Master_Report_Output.docx`.

Derive the filename from the user request and resolved project metadata using this canonical pattern:

`HRT_[Domain]_[DocumentType]_[ProjectName]_[OptionalScope]_[OptionalRevision].ext`

Rules:

- Prefix is always `HRT`.
- `Domain` describes the substantive domain when useful, e.g. `PassiveDefense`, `FS`, `PFS`, `Investment`, `UrbanPlanning`, or `Management`. For a cross-domain proposal, use the actual underlying domain, not `Proposal` twice.
- `DocumentType` describes the artifact, e.g. `Proposal`, `Report`, `Study`, `ManagementReport`, or another human-readable type.
- `ProjectName` is mandatory. Prefer the official English project/company name found in the source documents. Do not invent a transliteration when the official English name is unknown; a safe Persian Unicode project name is preferable to a guessed Latin spelling.
- Add `Scope` only when the user asks for a subset such as `Chapter01`, `ExecutiveSummary`, or `Volume02`.
- Add `Revision` only when explicitly known, e.g. `R01`.
- Use `_` as the separator. Remove Windows-invalid filename characters and collapse repeated separators.
- DOCX and PDF variants of the same deliverable must use the same basename.
- If the user explicitly supplies a filename, use it unless it violates filesystem safety; user-supplied naming overrides the automatic pattern.

Approved examples:

- Full Eurasia passive-defense proposal: `HRT_PassiveDefense_Proposal_Eurasia.docx`
- Chapter 1 only: `HRT_PassiveDefense_Proposal_Eurasia_Chapter01.docx`
- FS report: `HRT_FS_Report_[ProjectName].docx`
- Management report: `HRT_Management_Report_Dogharoun.docx`

Use `scripts/output_naming.py` to normalize and validate the final filename before delivery.

### 9. Client template precedence

If the client supplies a mandatory official template, it has priority over the HRT visual layer. Preserve HRT analytical and QA logic where compatible.

## Analytical workflow

1. Establish report identity and primary profile.
2. Resolve the dynamic output filename from domain, document type, project name, optional scope and revision.
3. Extract evidence before conclusions.
4. Keep documented fact, expert analysis and consultant recommendation distinct.
5. Use the primary profile for content architecture and domain checks.
6. Copy and populate the Golden Master.
7. Generate new content only with approved Word primitives.
8. Run structural QA and filename validation.
9. Render the full DOCX and inspect every page.
10. Before final Microsoft Word release, update fields with `Ctrl+A` then `F9`.

## Recommended tooling

Resolve the output filename:

```bash
python scripts/output_naming.py \
  --domain PassiveDefense \
  --document-type Proposal \
  --project-name Eurasia \
  --ext docx
```

Populate metadata:

```bash
python scripts/populate_metadata.py \
  assets/HRT_Master_Report_V3_2_4_REFERENCE.docx \
  output.docx --metadata-json metadata.json
```

Insert logos without changing geometry:

```bash
python scripts/insert_logos.py output.docx output-with-logos.docx \
  --client-logo client.png --consultant-logo consultant.png
```

Generate content using:

`scripts/word_primitives.py`

Then QA:

```bash
python scripts/hrt_qa.py output.docx --mode report --json qa.json
```

Do not release while QA reports any of the following:

- table missing structural RTL;
- semantic right-most column failure;
- table font or size not B Nazanin 11;
- table cell not horizontally/vertically centered;
- Persian body run font/script failure;
- typed bullet;
- `Title2_RYM` shading/highlight;
- heading hierarchy/numbering mismatch;
- direction marks inside heading numbering;
- missing TOC/list/caption fields;
- legacy Header contamination;
- unresolved metadata tokens;
- visible render defect.

## Short invocation aliases — explicit trigger vocabulary

The user does **not** need to type `@` or `$`. When a report/document request contains one of the following aliases, treat it as an explicit request to use this skill:

- `HRT`
- `HRT Master`
- `HRT Report`
- `قالب HRT`
- `گزارش HRT`
- `HRT Master Report`
- `HRT Master V3.2.3`
- legacy: `HR Master Report`

Examples that must invoke this skill:

- `HRT این گزارش را تهیه کن.`
- `HRT Report فصل اول پروپوزال اوراسیا را بساز.`
- `HRT Master گزارش FS را آماده کن.`
- `این فایل را با قالب HRT اصلاح کن.`

If the user writes only `HRT` as a standalone instruction in a report/document context, activate this skill for that task. Do not require the user to repeat the full product name.

## Invocation

Preferred natural invocation (no prefix required):

`HRT گزارش را مطابق قالب اصلی تهیه کن.`

Other short forms: `HRT Master` and `HRT Report`.

Skill identifier, when a surface explicitly supports `$` skill syntax:

`$hrt-master-report`
