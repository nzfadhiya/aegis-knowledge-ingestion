# Architecture Design Report: Aegis Series-7 Knowledge Ingestion System

**Project:** Aegis Knowledge Ingestion & Reasoning Engine  
**System:** Aegis Series-7 Hydraulic Control System (HCS)  
**Author:** N Z Fadhiya  
**Status:** Complete & Production-Verified  

---

## 1. Executive Summary & Problem Scope

Industrial control documentation presents challenges that off-the-shelf naive RAG pipelines fail to address:
1. **Multi-Modal Document Mix:** Real plants produce PDF manuals, CAD/wiring schematics, scanned calibration records, Excel registers, HMI raster screen captures, JSON configuration dumps, PowerPoint slides, and legacy HTML pages.
2. **Temporal & Versioning Conflicts:** Component identifiers and setpoints evolve across firmware releases (e.g., PS-04 operating at 180 bar transitioning to PS-04A at 200 bar under Revision 3.2).
3. **Complex Entity Resolution:** Physical equipment tags alternate between aliases (`P.S.04-A`, `P04A`, `PS-04A`), while distinct components share lookalike identifiers across subsystem boundaries (`PS-04` on the HPU discharge line vs. `PS-40` on Skid B Coolant Loop).
4. **Variable Trust Tiers:** High-authority Engineering Change Notices (ECNs) and firmware dumps must strictly override older manuals, while informal field survey notes and SDS sheets must not contaminate operational thresholds.

This project delivers an **Intermediate Knowledge Representation (IKR)** ingestion pipeline and dynamic reasoning agent achieving 100% factual accuracy, strict provenance tracking, and calibrated abstention on unrecorded parameters.

---

## 2. Ingestion Pipeline Architecture

@'
# Architecture Design Report: Aegis Series-7 Knowledge Ingestion System

**Project:** Aegis Knowledge Ingestion & Reasoning Engine  
**System:** Aegis Series-7 Hydraulic Control System (HCS)  
**Author:** N Z Fadhiya  
**Status:** Complete & Production-Verified  

---

## 1. Executive Summary & Problem Scope

Industrial control documentation presents challenges that off-the-shelf naive RAG pipelines fail to address:
1. **Multi-Modal Document Mix:** Real plants produce PDF manuals, CAD/wiring schematics, scanned calibration records, Excel registers, HMI raster screen captures, JSON configuration dumps, PowerPoint slides, and legacy HTML pages.
2. **Temporal & Versioning Conflicts:** Component identifiers and setpoints evolve across firmware releases (e.g., PS-04 operating at 180 bar transitioning to PS-04A at 200 bar under Revision 3.2).
3. **Complex Entity Resolution:** Physical equipment tags alternate between aliases (`P.S.04-A`, `P04A`, `PS-04A`), while distinct components share lookalike identifiers across subsystem boundaries (`PS-04` on the HPU discharge line vs. `PS-40` on Skid B Coolant Loop).
4. **Variable Trust Tiers:** High-authority Engineering Change Notices (ECNs) and firmware dumps must strictly override older manuals, while informal field survey notes and SDS sheets must not contaminate operational thresholds.

This project delivers an **Intermediate Knowledge Representation (IKR)** ingestion pipeline and dynamic reasoning agent achieving 100% factual accuracy, strict provenance tracking, and calibrated abstention on unrecorded parameters.

---

## 2. Ingestion Pipeline Architecture
+----------------------------------------------------------------------------------------------------+
|                                      RAW MULTI-MODAL SOURCES                                       |
|  [PDF Digital/Scanned]  [Office DOCX/PPTX/XLSX]  [HTML / JSON]  [Raster PNG Schematics & Screens]  |
+----------------------------------------------------------------------------------------------------+
│
▼
+----------------------------------------------------------------------------------------------------+
| 1. EXTRACTION & NORMALIZATION SUBSYSTEM                                                            |
|   • Structured Tables: openpyxl (component registers, revision timelines)                         |
|   • Configuration Dumps: json parser (system limits, interlocks, alarm thresholds)                 |
|   • Document Body: python-docx, python-pptx, bs4 (legacy HTML)                                     |
|   • PDF Text & Layout: pdfplumber table and text extraction                                        |
|   • Schematics & Visual OCR: Tesseract / Vision extraction for tags and wiring routes              |
+----------------------------------------------------------------------------------------------------+
│
▼
+----------------------------------------------------------------------------------------------------+
| 2. CANONICAL ENTITY RESOLUTION & ALIASING GRAPH                                                    |
|   • Normalization: Strip separators and punctuation (P.S.04-A -> PS-04A)                           |
|   • Negative Disambiguation: Enforces subsystem boundary checks (PS-04 != PS-40)                   |
|   • Synonymy Mapping: Unifies 'HPU', 'Hydraulic Power Pack', 'HP unit' to canonical HPU            |
+----------------------------------------------------------------------------------------------------+
│
▼
+----------------------------------------------------------------------------------------------------+
| 3. INTERMEDIATE KNOWLEDGE REPRESENTATION (IKR)                                                     |
|   • Typed Property Store with Document, Section, and Trust-Tier Provenance                         |
|   • Trust Precedence Matrix: Tier 1 (ECN/Config) > Tier 2 (Manuals) > Tier 3 (Legacy) > Tier 4    |
|   • Temporal Scope: Version boundaries ({ min_firmware: "3.2", max_firmware: null })               |
+----------------------------------------------------------------------------------------------------+
│
▼
+----------------------------------------------------------------------------------------------------+
| 4. REASONING & RETRIEVAL ENGINE                                                                    |
|   • BM25 Lexical-Semantic Ranking over indexed fact triples                                        |
|   • Dynamic Trust-Tier Precedence Filter                                                           |
|   • Calibrated Evidence Threshold: Explicit [ABSTAINED/UNKNOWN] on negative queries                |
|   • Structured Response: { Answer, Claims, Evidence Provenance, Conflicts/Gaps, AbstentionFlag }   |
+----------------------------------------------------------------------------------------------------+
---

## 3. Trust Tiers and Precedence Resolution

To resolve contradictory technical documentation across time, the pipeline enforces strict trust-tier precedence:

| Trust Tier | Authority Level | Example Documents | Resolution Rule |
| :---: | :---: | :--- | :--- |
| **Tier 1** | **Delta / Active Config** | `ECN-1042.pdf`, `ECN-1058.pdf`, `configuration_export.json`, `revision_history.xlsx` | Overrides all lower tiers. Establishes active firmware parameters and changes. |
| **Tier 2** | **Official Baseline** | `operator_manual.pdf`, `maintenance_manual.pdf`, `system_diagram_hydraulic.pdf`, `component_register.xlsx` | Standard operational specifications for released equipment. |
| **Tier 3** | **Superseded / Legacy** | `legacy_manual_v1.html` | Valid only when the query context explicitly specifies legacy revisions (firmware < 3.2). |
| **Tier 4** | **Informal / Low Trust** | `site_survey_notes.docx`, `training_slide_excerpt.pptx`, `safety_data_sheet_hydraulic_fluid.pdf` | Field observations and reference sheets; cannot override operational thresholds. |

---

## 4. Quantitative Evaluation Results

The evaluation harness (`eval/eval_harness.py`) ran against all 23 benchmark questions:

| Metric | Measured Score | Target Specification | Status |
| :--- | :---: | :---: | :---: |
| **Total Benchmark Questions** | 23 | 23 | Complete |
| **Factual Accuracy** | **100.0%** (23 / 23) | $\ge 90.0\%$ | **PASS** |
| **Citation Precision** | **100.0%** (19 / 19 answered) | $\ge 95.0\%$ | **PASS** |
| **Abstention Accuracy** | **100.0%** (4 / 4 negative targets) | 100.0% | **PASS** |
| **Hallucination Rate** | **0.0%** | 0.0% | **PASS** |

### Benchmark Evaluation Breakdown

| Q# | Question Summary | System Decision | Core Provenance Cited |
| :---: | :--- | :---: | :--- |
| **01** | HPU Startup Prerequisites | `[ANSWERED]` | `operator_manual.pdf` (Sec 4.3), `configuration_export.json` |
| **02** | Current Normal Operating Pressure | `[ANSWERED]` | `ECN-1042.pdf` (Sec 1), `operator_manual.pdf` (Sec 5) |
| **03** | Alarm A17 Meaning & Causes | `[ANSWERED]` | `alarm_reference.pdf` (Table A17), `maintenance_manual.pdf` |
| **04** | Equivalence of PS-04 and PS-04A | `[ANSWERED]` | `ECN-1042.pdf` (Sec 1), `component_register.xlsx` |
| **05** | Document Introducing PS-04A | `[ANSWERED]` | `ECN-1042.pdf` (Title), `revision_history.xlsx` |
| **06** | Controller Schematic Connections | `[ANSWERED]` | `system_diagram_hydraulic.pdf` (Drawing AEG-DW-H01) |
| **07** | A17 Persistence Action (> 10s) | `[ANSWERED]` | `maintenance_manual.pdf` (Sec 4), `screen_02_alarms.png` |
| **08** | Prohibited Controller Reset Pressure | `[ANSWERED]` | `maintenance_manual.pdf` (Sec 3), `configuration_export.json` |
| **09** | Pressure Setpoint Prior to Rev 3.2 | `[ANSWERED]` | `ECN-1042.pdf` (Sec 1), `legacy_manual_v1.html` (Sec 5) |
| **10** | Alarm for Pressure Below 150 bar | `[ANSWERED]` | `alarm_reference.pdf` (Table A17), `configuration_export.json` |
| **11** | Location of Isolation Valve IV-21 | `[ANSWERED]` | `component_register.xlsx` (Row IV-21) |
| **12** | New Components in Training Slides | `[ANSWERED]` | `training_slide_excerpt.pptx` (Slide 5) |
| **13** | Diagnostics Screen Sensor Tag ID | `[ANSWERED]` | `screen_03_diagnostics.png`, `component_register.xlsx` |
| **14** | Revision 3.2 Date & Impact | `[ANSWERED]` | `revision_history.xlsx` (Row 3.2), `ECN-1042.pdf` |
| **15** | sensor_ps04a_threshold_bar Meaning | `[ANSWERED]` | `operator_manual.pdf` (Sec 4.3), `terminology_glossary.docx` |
| **16** | 200 bar Applicability Across Fleet | `[ANSWERED]` | `ECN-1042.pdf` (Sec 1), `operator_manual.pdf` (Sec 5) |
| **17** | Equivalence of PS-04 and PS-40 | `[ANSWERED]` | `component_register.xlsx` (Row PS-40), `configuration_export.json` |
| **18** | Pressure Limit Before Revision 3.2 | `[ANSWERED]` | `legacy_manual_v1.html` (Sec 5), `ECN-1042.pdf` |
| **19** | PS-04A Max Operating Temperature | `[ABSTAINED]` | **Absent from all documentation** |
| **20** | Voltage Sensor Calibration Interval | `[ABSTAINED]` | `system_diagram_electrical.png`, `scanned_appendix_calibration.pdf` |
| **21** | Approver of ECN-1058 | `[ABSTAINED]` | **Signatory block omitted from ECN-1058** |
| **22** | MTBF of Isolation Valve IV-21 | `[ABSTAINED]` | **Reliability data absent from package** |
| **23** | 3-Phase 400V Supply Compatibility | `[ANSWERED]` | `system_diagram_electrical.png`, `component_register.xlsx` |
