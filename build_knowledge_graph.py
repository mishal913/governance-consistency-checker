import argparse
import csv
import re
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD


BASE_DIR = Path(__file__).resolve().parent
CUST = Namespace("http://cust.edu.pk/ontology/")


def read_clauses(data_dir=BASE_DIR):
    path = data_dir / "governance_clauses.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def resource_name(value):
    words = re.findall(r"[A-Za-z0-9]+", value)
    return "".join(word[:1].upper() + word[1:] for word in words)


def build_graph(data_dir=BASE_DIR):
    clauses = read_clauses(data_dir)
    graph = Graph()
    graph.bind("cust", CUST)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("xsd", XSD)

    graph.add((CUST.Document, RDF.type, RDFS.Class))
    graph.add((CUST.Clause, RDF.type, RDFS.Class))
    graph.add((CUST.GovernanceTier, RDF.type, RDFS.Class))
    for class_name in (
        "Charter",
        "Statute",
        "Regulation",
        "Policy",
        "Procedure",
        "Requirement",
        "Exception",
        "Constraint",
    ):
        graph.add((CUST[class_name], RDF.type, RDFS.Class))

    for level in range(1, 6):
        tier = CUST[f"GovernanceLevel{level}"]
        graph.add((tier, RDF.type, CUST.GovernanceTier))
        graph.add((tier, RDFS.label, Literal(f"Governance level {level}")))
        if level < 5:
            graph.add((tier, CUST.governs, CUST[f"GovernanceLevel{level + 1}"]))

    documents = {}
    for row in clauses:
        document_name = row["source_document"]
        document = documents.setdefault(document_name, CUST[resource_name(document_name)])
        graph.add((document, RDF.type, CUST.Document))
        graph.add((document, RDFS.label, Literal(document_name)))
        graph.add(
            (
                document,
                CUST.hasGovernanceTier,
                CUST[f"GovernanceLevel{row['governance_level']}"],
            )
        )

        clause = CUST[row["clause_id"]]
        graph.add((clause, RDF.type, CUST.Clause))
        graph.add((clause, RDF.type, CUST[row["clause_type"]]))
        graph.add((clause, CUST.clauseText, Literal(row["clause_text"])))
        graph.add((clause, CUST.belongsTo, document))
        graph.add(
            (
                clause,
                CUST.governanceLevel,
                Literal(int(row["governance_level"]), datatype=XSD.integer),
            )
        )
        graph.add((clause, CUST.subjectDomain, Literal(row["subject_domain"])))
        graph.add((clause, CUST.predicateLogic, Literal(row["predicate_logic"])))
        if row["clause_type"] == "Exception":
            graph.add((clause, RDF.type, CUST.Exception))
        elif re.search(r"\b(no|not|never|maximum|prohibited|cannot)\b", row["clause_text"], re.I):
            graph.add((clause, RDF.type, CUST.Constraint))
        elif re.search(r"\b(shall|must|required)\b", row["clause_text"], re.I):
            graph.add((clause, RDF.type, CUST.Requirement))

        if row["exception_to"]:
            graph.add((clause, CUST.exceptionTo, CUST[row["exception_to"]]))
        if row["exception_rationale"]:
            graph.add(
                (clause, CUST.exceptionRationale, Literal(row["exception_rationale"]))
            )

    return graph


def main():
    parser = argparse.ArgumentParser(
        description="Build RDF using governance_clauses.csv as the only input."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "cust_knowledge_graph.ttl",
        help="Turtle output path.",
    )
    args = parser.parse_args()

    graph = build_graph()
    graph.serialize(destination=args.output, format="turtle")
    print(f"Created {args.output} with {len(graph)} triples.")


if __name__ == "__main__":
    main()