# Presentation Outline

## Slide 1: Title

University Governance Document Consistency Checker

## Slide 2: Problem

- Governance documents form a hierarchy.
- Manual comparison is slow and error-prone.
- Required outputs: contradiction, entailment, neutral, exception, redundancy.

## Slide 3: Objectives

- Formal knowledge representation
- RDF graph storage
- Semantic similarity
- NLI classification
- Explainable hierarchy reasoning

## Slide 4: Dataset

- `governance_clauses.csv`
- Regulations, policies, procedures, and exceptions
- Ten subject domains
- Predicate logic and exception metadata

## Slide 5: Architecture

Document import -> clause extraction -> RDF graph -> embeddings -> NLI ->
symbolic reasoning -> explanations -> Streamlit interface

## Slide 6: Knowledge Graph

- Clause and document nodes
- Governance tier nodes
- `GOVERNS`, `BELONGS_TO`, `EXCEPTION_TO`, `CONTRADICTS`, and `ENTAILS`
- Turtle RDF export

## Slide 7: Embeddings

- Model: `all-MiniLM-L6-v2`
- 384-dimensional vectors
- Cosine similarity retrieves related clauses

## Slide 8: NLI and Symbolic Reasoning

- Model: `nli-deberta-v3-small`
- Entailment, contradiction, neutral
- Explicit exceptions and numeric conflicts handled symbolically

## Slide 9: Explainability Example

Show REG001 versus POL006:

- 75 percent versus 60 percent
- Contradiction
- Level 4 conflicts with level 3
- Hierarchy violation explanation

## Slide 10: User Interface

- Dashboard
- Full analysis
- Clause comparison
- Document import
- Data audit

## Slide 11: Results

- All required relationship classes detected
- RDF and CSV/JSON reports generated
- Automated tests pass
- Neural models run locally after caching

## Slide 12: Limitations

- Potential rather than legally definitive contradictions
- Manual predicate review
- No OCR for scanned PDFs

## Slide 13: Future Work

- OCR
- Expert-labeled evaluation
- Interactive graph visualization
- Regulation version tracking

## Slide 14: Conclusion

Complete explainable symbolic-neural governance consistency pipeline.