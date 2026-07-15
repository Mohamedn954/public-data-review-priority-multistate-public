"""Generates Figure 1, the manuscript's single conceptual flow diagram, from
this script alone. No facility-level data is used; every box is a stage of
the manuscript's own argument, in the order Sections 1 through 7 present it.
"""

import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "figures", "Fig1_Conceptual_Overview.png")

STAGES = [
    ("Documented oversight gap", "Sec. 1.1: independent federal and\nstate audit and inquiry evidence"),
    ("Claims-only oversight leaves gaps", "Sec. 1.2: access and transparency gaps\nfor most oversight actors"),
    ("Initial taxonomy, later revised", "Sec. 2.1-2.2: derived from Minnesota audit/\nenforcement sources, revised via derivation audit"),
    ("Phase 1: Washington pilot", "Sec. 3.3: n=3,457, implemented at\nscale, new audit evidence and policy context"),
    ("Phase 1: Oregon portability test", "Sec. 3.4: n=792, pipeline transfers\ntechnically; interpretation required recalibration"),
    ("Disclosed, two-state method", "Sec. 3.1-4.4: heterogeneous evidentiary\nsupport, limits stated explicitly"),
    ("Phase 2: claims-informed validation (next)", "Sec. 4.5: falsification criteria,\nfirst stage of a broader research agenda"),
]

fig, ax = plt.subplots(figsize=(6.5, 7.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, len(STAGES) * 1.8 + 0.6)
ax.axis("off")

box_w, box_h = 8.6, 1.3
x0 = (10 - box_w) / 2

colors = ["#f2f2f2"] * 2 + ["#dbe9f6"] * 4 + ["#eaf5ea"]

for i, (title, note) in enumerate(STAGES):
    y = (len(STAGES) - i - 1) * 1.8 + 0.6
    box = FancyBboxPatch(
        (x0, y), box_w, box_h,
        boxstyle="round,pad=0.08,rounding_size=0.12",
        linewidth=1.1, edgecolor="#333333", facecolor=colors[i],
    )
    ax.add_patch(box)
    ax.text(x0 + box_w / 2, y + box_h * 0.64, title, ha="center", va="center",
            fontsize=10, fontweight="bold", color="#1a1a1a")
    ax.text(x0 + box_w / 2, y + box_h * 0.26, note, ha="center", va="center",
            fontsize=7.8, color="#333333")
    if i < len(STAGES) - 1:
        arrow = FancyArrowPatch(
            (5, y), (5, y - 0.5),
            arrowstyle="-|>", mutation_scale=13, linewidth=1.1, color="#333333",
        )
        ax.add_patch(arrow)

ax.set_title("Figure 1. From documented oversight gap to a disclosed,\ntwo-state-tested review-priority framework",
              fontsize=11, fontweight="bold", pad=14)

plt.tight_layout()
plt.savefig(OUT, dpi=200)
plt.savefig(OUT.replace(".png", ".pdf"))
print(f"saved {OUT}")
