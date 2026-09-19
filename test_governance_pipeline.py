import unittest

from rdflib import RDF

from build_knowledge_graph import CUST, build_graph
from consistency_checker import run_checks, summary
from document_importer import segment_clauses
from semantic_analyzer import analyze_clauses


class GovernancePipelineTests(unittest.TestCase):
    def test_graph_contains_expected_resources_and_relationships(self):
        graph = build_graph()

        self.assertIn((CUST.EXC004, CUST.exceptionTo, CUST.POL003), graph)
        self.assertIn((CUST.REG001, RDF.type, CUST.Regulation), graph)
        self.assertIn(
            (CUST.GovernanceLevel3, CUST.governs, CUST.GovernanceLevel4),
            graph,
        )
        self.assertIn((CUST.REG001, RDF.type, CUST.Requirement), graph)
        self.assertIn(
            (CUST.REG001, CUST.belongsTo, CUST.StudentAcademicRegulations),
            graph,
        )

    def test_dataset_has_no_structural_errors(self):
        counts = summary(run_checks())

        self.assertEqual(counts["error"], 0)
        self.assertEqual(counts["warning"], 0)

    def test_required_relationships_are_detected(self):
        from build_knowledge_graph import read_clauses

        results, _, _ = analyze_clauses(read_clauses())
        by_pair = {
            frozenset((result.clause_a, result.clause_b)): result
            for result in results
        }

        self.assertEqual(
            by_pair[frozenset(("REG001", "POL006"))].relationship,
            "Contradiction",
        )
        self.assertTrue(
            by_pair[frozenset(("REG001", "POL006"))].hierarchy_violation
        )
        self.assertEqual(
            by_pair[frozenset(("REG021", "POL007"))].relationship,
            "Entailment",
        )
        self.assertEqual(
            by_pair[frozenset(("POL003", "POL008"))].relationship,
            "Redundancy",
        )
        self.assertEqual(
            by_pair[frozenset(("POL003", "EXC004"))].relationship,
            "Exception",
        )

    def test_clause_segmentation_preserves_first_letter(self):
        text = (
            "1. Students must maintain 75% attendance. "
            "National athletes may receive attendance relaxation."
        )
        self.assertEqual(
            segment_clauses(text),
            [
                "Students must maintain 75% attendance.",
                "National athletes may receive attendance relaxation.",
            ],
        )


if __name__ == "__main__":
    unittest.main()