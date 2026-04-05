import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("/Users/echoi/Documents/GitHub/DSC106 projects/grocerydb.csv")

# GRAPH 1
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

    ax.fill_between(range(4), norm, alpha=0.15, color=color)
    ax.plot(range(4), norm, color=color, linewidth=2.5, marker="o", markersize=7, label=label, zorder=3)

# Label points with vertical offsets to avoid overlap
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

# Graph 2/3
import matplotlib.patches as mpatches

CLASSES = [0, 1, 2, 3]
LABELS = ["Class 0\n(Unprocessed)", "Class 1\n(Culinary\nIngredients)", "Class 2\n(Processed)", "Class 3\n(Ultra-\nProcessed)"]
COLORS = ["#B863EC", "#8AA0F7", "#20236C", "#0CAFF0"]

def get_data(nutrient):
    out = []
    for c in CLASSES:
        vals = df[df["FPro_class"] == c][nutrient].dropna()
        cap = vals.quantile(0.99)
        out.append(vals[vals <= cap].values)
    return out

# ── 3-panel boxplot ───────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 6))
fig.patch.set_facecolor("white")

nutrients    = ["Sugars, total",  "Sodium",         "Carbohydrate"]
ylabels      = ["g per 100g",     "g per 100g",     "g per 100g"]
ylims        = [(0, 52),          (0, 2.3),         (0, 80)]
yticks       = [10,               0.5,              20]
dec          = [1,                3,                1]
callout_cls  = [3,                2,                3]
panel_titles = ["Sugar",          "Sodium",         "Carbohydrates"]

for ax, nutrient, ylabel, ylim, yt, d, cc, pt in zip(
        axes, nutrients, ylabels, ylims, yticks, dec, callout_cls, panel_titles):

    data = get_data(nutrient)

    med_cc = np.median(data[cc])
    med_c0 = np.median(data[0])
    ratio = round(med_cc / med_c0) if nutrient != "Sodium" else None
    ct = f"Median: {med_cc:.{d}f}g\n({ratio}× unprocessed)" if ratio else "Peaks at\nprocessed foods"

    bp = ax.boxplot(data, positions=range(4), widths=0.45, patch_artist=True,
                    showfliers=False, whis=[10, 90],
                    medianprops=dict(linewidth=2.5),
                    whiskerprops=dict(linewidth=1.1, linestyle="--"),
                    capprops=dict(linewidth=1.5),
                    boxprops=dict(linewidth=1.1))

    for patch, color in zip(bp["boxes"], COLORS):
        patch.set_facecolor(color + "30")
        patch.set_edgecolor(color)
    for median, color in zip(bp["medians"], COLORS):
        median.set_color(color)
    for whisker, color in zip(bp["whiskers"], np.repeat(COLORS, 2)):
        whisker.set_color(color)
    for cap, color in zip(bp["caps"], np.repeat(COLORS, 2)):
        cap.set_color(color)

    for i, arr in enumerate(data):
        med = np.median(arr)
        ax.text(i, med + ylim[1] * 0.015, f"{med:.{d}f}g",
                ha="center", va="bottom", fontsize=7.5,
                color=COLORS[i], fontweight="bold")

    ax.annotate(ct,
        xy=(cc, med_cc),
        xytext=(cc + 0.55, med_cc + ylim[1] * 0.18),
        fontsize=7.5, color=COLORS[cc],
        arrowprops=dict(arrowstyle="->", color=COLORS[cc], lw=1),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS[cc], lw=0.8))

    ax.set_ylim(ylim)
    ax.set_xticks(range(4))
    ax.set_xticklabels(LABELS, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(pt, fontsize=10, fontweight="bold", pad=6)
    ax.yaxis.set_major_locator(plt.MultipleLocator(yt))
    ax.grid(axis="y", color="#eeeeee", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

fig.suptitle("Ultra-processed foods are engineered around sugar and carbohydrates, not just fat",
             fontsize=13, fontweight="bold", x=0.02, ha="left", y=1.01)
fig.text(0.02, -0.04,
    "GroceryDB · 26,250 items across Walmart, Target, and Whole Foods · "
    "Boxes = IQR · Whiskers = P10–P90 · Values above P99 excluded per class",
    fontsize=7.5, color="#888888")
patches = [mpatches.Patch(color=COLORS[i], label=LABELS[i].replace("\n", " ")) for i in range(4)]
fig.legend(handles=patches, fontsize=8.5, frameon=False,
           loc="upper right", bbox_to_anchor=(1.0, 1.02), ncol=2)
plt.tight_layout()
plt.savefig("plot_nova_nutrients.png", dpi=180, bbox_inches="tight")
plt.close()
print("Saved plot_nova_nutrients.png")

# ── Individual sugar area chart ───────────────────────────────────────────────
col, ylabel, fname, color = "Sugars, total", "Sugar (g per 100g)", "plot_sugar.png", "#B863EC"
medians = []
for c in CLASSES:
    vals = df[df["FPro_class"] == c][col].dropna()
    cap = vals.quantile(0.99)
    medians.append(np.median(vals[vals <= cap]))

fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor("white")
ax.fill_between(range(4), medians, alpha=0.2, color=color)
ax.plot(range(4), medians, color=color, linewidth=2.5, marker="o", markersize=7, zorder=3)
for i, med in enumerate(medians):
    ax.text(i, med + max(medians) * 0.03, f"{med:.2f}g",
            ha="center", va="bottom", fontsize=9, color=color, fontweight="bold")
ax.set_title("Sugar content spikes in ultra-processed foods",
             fontsize=12, fontweight="bold", loc="left", pad=10)
ax.set_xticks(range(4))
ax.set_xticklabels(["Unprocessed", "Culinary\nIngredients", "Processed", "Ultra-\nProcessed"], fontsize=9)
ax.set_ylabel(ylabel, fontsize=10)
ax.set_ylim(0, max(medians) * 1.3)
ax.grid(axis="y", color="#eeeeee", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.text(0.12, -0.03,
    "GroceryDB · 26,250 items · Median sugar per NOVA class · Values above P99 excluded",
    fontsize=7.5, color="#888888")
plt.tight_layout()
plt.savefig("plot_sugar.png", dpi=180, bbox_inches="tight")
plt.close()
print("Saved plot_sugar.png")