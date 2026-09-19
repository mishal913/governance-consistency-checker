import argparse
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from build_knowledge_graph import BASE_DIR, read_clauses


REQUIRED_FIELDS = (
    "clause_id",
    "clause_text",
    "clause_type",
    "source_document",
    "governance_level",
    "subject_domain",
    "predicate_logic",
)
EXPECTED_LEVELS = {"Regulation": "3", "Policy": "4", "Procedure": "5"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    entities: tuple[str, ...] = ()


def add(findings, severity, code, message, *entities):
    findings.append(Finding(severity, code, message, tuple(entities)))


def consequent_literals(rule):
    if "->" not in rule:
        return []
    consequent = rule.split("->", 1)[1]
    literals = []
    for part in re.split(r"\s+AND\s+", consequent):
        value = part.strip()
        negative = value.startswith("NOT ")
        if negative:
            value = value[4:].strip()
        match = re.match(r"([A-Za-z][A-Za-z0-9_]*)\s*\(", value)
        if match:
            literals.append((match.group(1), negative))
    return literals


def run_checks(data_dir=BASE_DIR):
    clauses = read_clauses(data_dir)
    findings = []
    seen = set()

    for row_number, clause in enumerate(clauses, start=2):
        clause_id = clause["clause_id"]
        if clause_id in seen:
            add(findings, "error", "DUPLICATE_CLAUSE_ID", f"Duplicate ID {clause_id}.", clause_id)
        seen.add(clause_id)

        for field in REQUIRED_FIELDS:
            if not clause.get(field, "").strip():
                add(
                    findings,
                    "error",
                    "MISSING_VALUE",
                    f"Row {row_number} is missing {field}.",
                    clause_id or f"row-{row_number}",
                )

        expected_level = EXPECTED_LEVELS.get(clause["clause_type"])
        if expected_level and clause["governance_level"] != expected_level:
            add(
                findings,
                "warning",
                "TYPE_LEVEL_MISMATCH",
                (
                    f"{clause_id} is a {clause['clause_type']} but uses governance "
                    f"level {clause['governance_level']} instead of {expected_level}."
                ),
                clause_id,
            )

        if "->" not in clause["predicate_logic"]:
            add(
                findings,
                "error",
                "INVALID_RULE",
                f"{clause_id} predicate logic has no implication operator.",
                clause_id,
            )

        if (
            "only if" in clause["clause_text"].lower()
            and clause["predicate_logic"].split("->", 1)[0].find("Allowed") == -1
            and clause["predicate_logic"].split("->", 1)[0].find("Eligible") == -1
        ):
            add(
                findings,
                "warning",
                "ONLY_IF_DIRECTION_REVIEW",
                (
                    f"{clause_id} contains 'only if'; verify that the predicate logic "
                    "models a necessary condition rather than a sufficient one."
                ),
                clause_id,
            )

    clauses_by_id = {row["clause_id"]: row for row in clauses}
    exception_pairs = {
        frozenset((row["clause_id"], row["exception_to"]))
        for row in clauses
        if row["exception_to"]
    }
    for clause in clauses:
        target_id = clause["exception_to"]
        if clause["clause_type"] == "Exception" and not target_id:
            add(
                findings,
                "warning",
                "UNLINKED_EXCEPTION",
                f"{clause['clause_id']} is not linked to a rule it qualifies.",
                clause["clause_id"],
            )
        if not target_id:
            continue

        target = clauses_by_id.get(target_id)
        if target is None:
            add(
                findings,
                "error",
                "UNKNOWN_EXCEPTION_TARGET",
                f"{clause['clause_id']} targets unknown clause {target_id}.",
                clause["clause_id"],
                target_id,
            )
        elif clause["clause_type"] != "Exception":
            add(
                findings,
                "error",
                "INVALID_EXCEPTION_SOURCE",
                f"{clause['clause_id']} has exception_to but is not an Exception.",
                clause["clause_id"],
            )
        elif clause["subject_domain"] != target["subject_domain"]:
            add(
                findings,
                "warning",
                "EXCEPTION_DOMAIN_MISMATCH",
                f"{clause['clause_id']} and {target_id} use different domains.",
                clause["clause_id"],
                target_id,
            )

    consequences = defaultdict(list)
    for clause in clauses:
        for predicate, negative in consequent_literals(clause["predicate_logic"]):
            consequences[(clause["subject_domain"], predicate)].append(
                (clause["clause_id"], negative)
            )

    for (domain, predicate), values in consequences.items():
        positive = sorted(item for item, negative in values if not negative)
        negative = sorted(item for item, is_negative in values if is_negative)
        unresolved_pairs = [
            (positive_id, negative_id)
            for positive_id in positive
            for negative_id in negative
            if frozenset((positive_id, negative_id)) not in exception_pairs
        ]
        if unresolved_pairs:
            entities = sorted({item for pair in unresolved_pairs for item in pair})
            add(
                findings,
                "warning",
                "OPPOSING_CONSEQUENTS",
                (
                    f"{domain} rules derive both {predicate} and NOT {predicate}; "
                    "review whether their conditions overlap."
                ),
                *entities,
            )

    return sorted(findings, key=lambda item: (item.severity != "error", item.code, item.entities))


def summary(findings):
    counts = {"error": 0, "warning": 0}
    for finding in findings:
        counts[finding.severity] += 1
    return counts


def write_reports(findings, json_path, markdown_path):
    counts = summary(findings)
    payload = {
        "source": "governance_clauses.csv",
        "summary": counts,
        "findings": [
            {**asdict(finding), "entities": list(finding.entities)}
            for finding in findings
        ],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Governance Consistency Report",
        "",
        "Source: `governance_clauses.csv`",
        "",
        f"- Errors: {counts['error']}",
        f"- Warnings: {counts['warning']}",
        "",
    ]
    for severity in ("error", "warning"):
        selected = [item for item in findings if item.severity == severity]
        if not selected:
            continue
        lines.extend((f"## {severity.title()}s", ""))
        for item in selected:
            entities = f" ({', '.join(item.entities)})" if item.entities else ""
            lines.append(f"- **{item.code}**{entities}: {item.message}")
        lines.append("")
    if not findings:
        lines.append("No consistency findings.")
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Check governance_clauses.csv for consistency."
    )
    parser.add_argument("--json", type=Path, default=BASE_DIR / "consistency_report.json")
    parser.add_argument(
        "--markdown", type=Path, default=BASE_DIR / "consistency_report.md"
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    findings = run_checks()
    write_reports(findings, args.json, args.markdown)
    counts = summary(findings)
    print(f"Consistency check complete: {counts['error']} errors, {counts['warning']} warnings.")
    print("Input: governance_clauses.csv")

    if counts["error"] or (args.strict and counts["warning"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()