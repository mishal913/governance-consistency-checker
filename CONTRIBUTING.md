# Contributing

This repository contains an explainable hybrid symbolic-neural governance consistency checker.

## Before submitting a change

- keep `governance_clauses.csv` as the source of truth
- preserve explainability for detected relationships
- add or update ground-truth cases when relationship logic changes
- do not commit private institutional documents
- run the core tests before opening a pull request

## Validation

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_governance_pipeline.py
python -m compileall -q .
```

For neural mode, install `requirements-neural.txt` separately.
