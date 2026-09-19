
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# Load files
truth = pd.read_csv("ground_truth.csv")
pred = pd.read_csv("relationship_report.csv")

# Merge
data = truth.merge(
    pred,
    on=["clause_a", "clause_b"],
    how="inner"
)

# Normalize labels
y_true = (
    data["actual_relationship"]
    .astype(str)
    .str.strip()
    .str.title()
)

y_pred = (
    data["relationship"]
    .astype(str)
    .str.strip()
    .str.title()
)

# Fixed class order
labels = [
    "Contradiction",
    "Entailment",
    "Exception",
    "Neutral",
    "Redundancy",
]

accuracy = accuracy_score(y_true, y_pred)

precision = precision_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=labels
)

cm_df = pd.DataFrame(
    cm,
    index=labels,
    columns=labels,
)

print("Accuracy :", accuracy)
print("Precision :", precision)
print("Recall :", recall)
print("F1 Score :", f1)
print(cm_df)
