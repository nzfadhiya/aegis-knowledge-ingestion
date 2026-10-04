import os
import json
import openpyxl
from bs4 import BeautifulSoup
import docx
from pptx import Presentation
import pdfplumber
from PIL import Image

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

from src.models import Entity, Fact, Provenance, TrustTier, VersionScope
from src.knowledge_store import KnowledgeStore
from src.entity_resolution import EntityResolver

class AegisIngestionPipeline:
    def __init__(self, store: KnowledgeStore, resolver: EntityResolver, base_dir: str = "data/aegis-dataset"):
        self.store = store
        self.resolver = resolver
        self.base_dir = base_dir

    def _get_path(self, *parts):
        return os.path.join(self.base_dir, *parts)

    def ingest_all(self):
        """Discovers, parses, and indexes every file directly from disk."""
        self._parse_configuration_json()
        self._parse_excel_files()
        self._parse_word_documents()
        self._parse_powerpoint_slides()
        self._parse_html_manuals()
        self._parse_pdf_documents()
        self._parse_images_and_screenshots()

    def _parse_configuration_json(self):
        path = self._get_path("configuration", "configuration_export.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.store.configuration = data
        source = "configuration_export.json"

        # Dynamically index all key-values
        for section, content in data.items():
            if isinstance(content, dict):
                for key, val in content.items():
                    self.store.add_fact(Fact(
                        subject=section.upper(),
                        predicate=key,
                        value=val,
                        provenance=Provenance(source_document=source, section_or_location=f"{section}.{key}", trust_tier=TrustTier.TIER_1_DELTA)
                    ))

    def _parse_excel_files(self):
        # 1. Component Register
        cr_path = self._get_path("reference", "component_register.xlsx")
        if os.path.exists(cr_path) and os.path.getsize(cr_path) > 0:
            wb = openpyxl.load_workbook(cr_path, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if len(rows) > 1:
                for row in rows[1:]:
                    if not row or not row[0]:
                        continue
                    cid = str(row[0]).strip()
                    cname = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                    raw_aliases = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                    aliases = [a.strip() for a in raw_aliases.split(";") if a.strip()]
                    loc = str(row[3]).strip() if len(row) > 3 and row[3] else ""
                    stat = str(row[4]).strip() if len(row) > 4 and row[4] else "Active"
                    notes = str(row[5]).strip() if len(row) > 5 and row[5] else ""

                    self.store.register_entity(Entity(
                        canonical_id=cid, common_name=cname, aliases=aliases, location=loc, status=stat, notes=notes
                    ))
                    self.store.add_fact(Fact(
                        subject=cid, predicate="location", value=loc,
                        provenance=Provenance(source_document="component_register.xlsx", section_or_location=f"Row {cid}", trust_tier=TrustTier.TIER_2_OFFICIAL)
                    ))
                    if notes:
                        self.store.add_fact(Fact(
                            subject=cid, predicate="notes", value=notes,
                            provenance=Provenance(source_document="component_register.xlsx", section_or_location=f"Row {cid}", trust_tier=TrustTier.TIER_2_OFFICIAL)
                        ))

        # 2. Revision History
        rh_path = self._get_path("reference", "revision_history.xlsx")
        if os.path.exists(rh_path) and os.path.getsize(rh_path) > 0:
            wb = openpyxl.load_workbook(rh_path, data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if len(rows) > 1:
                for row in rows[1:]:
                    if not row or not row[0]:
                        continue
                    rev_dict = {
                        "rev": str(row[0]).strip(),
                        "date": str(row[1]).strip() if len(row) > 1 and row[1] else "",
                        "changes": str(row[2]).strip() if len(row) > 2 and row[2] else "",
                        "docs": str(row[3]).strip() if len(row) > 3 and row[3] else ""
                    }
                    self.store.revisions.append(rev_dict)
                    self.store.add_fact(Fact(
                        subject=f"REV_{rev_dict['rev']}", predicate="revision_entry", value=rev_dict,
                        provenance=Provenance(source_document="revision_history.xlsx", section_or_location=f"Rev {rev_dict['rev']}", trust_tier=TrustTier.TIER_1_DELTA)
                    ))

    def _parse_word_documents(self):
        targets = [
            ("reference", "terminology_glossary.docx", TrustTier.TIER_2_OFFICIAL),
            ("low_trust", "site_survey_notes.docx", TrustTier.TIER_4_LOW_TRUST)
        ]
        for folder, fname, tier in targets:
            path = self._get_path(folder, fname)
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                continue
            doc = docx.Document(path)
            full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
            self.store.add_fact(Fact(
                subject=fname, predicate="document_text", value=full_text,
                provenance=Provenance(source_document=fname, section_or_location="Document Body", trust_tier=tier)
            ))

    def _parse_powerpoint_slides(self):
        path = self._get_path("extra", "training_slide_excerpt.pptx")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return
        prs = Presentation(path)
        slides_text = []
        for i, slide in enumerate(prs.slides):
            texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    texts.append(shape.text.strip())
            slides_text.append(f"Slide {i+1}: {' | '.join(texts)}")

        self.store.add_fact(Fact(
            subject="training_slide_excerpt.pptx", predicate="slides_content", value="\n".join(slides_text),
            provenance=Provenance(source_document="training_slide_excerpt.pptx", section_or_location="Slide Content", trust_tier=TrustTier.TIER_4_LOW_TRUST)
        ))

    def _parse_html_manuals(self):
        path = self._get_path("manuals", "legacy_manual_v1.html")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        self.store.add_fact(Fact(
            subject="legacy_manual_v1.html", predicate="document_text", value=soup.get_text(separator="\n"),
            provenance=Provenance(source_document="legacy_manual_v1.html", section_or_location="Full Document", trust_tier=TrustTier.TIER_3_SUPERSEDED)
        ))

    def _parse_pdf_documents(self):
        pdf_targets = [
            ("manuals", "operator_manual.pdf", TrustTier.TIER_2_OFFICIAL),
            ("manuals", "maintenance_manual.pdf", TrustTier.TIER_2_OFFICIAL),
            ("engineering_bulletins", "ECN-1042.pdf", TrustTier.TIER_1_DELTA),
            ("engineering_bulletins", "ECN-1058.pdf", TrustTier.TIER_1_DELTA),
            ("reference", "alarm_reference.pdf", TrustTier.TIER_2_OFFICIAL),
            ("scans", "scanned_appendix_calibration.pdf", TrustTier.TIER_2_OFFICIAL),
            ("diagrams", "system_diagram_hydraulic.pdf", TrustTier.TIER_2_OFFICIAL),
            ("diagrams", "wiring_diagram.pdf", TrustTier.TIER_2_OFFICIAL),
            ("noise", "safety_data_sheet_hydraulic_fluid.pdf", TrustTier.TIER_4_LOW_TRUST)
        ]
        for folder, fname, tier in pdf_targets:
            path = self._get_path(folder, fname)
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                continue
            pages_text = []
            try:
                with pdfplumber.open(path) as pdf:
                    for idx, page in enumerate(pdf.pages):
                        txt = page.extract_text()
                        if txt:
                            pages_text.append(f"[Page {idx+1}] {txt.strip()}")
            except Exception:
                pass

            combined = "\n".join(pages_text)
            self.store.add_fact(Fact(
                subject=fname, predicate="document_text", value=combined,
                provenance=Provenance(source_document=fname, section_or_location="Extracted PDF Text", trust_tier=tier)
            ))

    def _parse_images_and_screenshots(self):
        """Reads real raster images via OCR (or image inspection) from disk."""
        image_targets = [
            ("screenshots", "screen_01_home.png"),
            ("screenshots", "screen_02_alarms.png"),
            ("screenshots", "screen_03_diagnostics.png"),
            ("diagrams", "system_diagram_electrical.png")
        ]
        for folder, fname in image_targets:
            path = self._get_path(folder, fname)
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                continue

            extracted_text = ""
            if HAS_OCR:
                try:
                    img = Image.open(path)
                    extracted_text = pytesseract.image_to_string(img).strip()
                except Exception:
                    extracted_text = ""

            self.store.add_fact(Fact(
                subject=fname,
                predicate="extracted_image_text",
                value=extracted_text,
                provenance=Provenance(source_document=fname, section_or_location="Raster OCR Extracted", trust_tier=TrustTier.TIER_2_OFFICIAL)
            ))