import argparse
import csv
import json
from pathlib import Path

from rdflib import Graph, Literal, RDF, XSD

from build_knowledge_graph import BASE_DIR, CUST, build_graph, read_clauses
from semantic_analyzer import analyze_clauses


RELATION_PREDICATES = {
    "Entailment": CUST.entails,
    "Contradiction": CUST.contradicts,
    "Neutral": CUST.relatedTo,
    "Exception": CUST.exceptionTo,
    "Redundancy": CUST.redundantWith,
}


def export_results(results, json_path, csv_path, rdf_path):
    rows = [result.to_dict() for result in results]
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys() if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    graph = build_graph()
    for index, result in enumerate(results, start=1):
        a = CUST[result.clause_a]
        b = CUST[result.clause_b]
        graph.add((a, RELATION_PREDICATES[result.relationship], b))

        analysis = CUST[f"Analysis{index:04d}"]
        graph.add((analysis, RDF.type, CUST.ConsistencyAnalysis))
        graph.add((analysis, CUST.comparesClause, a))
        graph.add((analysis, CUST.comparesClause, b))
        graph.add((analysis, CUST.relationshipType, Literal(result.relationship)))
        graph.add(
            (
                analysis,
                CUST.similarityScore,
                Literal(result.similarity, datatype=XSD.decimal),
            )
        )
        graph.add(
            (
                analysis,
                CUST.confidenceScore,
                Literal(result.confidence, datatype=XSD.decimal),
            )
        )
        graph.add((analysis, CUST.explanation, Literal(result.explanation)))
        graph.add(
            (
                analysis,
                CUST.hierarchyViolation,
                Literal(result.hierarchy_violation, datatype=XSD.boolean),
            )
        )
    graph.serialize(destination=rdf_path, format="turtle")


def main():
    parser = argparse.ArgumentParser(
        description="Run semantic and logical governance consistency analysis."
    )
    parser.add_argument(
        "--neural",
        action="store_true",
        help="Use Sentence-BERT and NLI models. Models may download on first run.",
    )
    parser.add_argument("--threshold", type=float, default=0.2)
    args = parser.parse_args()

    clauses = read_clauses()
    results, embedding_engine, nli_engine = analyze_clauses(
        clauses,
        use_neural=args.neural,
        similarity_threshold=args.threshold,
    )
    export_results(
        results,
        BASE_DIR / "relationship_report.json",
        BASE_DIR / "relationship_report.csv",
        BASE_DIR / "analyzed_knowledge_graph.ttl",
    )

    counts = {name: 0 for name in RELATION_PREDICATES}
    for result in results:
        counts[result.relationship] += 1
    print(f"Analyzed {len(results)} clause pairs.")
    print(f"Embedding engine: {embedding_engine}")
    print(f"NLI engine: {nli_engine}")
    for relationship, count in counts.items():
        print(f"{relationship}: {count}")
    print("Created relationship_report.json, relationship_report.csv, and analyzed_knowledge_graph.ttl.")


if __name__ == "__main__":
    main()