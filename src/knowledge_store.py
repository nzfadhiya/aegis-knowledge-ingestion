from typing import Dict, List, Optional
from src.models import Entity, Fact, TrustTier

class KnowledgeStore:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.facts: List[Fact] = []
        self.alarms: Dict[str, Dict] = {}
        self.configuration: Dict = {}
        self.revisions: List[Dict] = []
        self.startup_interlocks: List[str] = []

    def register_entity(self, entity: Entity):
        self.entities[entity.canonical_id] = entity

    def add_fact(self, fact: Fact):
        self.facts.append(fact)
        if fact.subject in self.entities:
            self.entities[fact.subject].facts.append(fact)

    def get_facts_for(self, subject: str, predicate: Optional[str] = None) -> List[Fact]:
        results = [f for f in self.facts if f.subject == subject]
        if predicate:
            results = [f for f in results if f.predicate == predicate]
        # Sort so Tier 1 overrides lower tiers
        results.sort(key=lambda x: x.provenance.trust_tier)
        return results