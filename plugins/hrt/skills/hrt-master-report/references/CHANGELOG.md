## 3.2.4 — Dynamic Output Naming Patch

- Added mandatory request-aware output filenames using `HRT_[Domain]_[DocumentType]_[ProjectName]_[OptionalScope]_[OptionalRevision].ext`.
- Added deterministic filename normalization/validation helper.
- Preserved the approved V3.2.3 Word Golden Master, numbering, TOC, RTL, typography and table rules byte-for-byte.
- Added deployment-oriented naming metadata for the future HRT App while keeping the Skill independently installable.

## 3.2.3 — Numbering Regression Fix

- Restored approved plain heading-number patterns `%1-`, `%1-%2-`, `%1-%2-%3-`.
- Removed LRM/RLM/direction marks from `numbering.xml`; body numbering is no longer changed to solve TOC direction.
- Limited BiDi correction to the TOC layer.
- Locked all table cell content to B Nazanin 11 pt.
- Preserved centered cells, semantic RTL, corrected revision-history order, B Nazanin 12 body, and HRT short aliases.


## 3.2.1 — Short invocation alias patch

- Added natural invocation aliases: `HRT`, `HRT Master`, `HRT Report`, `قالب HRT`, and `گزارش HRT`.
- Explicitly states that `@` or `$` prefixes are not required for natural-language invocation.
- Kept all V3.2 Golden Master, semantic RTL, typography, numbering and QA rules unchanged.

# HRT Master Report Changelog

## 3.2.0

- Added semantic RTL table rule in addition to `w:bidiVisual`.
- Normalized identity-table column semantics so labels render on the Persian right.
- Removed default shading from `Title2_RYM`.
- Unified heading levels 1–3 under one multilevel numbering definition.
- Locked numbering patterns to `1-`, `1-1-`, `1-1-1-` equivalents.
- Strengthened TOC/field rules for Persian BiDi ordering.
- Strengthened QA for semantic RTL, H2 shading and heading numbering.

## 3.1.0

- Fidelity patch for Golden-Master front matter, B Nazanin complex-script runs, true RTL tables, Word bullets and Header fidelity.


## 3.2.2 — RTL & TOC Fidelity Patch
- Replaced TOC1 B Titr inheritance with B Nazanin; normalized TOC2/3 and Table of Figures fonts.
- Added LRM boundaries to heading-number patterns to preserve `۱-` / `۱-۱-` visual order in Persian RTL TOC output.
- Enforced horizontal and vertical center alignment for all table cell content.
- Corrected revision-history semantic RTL order so status/description is the right-most column.
- Extended QA for TOC/list fonts, table centering, directional marks and revision-history schema.
