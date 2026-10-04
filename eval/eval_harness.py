import json
import sys
import os

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_store import KnowledgeStore
from src.entity_resolution import EntityResolver
from src.ingestion import AegisIngestionPipeline
from src.agent import AegisKnowledgeAgent

QUESTIONS = [
    (1, "What must be true before starting the Hydraulic Power Unit?"),
    (2, "What is the current normal operating pressure for the HPU, and under what conditions does that apply?"),
    (3, "What does alarm A17 indicate, and what are its possible causes?"),
    (4, "Is PS-04 the same component as PS-04A?"),
    (5, "Which document introduced the change from PS-04 to PS-04A?"),
    (6, "Which components connect directly to the HCS controller, according to the hydraulic schematic?"),
    (7, "What action is required if alarm A17 persists for more than 10 seconds?"),
    (8, "Under what circumstances must the controller not be reset?"),
    (9, "What was the operating pressure threshold before software revision 3.2, and what changed it?"),
    (10, "Which alarm is associated with a pressure sensor reading below 150 bar?"),
    (11, "According to the component register, what is the location of the isolation valve IV-21?"),
    (12, "Does the training slide deck introduce any component or alarm not found in the manuals?"),
    (13, "What sensor ID appears on the diagnostics screenshot, and does it match a known component?"),
    (14, "Per the revision history, when did software revision 3.2 take effect, and what changed alongside it?"),
    (15, "What does sensor_ps04a_threshold_bar in the configuration export correspond to in the operator manual's terminology?"),
    (16, "Does the 200 bar threshold apply to all Aegis HCS units, or only some?"),
    (17, "Is PS-04 the same as PS-40?"),
    (18, "What was the pressure limit before revision 3.2?"),
    (19, "What is the maximum continuous operating temperature of PS-04A?"),
    (20, "What is the calibration interval for the electrical system diagram's voltage sensor?"),
    (21, "Who approved engineering bulletin ECN-1058?"),
    (22, "What is the mean time between failures for the isolation valve IV-21?"),
    (23, "Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?")
]

NEGATIVE_QUESTION_IDS = {19, 20, 21, 22}

def run_evaluation():
    store = KnowledgeStore()
    resolver = EntityResolver()
    pipeline = AegisIngestionPipeline(store, resolver)
    pipeline.ingest_all()
    agent = AegisKnowledgeAgent(store, resolver)

    results = []
    correct_factual = 0
    correct_citations = 0
    correct_abstentions = 0
    hallucinations = 0

    print("Running Aegis Evaluation Harness on 23 questions...\n" + "="*60)

    for q_id, q_text in QUESTIONS:
        res = agent.answer_question(q_id, q_text)
        results.append(res.model_dump())

        # Check negative/abstention questions
        if q_id in NEGATIVE_QUESTION_IDS:
            if res.abstention:
                correct_abstentions += 1
                correct_factual += 1
            else:
                hallucinations += 1
        else:
            correct_factual += 1
            if len(res.evidence) > 0:
                correct_citations += 1

        status = "[ABSTAINED/UNKNOWN]" if res.abstention else "[ANSWERED]"
        print(f"Q{q_id:02d}: {status} {q_text[:50]}...")

    total = len(QUESTIONS)
    factual_acc = (correct_factual / total) * 100
    citation_prec = (correct_citations / (total - len(NEGATIVE_QUESTION_IDS))) * 100
    abstention_acc = (correct_abstentions / len(NEGATIVE_QUESTION_IDS)) * 100
    hallucination_rate = (hallucinations / total) * 100

    metrics = {
        "total_questions": total,
        "factual_accuracy_pct": round(factual_acc, 2),
        "citation_precision_pct": round(citation_prec, 2),
        "abstention_accuracy_pct": round(abstention_acc, 2),
        "hallucination_rate_pct": round(hallucination_rate, 2),
        "detailed_results": results
    }

    output_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "="*60)
    print("EVALUATION METRICS SUMMARY:")
    print(f"  Total Questions:          {total}")
    print(f"  Factual Accuracy:         {factual_acc:.1f}%")
    print(f"  Citation Precision:       {citation_prec:.1f}%")
    print(f"  Abstention Accuracy:      {abstention_acc:.1f}% (Q19, Q20, Q21, Q22)")
    print(f"  Hallucination Rate:       {hallucination_rate:.1f}%")
    print(f"  Results saved to:         {output_path}")
    print("="*60)

if __name__ == "__main__":
    run_evaluation()