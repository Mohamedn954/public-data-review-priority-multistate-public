"""Generates Figure 2, a dedicated visual of the 20-indicator framework's own
three-domain architecture, distinct from Figure 1 (the manuscript's overall
argument). Domain counts (9/5/6) are read directly from
anonymized_data/washington/WA_RedFlag_Testability_Matrix_v2.csv's Domain
column, not hardcoded, so the figure cannot drift out of sync with the data.
"""

import csv
import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "figures", "Fig2_Framework_Architecture.png")
MATRIX = os.path.join(BASE, "anonymized_data", "washington", "WA_RedFlag_Testability_Matrix_v2.csv")

DOMAIN_ORDER = [
    "Category 1: Program, Enrollment, and Network Anomalies",
    "Category 3: Oversight and Systemic Failures",
    "Category 2: Billing and Claims Anomalies Requiring Internal Data",
]
DOMAIN_LABELS = {
    "Category 1: Program, Enrollment, and Network Anomalies": "Program, Enrollment,\nand Network Anomalies",
    "Category 3: Oversight and Systemic Failures": "Oversight and\nSystemic Failures",
    "Category 2: Billing and Claims Anomalies Requiring Internal Data": "Billing and Claims\nAnomalies",
}
DOMAIN_SOURCE = {
    "Category 1: Program, Enrollment, and Network Anomalies": "Potentially assessed from public\nlicensing and enforcement records",
    "Category 3: Oversight and Systemic Failures": "Shown by a state's own audit\nor evaluation, not a roster count",
    "Category 2: Billing and Claims Anomalies Requiring Internal Data": "Requires internal claims,\nencounter, or investigative data",
}

counts = {d: 0 for d in DOMAIN_ORDER}
with open(MATRIX, newline="") as f:
    for row in csv.DictReader(f):
        counts[row["Domain"]] = counts.get(row["Domain"], 0) + 1

assert sum(counts.values()) == 20, f"domain counts do not sum to 20: {counts}"

fig, ax = plt.subplots(figsize=(6.5, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 9)
ax.axis("off")

box_w, box_h = 8.6, 1.9
x0 = (10 - box_w) / 2
colors = ["#dbe9f6", "#eaf5ea", "#f9e6e6"]
boundary_labels = [None, "Public-data boundary\n(structural counts stop; audits take over)",
                    "Claims boundary\n(no public-data method reaches past this line)"]

for i, domain in enumerate(DOMAIN_ORDER):
    y = (len(DOMAIN_ORDER) - i - 1) * 2.7 + 1.0
    box = FancyBboxPatch(
        (x0, y), box_w, box_h,
        boxstyle="round,pad=0.08,rounding_size=0.12",
        linewidth=1.1, edgecolor="#333333", facecolor=colors[i],
    )
    ax.add_patch(box)
    ax.text(x0 + 0.3, y + box_h * 0.68, DOMAIN_LABELS[domain], ha="left", va="center",
            fontsize=11, fontweight="bold", color="#1a1a1a")
    ax.text(x0 + 0.3, y + box_h * 0.28, DOMAIN_SOURCE[domain], ha="left", va="center",
            fontsize=8.5, color="#333333")
    ax.text(x0 + box_w - 0.5, y + box_h / 2, f"{counts[domain]}", ha="center", va="center",
            fontsize=22, fontweight="bold", color="#1a1a1a")
    if i < len(DOMAIN_ORDER) - 1:
        arrow = FancyArrowPatch((5, y), (5, y - 0.8), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.1, color="#333333")
        ax.add_patch(arrow)
        ax.text(5.6, y - 0.4, boundary_labels[i + 1], ha="left", va="center",
                fontsize=7.6, color="#555555", style="italic")

ax.set_title(f"Figure 2. The 20-indicator framework's architecture:\nthree domains ({counts[DOMAIN_ORDER[0]]}+{counts[DOMAIN_ORDER[1]]}+{counts[DOMAIN_ORDER[2]]}=20), ordered by evidentiary reach",
              fontsize=11, fontweight="bold", pad=14)

plt.tight_layout()
plt.savefig(OUT, dpi=200)
plt.savefig(OUT.replace(".png", ".pdf"))
print(f"saved {OUT}")
print("domain counts:", counts)
