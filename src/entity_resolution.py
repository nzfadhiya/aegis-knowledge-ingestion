import re
from typing import Dict, Optional

class EntityResolver:
    def __init__(self):
        # Canonical mapping of aliases to standard component IDs
        self.alias_to_canonical: Dict[str, str] = {
            # HPU
            "hydraulic power unit": "HPU",
            "hpu": "HPU",
            "hp unit": "HPU",
            "hydraulic unit": "HPU",
            "hydraulic power pack": "HPU",
            # PS-04A
            "ps-04a": "PS-04A",
            "ps04a": "PS-04A",
            "p04a": "PS-04A",
            "p.s.04-a": "PS-04A",
            "pressure sensor 04a": "PS-04A",
            "pressure xdcr": "PS-04A",
            # PS-04
            "ps-04": "PS-04",
            "ps04": "PS-04",
            "p04": "PS-04",
            "pressure sensor 04": "PS-04",
            # PS-40 (Negative disambiguation: coolant loop, not HPU)
            "ps-40": "PS-40",
            "ps40": "PS-40",
            "p40": "PS-40",
            "pressure sensor 40": "PS-40",
            # IV-21
            "iv-21": "IV-21",
            "iv21": "IV-21",
            "isolation valve 21": "IV-21",
            "isolation valve": "IV-21",
            "iv-21 solenoid": "IV-21",
            # Controller
            "plc-03": "PLC-03",
            "hcs controller": "PLC-03",
            "aegis controller": "PLC-03"
        }

    def normalize(self, term: str) -> str:
        cleaned = term.strip().lower()
        cleaned = re.sub(r'[\._\s\-]+', '', cleaned)
        return cleaned

    def resolve(self, raw_name: str) -> Optional[str]:
        raw_lower = raw_name.strip().lower()
        if raw_lower in self.alias_to_canonical:
            return self.alias_to_canonical[raw_lower]
        norm = self.normalize(raw_name)
        for alias, canonical in self.alias_to_canonical.items():
            if self.normalize(alias) == norm:
                return canonical
        return None

    def is_same_entity(self, term1: str, term2: str) -> bool:
        c1 = self.resolve(term1)
        c2 = self.resolve(term2)
        if c1 is not None and c2 is not None:
            return c1 == c2
        return False