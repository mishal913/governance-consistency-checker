# UNIVERSITY GOVERNANCE DOCUMENT CONSISTENCY CHECKER USING KNOWLEDGE GRAPH, SEMANTIC SIMILARITY AND NATURAL LANGUAGE INFERENCE

## Abstract

The increasing volume of university governance documents such as regulations, policies, procedures, and exceptions makes manual consistency verification difficult and time-consuming. Conflicting or redundant clauses can create ambiguity and lead to incorrect administrative decisions. This project presents an intelligent University Governance Document Consistency Checker that automatically identifies semantic relationships among governance clauses using a hybrid artificial intelligence framework.

The proposed system integrates Resource Description Framework (RDF)-based knowledge graphs, semantic similarity through Sentence-BERT embeddings, Natural Language Inference (NLI), symbolic logical reasoning, hierarchy validation, and explainable artificial intelligence techniques. Governance clauses are represented as structured knowledge entities, allowing the system to detect contradictions, entailments, redundancies, exceptions, and hierarchy violations.

The application provides a user-friendly Streamlit interface capable of importing governance documents in PDF, DOCX, and TXT formats, extracting governance clauses automatically, performing semantic consistency analysis, and generating downloadable reports. Experimental evaluation using manually annotated ground truth demonstrates an overall accuracy of 94.96%, precision of 98.91%, recall of 77.50%, and F1-score of 82.82%, indicating high reliability in detecting governance inconsistencies while maintaining excellent prediction precision.

The developed framework offers an efficient decision-support tool for universities to improve governance quality, reduce policy conflicts, and maintain institutional consistency.

**Keywords:** Knowledge Graph, RDF, Semantic Similarity, Sentence-BERT, Natural Language Inference, Governance Analysis, Explainable AI, Policy Consistency.

---

# Chapter 1: Introduction

## 1.1 Background

Universities operate through a large collection of governance documents including regulations, policies, procedures, statutes, and exceptions. These documents define academic rules, administrative procedures, financial policies, student conduct requirements, and institutional responsibilities.

As governance documents evolve over time, inconsistencies frequently emerge due to independent revisions by different departments. Manual review of hundreds of clauses is inefficient and prone to human error.

Recent advances in Artificial Intelligence and Natural Language Processing provide opportunities to automate governance analysis by understanding semantic relationships between policy statements rather than relying solely on keyword matching.

---

## 1.2 Problem Statement

Universities face several governance challenges:

- Contradictory regulations issued by different departments.
- Duplicate or redundant policies.
- Exception clauses that are not properly linked.
- Hierarchy violations where lower-level policies conflict with higher-level regulations.
- Manual consistency checking requiring extensive human effort.

Traditional text matching methods cannot understand semantic meaning, making automated governance verification difficult.

---

## 1.3 Objectives

The primary objectives of this project are:

- Develop an RDF-based governance knowledge graph.
- Extract governance clauses from multiple document formats.
- Compute semantic similarity using Sentence-BERT embeddings.
- Apply Natural Language Inference for logical relationship detection.
- Detect contradictions, entailments, redundancies, and exceptions.
- Identify governance hierarchy violations.
- Generate explainable outputs for every detected relationship.
- Evaluate system performance using standard classification metrics.

---

## 1.4 Scope

The proposed system supports:

- PDF document analysis
- DOCX document analysis
- TXT document analysis
- Governance clause extraction
- Knowledge graph construction
- Semantic similarity computation
- Rule-based reasoning
- Neural semantic reasoning
- Explainable relationship detection
- Downloadable consistency reports

---

# Chapter 2: Literature Review

Knowledge graphs have become an important technology for representing structured organizational knowledge. RDF enables semantic relationships among entities and supports logical reasoning.

Sentence-BERT provides contextual sentence embeddings that capture semantic similarity beyond lexical matching, making it suitable for policy comparison tasks.

Natural Language Inference models classify whether one statement entails, contradicts, or is neutral with respect to another statement, providing deeper semantic understanding.

Hybrid AI systems combining symbolic reasoning and neural language models have demonstrated superior interpretability and accuracy compared to purely neural architectures.

This project combines these technologies into a unified governance consistency analysis framework.

---

# Chapter 3: System Architecture

## 3.1 Overall Architecture

The system consists of the following modules:

1. Governance Dataset
2. Document Import Module
3. Clause Segmentation Module
4. RDF Knowledge Graph Generator
5. Sentence Embedding Generator
6. Similarity Computation Engine
7. Natural Language Inference Engine
8. Symbolic Rule Engine
9. Relationship Classifier
10. Explainability Generator
11. Evaluation Module
12. Streamlit User Interface

---

## 3.2 Workflow

Input Documents

↓

Text Extraction

↓

Clause Segmentation

↓

Knowledge Graph Construction

↓

Sentence Embedding Generation

↓

Semantic Similarity Calculation

↓

Natural Language Inference

↓

Symbolic Rule Analysis

↓

Relationship Classification

↓

Hierarchy Validation

↓

Explainable Output Generation

↓

CSV / JSON / RDF Reports

---

# Chapter 4: Methodology

## 4.1 Knowledge Graph Construction

Governance clauses are represented as RDF triples.

Example:

REG001 → belongsTo → Student Academic Regulations

REG001 → governanceLevel → Level 3

REG001 → subjectDomain → Attendance

This representation enables semantic querying and logical reasoning.

---

## 4.2 Clause Extraction

Uploaded documents are processed using document parsers.

Supported formats include:

- PDF
- DOCX
- TXT

Rule-based segmentation identifies governance clauses based on modal expressions such as:

- shall
- must
- may
- required
- prohibited
- eligible

---

## 4.3 Semantic Similarity

Sentence-BERT generates vector embeddings for governance clauses.

Cosine similarity measures semantic closeness between clause pairs.

Only candidate pairs above the similarity threshold proceed to detailed analysis.

---

## 4.4 Symbolic Rule Engine

The symbolic engine detects:

- Numeric conflicts
- Predicate conflicts
- Negation relationships
- Exception links
- Redundant rules

This provides interpretable logical reasoning.

---

## 4.5 Natural Language Inference

The DeBERTa NLI model classifies clause relationships into:

- Entailment
- Contradiction
- Neutral

Neural reasoning complements symbolic analysis for improved semantic understanding.

---

## 4.6 Hierarchy Validation

Governance levels are defined as:

Level 1 — Charter

Level 2 — Statute

Level 3 — Regulation

Level 4 — Policy

Level 5 — Procedure

Contradictions between lower-level and higher-level clauses are identified as hierarchy violations.

---

# Chapter 5: Implementation

The project is implemented using Python.

Major libraries include:

- Streamlit
- RDFLib
- Sentence Transformers
- Transformers
- NumPy
- Pandas
- Scikit-learn
- python-docx
- PyPDF

The application provides an interactive web interface supporting governance analysis and downloadable reports.

---

# Chapter 6: Experimental Results

## Evaluation Metrics

| Metric | Value |
|----------|------------|
| Accuracy | 94.96% |
| Precision | 98.91% |
| Recall | 77.50% |
| F1 Score | 82.82% |

The high accuracy demonstrates strong overall performance.

Excellent precision indicates that predicted relationships are highly reliable with very few false positives.

The comparatively lower recall suggests that some contradiction and exception relationships remain undetected, providing opportunities for future enhancement.

---

## Relationship Categories

The system detects:

- Entailment
- Contradiction
- Neutral
- Exception
- Redundancy

Each detected relationship is accompanied by a human-readable explanation, improving interpretability.

---

# Chapter 7: Advantages

- Automated governance verification
- Reduced manual effort
- Explainable AI decisions
- Knowledge graph representation
- Semantic understanding
- Hierarchy validation
- Multi-format document support
- High classification accuracy
- Downloadable reports
- Scalable architecture

---

# Chapter 8: Limitations

- Performance depends on dataset quality.
- Recall for contradiction detection can be improved.
- Implicit exceptions remain challenging.
- Neural models require additional computational resources.
- Domain adaptation may be needed for non-university governance documents.

---

# Chapter 9: Future Work

Future enhancements include:

- Large Language Model integration
- Graph Neural Networks
- Automatic ontology learning
- Cross-document reasoning
- Multilingual governance analysis
- Real-time policy monitoring
- Incremental knowledge graph updates
- Advanced contradiction detection
- Policy recommendation engine

---

# Chapter 10: Conclusion

This project presents a comprehensive University Governance Document Consistency Checker that integrates knowledge graphs, semantic similarity, symbolic reasoning, and Natural Language Inference to automate governance consistency analysis.

The hybrid framework successfully identifies contradictions, entailments, redundancies, exceptions, and hierarchy violations while providing explainable results through a user-friendly interface.

Experimental evaluation demonstrates high overall performance with 94.96% accuracy and 98.91% precision, indicating that the proposed system is an effective decision-support tool for institutional governance management.

The developed framework contributes to intelligent policy analysis and provides a scalable foundation for future AI-driven governance systems.

---

# References

1. Devlin, J., Chang, M., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.

2. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT Networks.

3. Pan, J. Z. (2009). Resource Description Framework (RDF): Concepts and Applications.

4. Vaswani, A., et al. (2017). Attention Is All You Need.

5. Wolf, T., et al. (2020). Transformers: State-of-the-Art Natural Language Processing.

6. W3C. RDF 1.1 Concepts and Abstract Syntax.

7. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python.

8. Abadi, M., et al. TensorFlow: Large-Scale Machine Learning on Heterogeneous Systems.

9. Goodfellow, I., Bengio, Y., & Courville, A. Deep Learning. MIT Press.

10. Jurafsky, D., & Martin, J. H. Speech and Language Processing.