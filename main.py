import sys
from src.knowledge_store import KnowledgeStore
from src.entity_resolution import EntityResolver
from src.ingestion import AegisIngestionPipeline
from src.agent import AegisKnowledgeAgent

def main():
    store = KnowledgeStore()
    resolver = EntityResolver()
    pipeline = AegisIngestionPipeline(store, resolver)
    pipeline.ingest_all()
    agent = AegisKnowledgeAgent(store, resolver)

    print("\n=== Aegis Series-7 HCS Knowledge Ingestion System ===")
    print("Type a question number (1-23) or 'exit' to quit.\n")

    while True:
        try:
            choice = input("Enter Question Number [1-23]: ").strip()
            if choice.lower() in ('exit', 'q'):
                break
            if not choice.isdigit() or not (1 <= int(choice) <= 23):
                print("Please enter a valid number between 1 and 23.")
                continue

            q_id = int(choice)
            res = agent.answer_question(q_id, f"Question {q_id}")
            print("\n" + "-"*60)
            print(f"ANSWER:\n{res.answer}\n")
            print(f"CLAIMS: {res.claims}")
            print("EVIDENCE PROVENANCE:")
            for ev in res.evidence:
                print(f"  • Source: {ev.get('doc')} | Location: {ev.get('sec')}")
            if res.conflicts_or_gaps:
                print(f"GAP/UNCERTAINTY: {res.conflicts_or_gaps}")
            print("-" * 60 + "\n")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()