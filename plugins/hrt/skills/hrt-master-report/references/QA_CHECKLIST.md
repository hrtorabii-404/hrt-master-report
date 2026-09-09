# HRT Master Report V3.2.3 — QA Checklist

## Golden Master fidelity
- Cover/Header/identity/revision geometry is inherited, not rebuilt.
- Missing logos remain blank image slots.

## Typography
- Body Persian text = B Nazanin 12 pt.
- Header Persian runs = B Nazanin.
- Every visible report-body/content-table run = B Nazanin 11 pt. Header tables follow the separate Header typography rules.

## Tables
- Every Persian table has `w:bidiVisual`.
- Semantic RTL order is correct; `ردیف` is first/right XML cell when present.
- Revision History order = `شرح/وضعیت | کارشناسان/ افراد | تاریخ`.
- Every cell is horizontally and vertically centered.

## Headings and numbering
- Title1/2/3 share the approved multilevel list.
- Patterns are exactly `%1-`, `%1-%2-`, `%1-%2-%3-`.
- No LRM/RLM/Unicode direction-control character appears in `w:lvlText`.
- Title2 has no shading.

## TOC/lists
- TOC is a real Word field.
- TOC1/2/3 = B Nazanin 12; TOC1 bold only.
- Table of Figures = B Nazanin 11.
- Fix TOC direction at TOC style/paragraph/tab/field level only; do not alter heading numbering.

## Bullets/fields
- No typed bullet glyphs.
- Use numId 11 for RTL bullets.
- SEQ/REF/PAGE/NUMPAGES remain Word fields.

## Release
- Run structural QA.
- Render and inspect all pages.
- In Microsoft Word, update fields with Ctrl+A then F9 before final release.
