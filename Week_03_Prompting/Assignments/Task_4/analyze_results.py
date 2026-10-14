"""Paired comparison of Task 3's saved accuracy and row-overlap scores."""

import csv
import itertools
import math
import shutil
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCORES_PATH = HERE.parent / "Task_3" / "row_overlap_results.csv"
FRAMEWORKS = ("RTF", "ICIO", "APE")
PAIRS = tuple(itertools.combinations(FRAMEWORKS, 2))


def mcnemar_exact(first_only, second_only):
    n = first_only + second_only
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(first_only, second_only) + 1)) / 2**n) if n else 1.0


def paired_signflip_p(first, second):
    if not first or len(first) != len(second):
        raise ValueError("Paired samples must be nonempty and have equal lengths")
    differences = [a - b for a, b in zip(first, second) if a != b]
    if not differences:
        return 1.0
    if len(differences) > 20:
        raise ValueError("Exact enumeration supports at most 20 nonzero pairs")
    observed = abs(math.fsum(differences))
    extreme = sum(
        abs(math.fsum(value * sign for value, sign in zip(differences, signs))) >= observed - 1e-12
        for signs in itertools.product((-1, 1), repeat=len(differences))
    )
    return extreme / 2**len(differences)


def holm_adjust(pvalues):
    adjusted = [0.0] * len(pvalues)
    previous = 0.0
    for rank, index in enumerate(sorted(range(len(pvalues)), key=pvalues.__getitem__)):
        previous = max(previous, min(1.0, (len(pvalues) - rank) * pvalues[index]))
        adjusted[index] = previous
    return adjusted


def read_scores():
    csv.field_size_limit(1_000_000_000)
    groups = {name: {} for name in FRAMEWORKS}
    with SCORES_PATH.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, strict=True):
            name = row["framework"]
            index = int(row["question_index"])
            if name not in groups or index < 1 or index in groups[name]:
                raise ValueError("Unknown framework, invalid index or duplicate score")
            exact, overlap = int(row["exact_match"]), float(row["jaccard"])
            if exact not in (0, 1) or not 0 <= overlap <= 1:
                raise ValueError("Invalid score")
            groups[name][index] = (row["question"], exact, overlap)
    indices = sorted(groups["RTF"])
    if not indices or indices != list(range(1, len(indices) + 1)):
        raise ValueError("Question indices must be nonempty and contiguous")
    for name in FRAMEWORKS:
        if set(groups[name]) != set(indices):
            raise ValueError("Frameworks must cover the same questions")
        if any(groups[name][index][0] != groups["RTF"][index][0] for index in indices):
            raise ValueError("Question text differs between frameworks")
    return {
        metric: {name: [groups[name][index][column] for index in indices] for name in FRAMEWORKS}
        for metric, column in (("Accuracy", 1), ("Row overlap", 2))
    }


def compare(scores):
    tests = []
    for metric, series in scores.items():
        for first, second in PAIRS:
            a, b = series[first], series[second]
            if metric == "Accuracy":
                pvalue = mcnemar_exact(sum(x and not y for x, y in zip(a, b)), sum(y and not x for x, y in zip(a, b)))
            else:
                pvalue = paired_signflip_p(a, b)
            tests.append({"metric": metric, "pair": f"{first} − {second}",
                          "difference_pp": statistics.mean(a) * 100 - statistics.mean(b) * 100, "p_raw": pvalue})
    for test, adjusted in zip(tests, holm_adjust([test["p_raw"] for test in tests])):
        test["p_holm"] = adjusted
    return tests


def draw_comparison(scores):
    renderer = shutil.which("magick")
    if not renderer:
        print("PNG regeneration requires ImageMagick (magick); statistical results are still available.")
        return
    colors = {"RTF": "#2563eb", "ICIO": "#0d9488", "APE": "#b45309"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="940" height="440">',
        '<style>text{font-family:Arial,sans-serif;fill:#0f172a}.title{font-size:23px;font-weight:bold}.heading{font-size:18px;font-weight:bold}.small{font-size:12px;fill:#475569}.value{font-size:15px;font-weight:bold;paint-order:stroke;stroke:white;stroke-width:4px}</style>',
        '<rect width="940" height="440" fill="#f8fafc"/>',
        '<text x="24" y="35" class="title">Exact accuracy versus partial row overlap</text>',
        '<text x="24" y="61" class="small">GPT-6.1 Sol · max thinking · Pi · 155 questions · one generation per framework</text>',
    ]
    for panel, (metric, series) in enumerate(scores.items()):
        left = 20 + panel * 460
        parts.extend([
            f'<rect x="{left}" y="88" width="440" height="314" rx="10" fill="white" stroke="#e2e8f0"/>',
            f'<text x="{left+24}" y="121" class="heading">{metric}</text>',
        ])
        for tick in (0, 25, 50, 75, 100):
            y = 338 - tick * 1.7
            parts.append(f'<line x1="{left+65}" y1="{y}" x2="{left+407}" y2="{y}" stroke="#e2e8f0"/>')
            parts.append(f'<text x="{left+56}" y="{y+4}" text-anchor="end" class="small">{tick}%</text>')
        for index, name in enumerate(FRAMEWORKS):
            x = left + 126 + index * 111
            value = statistics.mean(series[name]) * 100
            height = value * 1.7
            parts.extend([
                f'<rect x="{x-27}" y="{338-height:.3f}" width="54" height="{height:.3f}" rx="3" fill="{colors[name]}"/>',
                f'<text x="{x}" y="{326-height:.3f}" text-anchor="middle" class="value">{value:.2f}%</text>',
                f'<text x="{x}" y="366" text-anchor="middle" class="heading">{name}</text>',
            ])
    parts.append('<text x="24" y="426" class="small">Row overlap rewards partially correct answers; identical output rows give identical scores.</text></svg>')
    subprocess.run([renderer, "-background", "white", "-density", "96", "svg:-", str(HERE / "comparison.png")],
                   input="\n".join(parts).encode(), check=True)


def main():
    scores = read_scores()
    print("Metric | Framework | Mean score")
    for metric, series in scores.items():
        for name in FRAMEWORKS:
            print(f"{metric} | {name} | {statistics.mean(series[name]):.6%}")
    print("\nMetric | Pair | Difference (pp) | Raw p | Holm p")
    for test in compare(scores):
        print(f"{test['metric']} | {test['pair']} | {test['difference_pp']:+.6f} | {test['p_raw']:.6f} | {test['p_holm']:.6f}")
    draw_comparison(scores)


if __name__ == "__main__":
    main()
