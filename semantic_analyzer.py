import math
import os
import re
from dataclasses import asdict, dataclass

import numpy as np


RELATIONSHIPS = ("Entailment", "Contradiction", "Neutral", "Exception", "Redundancy")
NEGATIONS = {"no", "not", "never", "cannot", "prohibited", "non-refundable"}
TOKEN_RE = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")


@dataclass(frozen=True)
class AnalysisResult:
    clause_a: str
    clause_b: str
    relationship: str
    similarity: float
    confidence: float
    hierarchy_violation: bool
    engine: str
    explanation: str

    def to_dict(self):
        return asdict(self)


def tokens(text):
    return TOKEN_RE.findall(text.lower())


def normalized_text(text):
    return " ".join(tokens(text))


def numeric_values(text):
    return [float(value) for value in re.findall(r"\d+(?:\.\d+)?", text)]


def has_negation(text):
    return bool(set(tokens(text)) & NEGATIONS)


def consequent_predicates(rule):
    if "->" not in rule:
        return set()
    consequent = rule.split("->", 1)[1]
    return set(re.findall(r"(?:NOT\s+)?([A-Za-z][A-Za-z0-9_]*)\s*\(", consequent))


class EmbeddingEngine:
    def __init__(self, use_neural=False, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.engine_name = "lexical cosine"
        if use_neural:
            try:
                os.environ.setdefault("HF_HUB_OFFLINE", "1")
                os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(model_name, local_files_only=True)
                self.engine_name = model_name
            except (ImportError, OSError, RuntimeError):
                self.model = None

    def encode(self, texts):
        if self.model is not None:
            return np.asarray(
                self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            )
        vocabulary = sorted({token for text in texts for token in tokens(text)})
        index = {token: position for position, token in enumerate(vocabulary)}
        matrix = np.zeros((len(texts), max(1, len(vocabulary))), dtype=float)
        document_frequency = {token: 0 for token in vocabulary}
        for text in texts:
            for token in set(tokens(text)):
                document_frequency[token] += 1
        for row, text in enumerate(texts):
            words = tokens(text)
            for token in words:
                tf = words.count(token) / max(1, len(words))
                idf = math.log((1 + len(texts)) / (1 + document_frequency[token])) + 1
                matrix[row, index[token]] = tf * idf
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.where(norms == 0, 1, norms)

    def similarity_matrix(self, texts):
        embeddings = self.encode(texts)
        return np.clip(embeddings @ embeddings.T, -1.0, 1.0)


class NLIEngine:
    def __init__(self, use_neural=False, model_name="cross-encoder/nli-deberta-v3-small"):
        self.pipeline = None
        self.model_name = "symbolic rules"
        if use_neural:
            try:
                os.environ.setdefault("HF_HUB_OFFLINE", "1")
                os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
                from transformers import AutoModelForSequenceClassification, AutoTokenizer
                from transformers import pipeline

                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    local_files_only=True,
                )
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    local_files_only=True,
                )
                self.pipeline = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                )
                self.model_name = model_name
            except (ImportError, OSError, RuntimeError):
                self.pipeline = None

    def predict(self, premise, hypothesis):
        if self.pipeline is None:
            return None
        prediction = self.pipeline(
            {"text": premise, "text_pair": hypothesis},
            truncation=True,
        )
        if isinstance(prediction, list):
            prediction = prediction[0]
        label = prediction["label"].lower()
        if "entail" in label:
            relation = "Entailment"
        elif "contrad" in label:
            relation = "Contradiction"
        else:
            relation = "Neutral"
        return relation, float(prediction["score"])


def _symbolic_relation(a, b, similarity):
    text_a = a["clause_text"]
    text_b = b["clause_text"]
    if a.get("exception_to") == b["clause_id"] or b.get("exception_to") == a["clause_id"]:
        return "Exception", 1.0, "An explicit exception_to link connects these clauses."

    if normalized_text(text_a) == normalized_text(text_b):
        return "Redundancy", 1.0, "The normalized clause texts are identical."

    values_a = numeric_values(text_a)
    values_b = numeric_values(text_b)
    same_domain = a["subject_domain"] == b["subject_domain"]
    same_consequence = bool(
        consequent_predicates(a["predicate_logic"])
        & consequent_predicates(b["predicate_logic"])
    )
    if (
        same_domain
        and (same_consequence or similarity >= 0.35)
        and values_a
        and values_b
        and values_a != values_b
    ):
        return (
            "Contradiction",
            min(0.98, 0.75 + similarity / 4),
            f"The clauses discuss the same domain but set different numeric values: {values_a} and {values_b}.",
        )

    if a["predicate_logic"].strip() == b["predicate_logic"].strip():
        return (
            "Redundancy",
            max(0.9, similarity),
            "The clauses use the same formal predicate rule.",
        )

    if same_domain and similarity >= 0.35 and has_negation(text_a) != has_negation(text_b):
        return (
            "Contradiction",
            min(0.9, 0.6 + similarity / 3),
            "The clauses are semantically related but one negates or prohibits what the other permits.",
        )

    words_a = set(tokens(text_a))
    words_b = set(tokens(text_b))
    containment = min(
        len(words_a & words_b) / max(1, len(words_a)),
        len(words_a & words_b) / max(1, len(words_b)),
    )
    if similarity >= 0.88 or containment >= 0.8:
        return "Redundancy", max(similarity, containment), "The clauses express nearly the same rule."
    if same_domain and same_consequence and similarity >= 0.25:
        return (
            "Entailment",
            max(0.78, similarity),
            "The formal rules derive the same consequence from compatible conditions.",
        )
    if similarity >= 0.55 and same_domain:
        return "Entailment", min(0.88, similarity), "The clauses are closely related and one supports the other."
    return "Neutral", max(0.5, 1 - similarity), "No direct logical conflict, implication, or exception was established."


def _explanation(a, b, relationship, reason, hierarchy_violation):
    explanation = (
        f"{a['clause_id']} ({a['source_document']}, level {a['governance_level']}) "
        f"was compared with {b['clause_id']} ({b['source_document']}, "
        f"level {b['governance_level']}). {reason}"
    )
    if hierarchy_violation:
        lower = a if int(a["governance_level"]) > int(b["governance_level"]) else b
        higher = b if lower is a else a
        explanation += (
            f" This is a hierarchy violation because lower-level {lower['clause_id']} "
            f"conflicts with higher-level {higher['clause_id']}."
        )
    elif relationship == "Exception":
        explanation += " The narrower rule qualifies the general rule instead of replacing it."
    return explanation


def analyze_pair(a, b, similarity, nli_engine=None):
    relationship, confidence, reason = _symbolic_relation(a, b, similarity)
    engine = "symbolic"

    if relationship not in {"Exception", "Redundancy", "Contradiction"} and nli_engine:
        neural = nli_engine.predict(a["clause_text"], b["clause_text"])
        if neural:
            relationship, confidence = neural
            reason = f"The NLI model classified the pair as {relationship.lower()}."
            engine = nli_engine.model_name

    hierarchy_violation = (
        relationship == "Contradiction"
        and int(a["governance_level"]) != int(b["governance_level"])
    )
    return AnalysisResult(
        clause_a=a["clause_id"],
        clause_b=b["clause_id"],
        relationship=relationship,
        similarity=round(float(similarity), 4),
        confidence=round(float(confidence), 4),
        hierarchy_violation=hierarchy_violation,
        engine=engine,
        explanation=_explanation(a, b, relationship, reason, hierarchy_violation),
    )


def analyze_clauses(clauses, use_neural=False, similarity_threshold=0.2):
    embedding_engine = EmbeddingEngine(use_neural=use_neural)
    nli_engine = NLIEngine(use_neural=use_neural)
    similarities = embedding_engine.similarity_matrix(
        [clause["clause_text"] for clause in clauses]
    )
    results = []
    for first in range(len(clauses)):
        for second in range(first + 1, len(clauses)):
            a, b = clauses[first], clauses[second]
            similarity = float(similarities[first, second])
            explicit_exception = (
                a.get("exception_to") == b["clause_id"]
                or b.get("exception_to") == a["clause_id"]
            )
            same_domain = a["subject_domain"] == b["subject_domain"]
            if similarity < similarity_threshold and not explicit_exception and not same_domain:
                continue
            results.append(analyze_pair(a, b, similarity, nli_engine))
    return results, embedding_engine.engine_name, nli_engine.model_name