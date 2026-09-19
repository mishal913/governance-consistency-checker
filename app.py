import csv
import io

import streamlit as st

from build_knowledge_graph import read_clauses
from consistency_checker import run_checks, summary
from document_importer import extract_text, imported_rows, segment_clauses
from semantic_analyzer import EmbeddingEngine, NLIEngine, analyze_clauses, analyze_pair

from evaluation import (
    accuracy,
    precision,
    recall,
    f1,
    cm_df,
)


st.set_page_config(
    page_title="University Governance Consistency Checker",
    page_icon="U",
    layout="wide",
)


@st.cache_data
def load_clauses():
    return read_clauses()


@st.cache_resource
def engines(use_neural):
    return EmbeddingEngine(use_neural=use_neural), NLIEngine(use_neural=use_neural)


def rows_to_csv(rows):
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue()


clauses = load_clauses()
st.title("University Governance Document Consistency Checker")
st.caption("Knowledge graphs, semantic similarity, NLI, symbolic rules, and explainable results")

with st.sidebar:
    st.header("Analysis settings")
    use_neural = st.toggle(
    "Use Sentence-BERT + NLI",
    value=True,   # ON by default
    help="Downloads the configured Hugging Face models on first use.",
)
    threshold = st.slider(
    "Candidate similarity threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.50,   # Default = 0.50
    step=0.05,
)
    st.caption("Symbolic mode is fast and offline. Neural mode satisfies the embedding and NLI layers.")


dashboard, analyzer_tab, compare_tab, import_tab, evaluation_tab = st.tabs(
    [
        "Dashboard",
        "Analyze Knowledge Base",
        "Compare Clauses",
        "Import Document",
        "Evaluation Metrics",
    ]
)


with dashboard:
    types = {}
    domains = set()
    documents = set()
    for clause in clauses:
        types[clause["clause_type"]] = types.get(clause["clause_type"], 0) + 1
        domains.add(clause["subject_domain"])
        documents.add(clause["source_document"])

    columns = st.columns(4)
    columns[0].metric("Clauses", len(clauses))
    columns[1].metric("Documents", len(documents))
    columns[2].metric("Domains", len(domains))
    columns[3].metric("Explicit exceptions", sum(bool(row["exception_to"]) for row in clauses))
    st.subheader("Dataset composition")
    st.bar_chart(types)
    st.dataframe(
        [
            {
                "ID": row["clause_id"],
                "Type": row["clause_type"],
                "Document": row["source_document"],
                "Level": row["governance_level"],
                "Domain": row["subject_domain"],
                "Clause": row["clause_text"],
            }
            for row in clauses
        ],
        width="stretch",
        hide_index=True,
    )

with analyzer_tab:
    st.write("Analyze semantically related pairs and classify their relationship.")
    if st.button("Run full analysis", type="primary"):
        with st.spinner("Comparing governance clauses..."):
            results, embedding_name, nli_name = analyze_clauses(
                clauses,
                use_neural=use_neural,
                similarity_threshold=threshold,
            )
        st.session_state["analysis_results"] = results
        st.success(f"Analyzed {len(results)} candidate pairs.")
        st.caption(f"Embeddings: {embedding_name} | NLI: {nli_name}")

    results = st.session_state.get("analysis_results", [])
    if results:
        relationship = st.selectbox(
            "Relationship filter",
            ["All", "Contradiction", "Entailment", "Exception", "Redundancy", "Neutral"],
        )
        filtered = [
            result
            for result in results
            if relationship == "All" or result.relationship == relationship
        ]
        st.dataframe(
            [result.to_dict() for result in filtered],
            width="stretch",
            hide_index=True,
        )
        st.download_button(
            "Download analysis CSV",
            rows_to_csv([result.to_dict() for result in filtered]),
            "relationship_report.csv",
            "text/csv",
        )

with compare_tab:
    labels = {
        f"{row['clause_id']} - {row['clause_text'][:65]}": row for row in clauses
    }
    left, right = st.columns(2)
    label_a = left.selectbox("Clause A", list(labels), index=0)
    label_b = right.selectbox("Clause B", list(labels), index=1)
    if st.button("Compare selected clauses"):
        a, b = labels[label_a], labels[label_b]
        embedding_engine, nli_engine = engines(use_neural)
        matrix = embedding_engine.similarity_matrix([a["clause_text"], b["clause_text"]])
        result = analyze_pair(a, b, float(matrix[0, 1]), nli_engine)
        st.subheader(result.relationship)
        first, second, third = st.columns(3)
        first.metric("Similarity", f"{result.similarity:.2f}")
        second.metric("Confidence", f"{result.confidence:.2f}")
        third.metric("Hierarchy violation", "Yes" if result.hierarchy_violation else "No")
        st.info(result.explanation)

with import_tab:
    uploaded = st.file_uploader("Upload a governance document", type=["pdf", "docx", "txt"])
    left, right = st.columns(2)
    document_name = left.text_input("Source document", "Imported Governance Document")
    level = right.selectbox("Governance level", [1, 2, 3, 4, 5], index=2)
    clause_type = left.selectbox(
        "Clause type", ["Charter", "Statute", "Regulation", "Policy", "Procedure", "Exception"]
    )
    domain = right.text_input("Subject domain", "General")
    if uploaded:
        try:
            text = extract_text(uploaded.name, uploaded.getvalue())
            extracted = segment_clauses(text)
            rows = imported_rows(extracted, document_name, level, clause_type, domain)
            st.success(f"Extracted {len(rows)} candidate governance clauses.")
            st.dataframe(rows, width="stretch", hide_index=True)
            st.download_button(
                "Download extracted clauses CSV",
                rows_to_csv(rows),
                "extracted_clauses.csv",
                "text/csv",
            )
        except Exception as exc:
            st.error(str(exc))

with evaluation_tab:

    st.header("Model Evaluation")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Accuracy",
        f"{accuracy*100:.2f}%"
    )

    c2.metric(
        "Precision",
        f"{precision*100:.2f}%"
    )

    c3.metric(
        "Recall",
        f"{recall*100:.2f}%"
    )

    c4.metric(
        "F1 Score",
        f"{f1*100:.2f}%"
    )

    st.markdown("---")

    st.subheader("Confusion Matrix")

    st.dataframe(
        cm_df,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Performance Summary")

    st.write(
        f"""
        **Accuracy:** {accuracy*100:.2f}%  
        **Precision:** {precision*100:.2f}%  
        **Recall:** {recall*100:.2f}%  
        **F1 Score:** {f1*100:.2f}%  

        These metrics evaluate the performance of the semantic consistency analyzer by comparing predicted relationships with manually annotated ground truth labels.
        """
    )
