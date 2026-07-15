"""Generates Figure 3, the population and analytic-flow diagram, from this
script alone. Shows the path from raw source records to the analytic
population used for RF evaluation in each state, replacing prose description
of population/denominator decisions in the main text (Sections 2.4-2.5,
3.3-3.4).
"""

import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "figures", "Fig3_Population_Analytic_Flow.png")

STAGES = [
    ("Source records", "WA: DSHS geospatial roster, 3 counties\nOR: statewide licensing portal, 2 counties"),
    ("Exclusions", "Non-Medicaid-contracted facilities excluded\nwhere flagged; no other facility-level exclusions applied"),
    ("Deduplication", "One row per license number;\nmulti-license operators retained as separate facilities"),
    ("Analytic population", "WA: n = 3,457 (single facility type, AFH)\nOR: n = 792 (4 facility types: AFH/ALF/RCF/NF)"),
    ("Linkage", "Shared phone/address keys built per facility;\nWA phone_key applies 1 upstream generic-number exclusion"),
    ("RF evaluation", "20-indicator coding applied to the\nanalytic population, stratified by county and facility type"),
]

fig, ax = plt.subplots(figsize=(6.5, 6.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, len(STAGES) * 1.8 + 0.6)
ax.axis("off")

box_w, box_h = 8.6, 1.3
x0 = (10 - box_w) / 2

colors = ["#f2f2f2", "#fbe9e7", "#fbe9e7", "#dbe9f6", "#dbe9f6", "#eaf5ea"]

for i, (title, note) in enumerate(STAGES):
    y = (len(STAGES) - i - 1) * 1.8 + 0.6
    box = FancyBboxPatch(
        (x0, y), box_w, box_h,
        boxstyle="round,pad=0.08,rounding_size=0.12",
        linewidth=1.1, edgecolor="#333333", facecolor=colors[i],
    )
    ax.add_patch(box)
    ax.text(x0 + box_w / 2, y + box_h * 0.68, title, ha="center", va="center",
            fontsize=10, fontweight="bold", color="#1a1a1a")
    ax.text(x0 + box_w / 2, y + box_h * 0.28, note, ha="center", va="center",
            fontsize=7.5, color="#333333")
    if i < len(STAGES) - 1:
        arrow = FancyArrowPatch(
            (5, y), (5, y - 0.5),
            arrowstyle="-|>", mutation_scale=13, linewidth=1.1, color="#333333",
        )
        ax.add_patch(arrow)

ax.set_title("Figure 3. Population and analytic-flow diagram:\nsource records to RF-evaluated analytic population, both states",
              fontsize=11, fontweight="bold", pad=14)

plt.tight_layout()
plt.savefig(OUT, dpi=200)
plt.savefig(OUT.replace(".png", ".pdf"))
print(f"saved {OUT}")
