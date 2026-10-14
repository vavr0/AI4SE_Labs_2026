# Task 3 — Row Overlap

## Metric and justification

The additional metric is **multiset Jaccard overlap** between the expected and returned rows:

`overlap = matched rows / union of expected and returned rows`

The union counts each distinct row using the larger of its expected and returned multiplicities; the intersection uses the smaller. This preserves duplicate counts, as the original evaluator does. Row order is ignored; column order still matters.

Examples:
- Expected 10 rows, returned 9 correct rows: **90% overlap**, but **0% exact-match accuracy** for that question.
- Expected 10 rows, returned all 10 plus 2 wrong rows: **83.33% overlap**.
- Both answers empty: **100%**; only one empty: **0%**.

This metric distinguishes a nearly correct answer from a completely wrong one and penalizes both missing and extra rows. It **complements accuracy**, not replaces it: partial overlap does not mean the requested answer is complete. Jaccard is an established metric; the task-specific adaptation is applying it to SQL result multisets.

## Implementation and results

[calculate_overlap.py](calculate_overlap.py) executes the unchanged Task 2 predictions against the teacher's database and compares them with the reference row multisets. No new LLM runs are needed. The final score is the **mean across all 155 questions**, giving each question equal weight rather than letting large result sets dominate.

| Framework | Exact-match accuracy | Mean row overlap |
|---|---:|---:|
| RTF | 92.90% | 98.33% |
| ICIO | 94.84% | 98.36% |
| APE | 94.84% | 98.36% |

The overlap scores are almost identical: ICIO/APE exceed RTF by only **0.035 percentage points**. This suggests the exact-match accuracy difference overstates the difference in partial result quality. ICIO and APE return the same row multisets on every question, so they necessarily tie on both metrics.

All 43 empty reference answers were correctly returned by every framework and contribute 100% overlap. Scores measure agreement with the supplied labels, not independent verification of their intended meaning.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 Week_03_Prompting/Assignments/Task_3/calculate_overlap.py
```

Per-question scores and matched/missing/extra row counts are saved in [row_overlap_results.csv](row_overlap_results.csv). Only Python's standard library is required.
