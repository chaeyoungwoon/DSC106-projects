import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("/Users/echoi/Documents/GitHub/DSC106 projects/grocerydb.csv")

CLASSES = [0, 1, 2, 3]
LABELS = ["Unprocessed", "Culinary\nIngredients", "Processed", "Ultra-\nProcessed"]

nutrients = [
    ("Sugars, total", "Sugar",         "#B863EC"),
    ("Carbohydrate",  "Carbohydrates", "#20236C"),
    ("Sodium",        "Sodium",        "#0CAFF0"),
]

fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor("white")

actual_medians = {}
all_norms = {}

for col, label, color in nutrients:
    medians = []
    for c in CLASSES:
        vals = df[df["FPro_class"] == c][col].dropna()
        cap = vals.quantile(0.99)
        medians.append(np.median(vals[vals <= cap]))

    actual_medians[label] = medians
    norm = [(v - min(medians)) / (max(medians) - min(medians)) for v in medians]
    all_norms[label] = norm

    # No fill_between — just the line
    ax.plot(range(4), norm, color=color, linewidth=2.5, marker="o", markersize=7, label=label, zorder=3)

offsets = {
    "Sugar":         [0.05, 0.05, 0.05, 0.05],
    "Carbohydrates": [0.05, 0.05, 0.05, -0.08],
    "Sodium":        [0.05, 0.05, 0.05, -0.1],
}

for col, label, color in nutrients:
    norm = all_norms[label]
    off = offsets[label]
    for i, v in enumerate(norm):
        ax.text(i, v + off[i], f"{v:.2f}",
                ha="center", va="bottom", fontsize=8, color=color, fontweight="bold")

ax.set_title(
    "Ultra-Processed foods contain higher sugar and carb content",
    fontsize=12, fontweight="bold", loc="left", pad=10)
ax.set_xticks(range(4))
ax.set_xticklabels(LABELS, fontsize=9)
ax.set_ylabel("Normalized median (0 = min, 1 = max)", fontsize=9)
ax.set_ylim(-0.05, 1.35)
ax.legend(fontsize=9, frameon=False, loc="upper left")
ax.grid(axis="y", color="#eeeeee", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

s = actual_medians["Sugar"]
c = actual_medians["Carbohydrates"]
n = actual_medians["Sodium"]
fig.text(0.02, -0.08,
    f"GroceryDB · 26,250 items across Walmart, Target, and Whole Foods · "
    f"Values normalized per nutrient to show relative change across NOVA classes\n"
    f"Actual medians (Class 3): Sugar {s[3]:.1f}g, Carbohydrates {c[3]:.1f}g, Sodium {n[3]:.3f}g per 100g · "
    f"Values above P99 excluded per class",
    fontsize=7.5, color="#888888")

plt.tight_layout()
plt.savefig("plot_nova_combined.png", dpi=180, bbox_inches="tight")
plt.close()
print("Saved plot_nova_combined.png")