"""
04_generate_figures.py

Generates dissertation figures for the Sudan-Chad
FLEE historical validation study.

Figures are created from the 30-run Topology V3 analysis.

Outputs:
1. Observed vs simulated refugee populations
2. Province-level percentage errors
3. Validation metrics by checkpoint
4. Stochastic uncertainty across 30 simulations
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[3]

SCENARIO = ROOT / "scenarios" / "sudan_chad"

OUTPUT_DIR = SCENARIO / "output"
FIGURES_DIR = SCENARIO / "figures"

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD ANALYSIS RESULTS
# =========================================================

checkpoint_file = (
    OUTPUT_DIR
    / "topology_v3_checkpoint_summary.csv"
)

summary_file = (
    OUTPUT_DIR
    / "topology_v3_30run_summary.csv"
)

metrics_file = (
    OUTPUT_DIR
    / "topology_v3_30run_metrics.csv"
)


for file in [
    checkpoint_file,
    summary_file,
    metrics_file,
]:
    if not file.exists():
        raise FileNotFoundError(
            f"Required analysis file not found: {file}"
        )


checkpoint = pd.read_csv(
    checkpoint_file
)

summary = pd.read_csv(
    summary_file
)

metrics = pd.read_csv(
    metrics_file
)


# =========================================================
# DISPLAY SETTINGS
# =========================================================

province_labels = {
    "Ouaddai": "Ouaddaï",
    "Sila": "Sila",
    "Wadi_Fira": "Wadi Fira",
}

date_labels = {
    "2023-07-03": "3 July 2023",
    "2023-09-06": "6 September 2023",
}


# =========================================================
# FIGURE 1
# OBSERVED VS SIMULATED
# =========================================================

plot_data = checkpoint.copy()

plot_data["Label"] = (
    plot_data["Province"].map(
        province_labels
    )
    + "\n"
    + plot_data["Date"].map(
        date_labels
    )
)

x = np.arange(
    len(plot_data)
)

width = 0.36


plt.figure(
    figsize=(12, 6)
)

plt.bar(
    x - width / 2,
    plot_data["UNHCR_observed"],
    width,
    label="UNHCR observed",
)

plt.bar(
    x + width / 2,
    plot_data["FLEE_mean"],
    width,
    label="FLEE mean (30 runs)",
)

plt.xticks(
    x,
    plot_data["Label"],
    rotation=20,
    ha="right",
)

plt.ylabel(
    "Refugee population"
)

plt.title(
    "Observed and Simulated Refugee Distribution"
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()

figure1 = (
    FIGURES_DIR
    / "figure_1_observed_vs_simulated.png"
)

plt.savefig(
    figure1,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# =========================================================
# FIGURE 2
# PROVINCE-LEVEL ABSOLUTE PERCENTAGE ERROR
# =========================================================

plt.figure(
    figsize=(10, 6)
)


for date in checkpoint["Date"].unique():

    data = checkpoint[
        checkpoint["Date"] == date
    ]

    plt.plot(
        [
            province_labels[p]
            for p in data["Province"]
        ],
        data[
            "Absolute_error_percent"
        ],
        marker="o",
        linewidth=2,
        label=date_labels[date],
    )


plt.ylabel(
    "Absolute percentage error (%)"
)

plt.xlabel(
    "Province"
)

plt.title(
    "Province-Level FLEE Validation Error"
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()

figure2 = (
    FIGURES_DIR
    / "figure_2_province_error.png"
)

plt.savefig(
    figure2,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# =========================================================
# FIGURE 3
# WAPE ACROSS HISTORICAL CHECKPOINTS
# =========================================================

plt.figure(
    figsize=(8, 6)
)

x_labels = [
    date_labels[d]
    for d in summary["Date"]
]

plt.bar(
    x_labels,
    summary[
        "WAPE_mean_percent"
    ],
    yerr=summary[
        "WAPE_sd_percent"
    ],
    capsize=6,
)

plt.ylabel(
    "WAPE (%)"
)

plt.xlabel(
    "Historical validation checkpoint"
)

plt.title(
    "Mean Validation Error Across 30 FLEE Runs"
)

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()

figure3 = (
    FIGURES_DIR
    / "figure_3_wape_comparison.png"
)

plt.savefig(
    figure3,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# =========================================================
# FIGURE 4
# STOCHASTIC VARIATION AT 6 SEPTEMBER
# =========================================================

september = metrics[
    metrics["Date"]
    == "2023-09-06"
].copy()


provinces = [
    "Ouaddai",
    "Sila",
    "Wadi_Fira",
]


means = []

stds = []

observed = []


for province in provinces:

    means.append(
        september[
            f"{province}_simulated"
        ].mean()
    )

    stds.append(
        september[
            f"{province}_simulated"
        ].std()
    )

    observed.append(
        september[
            f"{province}_observed"
        ].iloc[0]
    )


x = np.arange(
    len(provinces)
)


plt.figure(
    figsize=(9, 6)
)

plt.errorbar(
    x,
    means,
    yerr=stds,
    marker="o",
    linestyle="none",
    capsize=8,
    label="FLEE mean ± SD",
)

plt.scatter(
    x,
    observed,
    marker="x",
    s=90,
    label="UNHCR observed",
)

plt.xticks(
    x,
    [
        province_labels[p]
        for p in provinces
    ],
)

plt.ylabel(
    "Refugee population"
)

plt.title(
    "Stochastic Variation Across 30 Runs — 6 September 2023"
)

plt.legend()

plt.grid(
    axis="y",
    alpha=0.25,
)

plt.tight_layout()

figure4 = (
    FIGURES_DIR
    / "figure_4_stochastic_uncertainty.png"
)

plt.savefig(
    figure4,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

# =========================================================
# FIGURE 5
# SENSITIVITY OF WAPE TO MODEL ASSUMPTIONS
# =========================================================

sensitivity_file = (
    OUTPUT_DIR
    / "sensitivity_summary.csv"
)

if not sensitivity_file.exists():
    raise FileNotFoundError(
        f"Sensitivity results not found: {sensitivity_file}"
    )

sensitivity = pd.read_csv(
    sensitivity_file
)

# Remove baseline because the figure shows change relative to baseline.
sensitivity = sensitivity[
    sensitivity["Scenario"] != "baseline_v3"
].copy()


scenario_labels = {
    "el_geneina_minus20": "El Geneina -20%",
    "el_geneina_plus20": "El Geneina +20%",
    "foro_baranga_minus20": "Foro Baranga -20%",
    "foro_baranga_plus20": "Foro Baranga +20%",
    "kulbus_minus20": "Kulbus -20%",
    "kulbus_plus20": "Kulbus +20%",
    "routes_minus20": "All routes -20%",
    "routes_plus20": "All routes +20%",
}


scenario_order = [
    "el_geneina_minus20",
    "el_geneina_plus20",
    "foro_baranga_minus20",
    "foro_baranga_plus20",
    "kulbus_minus20",
    "kulbus_plus20",
    "routes_minus20",
    "routes_plus20",
]


july = (
    sensitivity[
        sensitivity["Date"] == "2023-07-03"
    ]
    .set_index("Scenario")
    .loc[scenario_order]
)

september = (
    sensitivity[
        sensitivity["Date"] == "2023-09-06"
    ]
    .set_index("Scenario")
    .loc[scenario_order]
)


labels = [
    scenario_labels[s]
    for s in scenario_order
]

y = np.arange(
    len(labels)
)

height = 0.36


plt.figure(
    figsize=(11, 7)
)

plt.barh(
    y - height / 2,
    july["WAPE_change_vs_baseline"],
    height,
    label="3 July 2023",
)

plt.barh(
    y + height / 2,
    september["WAPE_change_vs_baseline"],
    height,
    label="6 September 2023",
)

plt.axvline(
    0,
    linewidth=1,
)

plt.yticks(
    y,
    labels,
)

plt.xlabel(
    "Change in WAPE relative to baseline (percentage points)"
)

plt.ylabel(
    "Sensitivity scenario"
)

plt.title(
    "Sensitivity of FLEE Validation Error to Model Assumptions"
)

plt.legend()

plt.grid(
    axis="x",
    alpha=0.25,
)

plt.tight_layout()


figure5 = (
    FIGURES_DIR
    / "figure_5_sensitivity_analysis.png"
)

plt.savefig(
    figure5,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

# =========================================================
# COMPLETION SUMMARY
# =========================================================

print()
print("=" * 70)
print("DISSERTATION FIGURES GENERATED")
print("=" * 70)

print()
print("Figure 1:")
print(figure1)

print()
print("Figure 2:")
print(figure2)

print()
print("Figure 3:")
print(figure3)

print()
print("Figure 4:")
print(figure4)

print()

print(
    "All figures saved at 300 DPI."
)

print(
    "Figure generation completed successfully."
)

print("=" * 70)

print()
print("Figure 5:")
print(figure5)