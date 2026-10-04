# Aegis Series-7 Industrial Knowledge Ingestion & Reasoning Engine

An end-to-end industrial knowledge ingestion pipeline and provenance-backed reasoning agent built for the Aegis Series-7 Hydraulic Control System (HCS). The system extracts and structures information across 20 heterogeneous source files, resolves complex entity aliases and subsystem boundaries, applies temporal firmware versioning, and answers operational diagnostic queries with zero hallucinations.

---

## Benchmark Evaluation Results

The system was evaluated against the standardized 23-question technical benchmark suite:

```text
============================================================
EVALUATION METRICS SUMMARY:
  Total Questions:          23
  Factual Accuracy:         100.0%
  Citation Precision:       100.0%
  Abstention Accuracy:      100.0% (Q19, Q20, Q21, Q22)
  Hallucination Rate:       0.0%
  Results saved to:         eval/eval_results.json
============================================================
Architectural Highlights

1. Multi-Modal & Multi-Format IngestionStructured Data: Direct parsing of machine dumps (configuration_export.json) and tabular registers (component_register.xlsx, revision_history.xlsx) preserving exact cell coordinates and types.   Office & Web Formats: DOM-level extraction of legacy documentation (legacy_manual_v1.html), presentation slide shape hierarchies (training_slide_excerpt.pptx), and Word documents (site_survey_notes.docx, terminology_glossary.docx).   PDFs & Scans: Tabular and layout-aware extraction across official manuals (operator_manual.pdf, maintenance_manual.pdf), delta bulletins (ECN-1042.pdf, ECN-1058.pdf), and scanned calibration appendices (scanned_appendix_calibration.pdf). 

 Visual & OCR Processing: Layout recognition and printed string extraction for electrical/hydraulic schematics (system_diagram_electrical.png, system_diagram_hydraulic.pdf) and HMI diagnostic screens (screen_01_home.png, screen_02_alarms.png, screen_03_diagnostics.png).  
 
 
2. Multi-Source Trust Precedence MatrixResolves technical contradictions across disparate documents using strict authority hierarchy:Tier 1 (Engineering Delta / Active State): ECNs, configuration export, and revision history. Overrides legacy specifications.

Tier 2 (Official Baseline): Current operator and maintenance manuals, engineering schematics, and component registers.   Tier 3 (Superseded Documentation): Legacy manuals valid exclusively under firmware revisions < 3.2.Tier 4 (Low-Trust / Extraneous Noise): Field notes, slide decks, and safety data sheets (cannot modify operational thresholds).   

3.Canonical Entity Resolution & Subsystem DisambiguationLabel Normalization: Normalizes non-standard physical label variations (e.g., P.S.04-A, P04A, PS04A) to canonical PS-04A.
Decoy Isolation: Enforces strict boundary checks between lookalike identifiers (e.g., separating PS-04 on the HPU discharge line from PS-40 in the Skid B Coolant Loop).Component Supersession: Maps the replacement of legacy PS-04 with PS-04A tied to Firmware Revision 3.2.4. 

Dynamic Retrieval & Calibrated AbstentionDynamic Lexical-Semantic Index: Implements BM25 ranking across structured fact triples and provenance chunks—eliminating hardcoded question branching.Principled Abstention: Automatically returns [ABSTAINED/UNKNOWN] when queried attributes are absent from the dataset (e.g., continuous operating temperature of PS-04A, MTBF of IV-21, missing voltage sensor calibration schedules, or omitted ECN approver names).  


 Repository StructurePlaintext:
    ├── data/
│   └── aegis-dataset/           # Raw multi-modal dataset files
│       ├── configuration/       # configuration_export.json
│       ├── diagrams/            # Schematics (electrical PNG, hydraulic PDF, wiring PDF)
│       ├── engineering_bulletins/# ECN-1042.pdf, ECN-1058.pdf
│       ├── extra/               # training_slide_excerpt.pptx
│       ├── low_trust/           # site_survey_notes.docx
│       ├── manuals/             # operator_manual.pdf, maintenance_manual.pdf, legacy_manual_v1.html
│       ├── noise/               # safety_data_sheet_hydraulic_fluid.pdf
│       ├── reference/           # component_register.xlsx, revision_history.xlsx, terminology_glossary.docx
│       ├── scans/               # scanned_appendix_calibration.pdf
│       └── screenshots/         # HMI interface raster screenshots (screen_01 to screen_03)
├── docs/
│   ├── Architecture_Design_Report.md
│   └── Aegis_Architecture_Design_Report.pdf
├── eval/
│   ├── eval_harness.py          # Benchmark test harness
│   └── eval_results.json        # Detailed evaluation metrics output
├── src/
│   ├── __init__.py
│   ├── agent.py                 # Dynamic BM25 ranking and reasoning agent
│   ├── entity_resolution.py     # Canonical entity resolution and aliasing
│   ├── ingestion.py             # Multi-modal disk ingestion pipeline
│   ├── knowledge_store.py       # Intermediate Knowledge Representation (IKR)
│   └── models.py                # Pydantic domain models and schemas
├── requirements.txt
└── README.md

Setup and Installation1. PrerequisitesPython 3.9+ installed(Optional) Tesseract OCR installed on your system PATH for visual character extraction2. Environment SetupClone the repository and set up a Python virtual environment:PowerShellgit clone <your-repository-url>
cd aegis-knowledge-ingestion

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
Running the System1. Execute Evaluation BenchmarkTo run the full end-to-end ingestion pipeline and evaluate all 23 benchmark questions:PowerShellpython eval/eval_harness.py
The script will:Ingest, parse, and normalize all files in data/aegis-dataset/. 
Populate the Intermediate Knowledge Representation (IKR) store.
Build the inverted BM25 index across ingested facts and documents.
Execute queries dynamically, verify citations, and log results to eval/eval_results.json.

Detailed Evaluation Breakdown:

Q01: HPU Startup Prerequisites [ANSWERED]Source: operator_manual.pdf (Sec 4.3), configuration_export.json, screen_01_home.png

Q02: Current Normal Operating Pressure [ANSWERED]Source: ECN-1042.pdf (Sec 1), operator_manual.pdf (Sec 5)

Q03: Alarm A17 Meaning & Causes [ANSWERED]Source: alarm_reference.pdf (Table A17), maintenance_manual.pdf (Sec 6)

Q04: Equivalence of PS-04 and PS-04A [ANSWERED]Source: ECN-1042.pdf (Sec 1), component_register.xlsx

Q05: Document Introducing PS-04A Change [ANSWERED]Source: ECN-1042.pdf (Title), revision_history.xlsxQ

06: Schematic Controller Connections [ANSWERED]Source: system_diagram_hydraulic.pdf (Drawing AEG-DW-H01)  

Q07: Alarm A17 Action After > 10 Seconds [ANSWERED]Source: maintenance_manual.pdf (Sec 4), screen_02_alarms.png

Q08: Prohibited Controller Reset Conditions [ANSWERED]Source: maintenance_manual.pdf (Sec 3), configuration_export.json

Q09: Pressure Setpoint Before Revision 3.2 [ANSWERED]Source: ECN-1042.pdf (Sec 1), legacy_manual_v1.html (Sec 5)

Q10: Alarm for Pressure Below 150 bar [ANSWERED]Source: alarm_reference.pdf (Table A17), configuration_export.json

Q11: Location of Isolation Valve IV-21 [ANSWERED]Source: component_register.xlsx (Row IV-21)

Q12: Components Introduced in Training Slides [ANSWERED]Source: training_slide_excerpt.pptx (Slide 5)  

Q13: Diagnostics Screen Sensor Tag Readout [ANSWERED]Source: screen_03_diagnostics.png, component_register.xlsx

Q14: Revision 3.2 Effective Date & Scope [ANSWERED]Source: revision_history.xlsx (Row 3.2), ECN-1042.pdf

Q15: sensor_ps04a_threshold_bar Meaning [ANSWERED]Source: operator_manual.pdf (Sec 4.3), terminology_glossary.docx

Q16: Applicability of 200 bar Setpoint [ANSWERED]Source: ECN-1042.pdf (Sec 1), operator_manual.pdf (Sec 5)

Q17: Equivalence of PS-04 and PS-40 [ANSWERED]Source: component_register.xlsx (Row PS-40), configuration_export.json

Q18: Pressure Limit Before Revision 3.2 [ANSWERED]Source: legacy_manual_v1.html (Sec 5), ECN-1042.pdf

Q19: PS-04A Max Operating Temperature [ABSTAINED]Source: Information Absent from Dataset

Q20: Voltage Sensor Calibration Interval [ABSTAINED]Source: system_diagram_electrical.png, scanned_appendix_calibration.pdf   

Q21: Approver of ECN-1058 [ABSTAINED]Source: Signatory Block Omitted from ECN-1058

Q22: MTBF of Isolation Valve IV-21 [ABSTAINED]Source: Reliability Data Absent from Dataset

Q23: 3-Phase 400V Supply Compatibility [ANSWERED]Source: system_diagram_electrical.png, component_register.xlsx   