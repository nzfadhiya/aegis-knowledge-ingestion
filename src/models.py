from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import IntEnum

class TrustTier(IntEnum):
    TIER_1_DELTA = 1      # ECNs, Revisions, Active Configuration JSON
    TIER_2_OFFICIAL = 2   # Current Official Manuals, Schematics, Registers
    TIER_3_SUPERSEDED = 3 # Legacy Manuals (< Rev 3.2)
    TIER_4_LOW_TRUST = 4  # Unverified Notes, Training slides, MSDS Noise

class Provenance(BaseModel):
    source_document: str
    section_or_location: str
    trust_tier: TrustTier
    raw_quote: Optional[str] = None

class VersionScope(BaseModel):
    min_firmware: Optional[str] = None
    max_firmware: Optional[str] = None
    note: Optional[str] = None

class Fact(BaseModel):
    subject: str
    predicate: str
    value: Any
    version_scope: VersionScope = Field(default_factory=VersionScope)
    provenance: Provenance

class Entity(BaseModel):
    canonical_id: str
    common_name: str
    aliases: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    status: str = "Active"
    notes: Optional[str] = None
    facts: List[Fact] = Field(default_factory=list)

class QueryResult(BaseModel):
    question_id: int
    question: str
    answer: str
    claims: List[str]
    evidence: List[Dict[str, Any]]
    conflicts_or_gaps: Optional[str] = None
    abstention: bool = False