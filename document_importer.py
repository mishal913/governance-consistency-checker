import io
import re
from pathlib import Path


RULE_WORDS = re.compile(
    r"\b(shall|must|may|should|required|prohibited|eligible|permitted|"
    r"not allowed|cannot|will)\b",
    re.IGNORECASE,
)


def extract_text(file_name, content):
    suffix = Path(file_name).suffix.lower()
    if suffix == ".txt":
        return content.decode("utf-8-sig", errors="replace")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError(
                "DOCX support requires: python -m pip install python-docx"
            ) from exc
        document = Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    raise ValueError("Supported document types are PDF, DOCX, and TXT.")


def segment_clauses(text, minimum_words=5):
    cleaned = re.sub(r"[ \t]+", " ", text.replace("\r", "\n"))
    blocks = re.split(r"\n+|(?<=[.!?;])\s+(?=[A-Z0-9])", cleaned)
    clauses = []
    seen = set()

    for block in blocks:
        candidate = re.sub(
            r"^\s*(?:\d+(?:\.\d+)*[\).:-]?|[a-zA-Z][\).:-])\s*",
            "",
            block,
        )
        candidate = candidate.strip(" \n\t-")
        if len(candidate.split()) < minimum_words or not RULE_WORDS.search(candidate):
            continue
        normalized = re.sub(r"\W+", " ", candidate.lower()).strip()
        if normalized not in seen:
            clauses.append(candidate)
            seen.add(normalized)
    return clauses


def imported_rows(
    clauses,
    source_document,
    governance_level,
    clause_type,
    subject_domain,
    prefix="NEW",
):
    return [
        {
            "clause_id": f"{prefix}{index:03d}",
            "clause_text": text,
            "clause_type": clause_type,
            "source_document": source_document,
            "governance_level": str(governance_level),
            "subject_domain": subject_domain,
            "predicate_logic": "",
            "exception_to": "",
            "exception_rationale": "",
        }
        for index, text in enumerate(clauses, start=1)
    ]