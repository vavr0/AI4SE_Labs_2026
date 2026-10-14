"""Evaluate saved SQL with exact-match accuracy and multiset Jaccard overlap."""

import csv
import importlib.util
import json
import sqlite3
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK2 = HERE.parent / "Task_2"
RESULTS_PATH = HERE / "row_overlap_results.csv"
FRAMEWORKS = ("RTF", "ICIO", "APE")


def multiset_jaccard(expected, actual):
    """Counters preserve duplicate rows; two empty answers score 1."""
    union_size = sum((expected | actual).values())
    return sum((expected & actual).values()) / union_size if union_size else 1.0


def load_evaluator():
    sys.dont_write_bytecode = True
    path = TASK2 / "data" / "evaluate_retrieval_predictions.py"
    spec = importlib.util.spec_from_file_location("teacher_evaluator", path)
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    return evaluator


def read_predictions(path, questions):
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != ["question", "predicted_sql"]:
            raise ValueError(f"Unexpected prediction columns in {path}")
        predictions = {}
        for row in reader:
            question = row["question"]
            sql = (row.get("predicted_sql") or "").strip()
            if question in predictions or not sql or None in row:
                raise ValueError(f"Duplicate question, empty SQL or malformed row in {path}")
            predictions[question] = sql
    if len(predictions) != len(questions) or set(predictions) != set(questions):
        raise ValueError(f"Prediction coverage does not match the dataset: {path}")
    return [predictions[question] for question in questions]


def evaluate_predictions():
    csv.field_size_limit(1_000_000_000)
    evaluator = load_evaluator()
    with evaluator.LABELS_PATH.open(encoding="utf-8", newline="") as source:
        labels = list(csv.DictReader(source, strict=True))
    questions = [row["question"] for row in labels]
    expected = []
    for row in labels:
        result = json.loads(row["result"])
        if not isinstance(result, list):
            raise ValueError("Reference result must be a JSON array")
        expected.append(evaluator.row_multiset(result))
    queries = {name: read_predictions(TASK2 / f"prediction_{name.lower()}.csv", questions) for name in FRAMEWORKS}

    connection = evaluator.load_database()
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    connection.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
    records = []
    try:
        for name in FRAMEWORKS:
            for index, (question, reference, sql) in enumerate(zip(questions, expected, queries[name]), start=1):
                try:
                    actual = evaluator.row_multiset(connection.execute(sql).fetchall())
                except sqlite3.Error as error:
                    raise ValueError(f"{name}, question {index}: SQL execution failed") from error
                records.append({
                    "framework": name,
                    "question_index": index,
                    "question": question,
                    "exact_match": int(actual == reference),
                    "jaccard": multiset_jaccard(reference, actual),
                    "expected_rows": sum(reference.values()),
                    "returned_rows": sum(actual.values()),
                    "matched_rows": sum((reference & actual).values()),
                    "missing_rows": sum((reference - actual).values()),
                    "extra_rows": sum((actual - reference).values()),
                })
    finally:
        connection.close()
    return records


def main():
    records = evaluate_predictions()
    if not records:
        raise ValueError("No predictions to evaluate")
    with RESULTS_PATH.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print("Framework | Exact accuracy | Mean row overlap")
    for name in FRAMEWORKS:
        selected = [row for row in records if row["framework"] == name]
        correct = sum(row["exact_match"] for row in selected)
        print(f"{name} | {correct}/{len(selected)} ({correct/len(selected):.2%}) | {statistics.mean(row['jaccard'] for row in selected):.4%}")
    print(f"Per-question scores: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
