"""
03_analyse_results.py

Analyses the 30 seeded FLEE Topology V3 simulations.

The script:
1. Loads all 30 stochastic simulation outputs.
2. Corrects the identified one-day FLEE output-date offset.
3. Evaluates two historical UNHCR checkpoints:
      - 3 July 2023
      - 6 September 2023
4. Calculates:
      - MAE
      - RMSE
      - MAPE
      - WAPE
5. Calculates mean and standard deviation across 30 runs.
6. Calculates province-level simulated means and errors.
7. Saves detailed and summary CSV files for dissertation analysis.
"""

from pathlib import Path
import numpy as np
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[3]

SCENARIO = ROOT / "scenarios" / "sudan_chad"
OUTPUT_DIR = SCENARIO / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# ANALYSIS SETTINGS
# =========================================================

CHECKPOINTS = [
    "2023-07-03",
    "2023-09-06",
]

PROVINCES = [
    "Ouaddai",
    "Sila",
    "Wadi_Fira",
]

EXPECTED_RUNS = 30


# =========================================================
# FIND SIMULATION FILES
# =========================================================

files = sorted(
    OUTPUT_DIR.glob(
        "topology_v3_seed_10??_raw.csv"
    )
)

# Restrict specifically to seeds 1001-1030.
files = [
    f for f in files
    if 1001 <= int(f.stem.split("_")[3]) <= 1030
]

print()
print("=" * 70)
print("SUDAN-CHAD FLEE — TOPOLOGY V3")
print("30-RUN HISTORICAL VALIDATION ANALYSIS")
print("=" * 70)

print(f"\nSimulation files found: {len(files)}")


if len(files) != EXPECTED_RUNS:
    raise RuntimeError(
        f"Expected {EXPECTED_RUNS} simulation files "
        f"but found {len(files)}."
    )


# =========================================================
# ANALYSE EACH RUN
# =========================================================

detailed_rows = []


for file in files:

    seed = int(
        file.stem.split("_")[3]
    )

    df = pd.read_csv(file)

    # -----------------------------------------------------
    # Correct the one-day FLEE printed-date offset
    # -----------------------------------------------------

    df["Date"] = (
        pd.to_datetime(df["Date"])
        - pd.Timedelta(days=1)
    )

    df["Date"] = (
        df["Date"]
        .dt.strftime("%Y-%m-%d")
    )


    # -----------------------------------------------------
    # HISTORICAL CHECKPOINTS
    # -----------------------------------------------------

    for date in CHECKPOINTS:

        checkpoint = df[
            df["Date"] == date
        ]

        if len(checkpoint) != 1:
            raise RuntimeError(
                f"{file.name}: expected one row "
                f"for {date}, found {len(checkpoint)}"
            )

        row = checkpoint.iloc[0]


        observed = np.array(
            [
                row[f"{province} data"]
                for province in PROVINCES
            ],
            dtype=float,
        )

        simulated = np.array(
            [
                row[f"{province} sim"]
                for province in PROVINCES
            ],
            dtype=float,
        )


        difference = (
            simulated - observed
        )

        absolute_difference = (
            np.abs(difference)
        )


        # -------------------------------------------------
        # VALIDATION METRICS
        # -------------------------------------------------

        mae = np.mean(
            absolute_difference
        )

        rmse = np.sqrt(
            np.mean(
                difference ** 2
            )
        )

        valid = observed != 0

        mape = (
            np.mean(
                absolute_difference[valid]
                / observed[valid]
            )
            * 100
        )

        wape = (
            absolute_difference.sum()
            / observed.sum()
            * 100
        )


        # -------------------------------------------------
        # STORE DETAILED RESULTS
        # -------------------------------------------------

        result = {
            "Seed": seed,
            "Date": date,
        }


        for index, province in enumerate(
            PROVINCES
        ):

            obs = observed[index]
            sim = simulated[index]
            diff = difference[index]

            result[
                f"{province}_observed"
            ] = obs

            result[
                f"{province}_simulated"
            ] = sim

            result[
                f"{province}_difference"
            ] = diff

            result[
                f"{province}_percentage_error"
            ] = (
                abs(diff) / obs * 100
                if obs != 0
                else np.nan
            )


        result["MAE"] = mae
        result["RMSE"] = rmse
        result["MAPE_percent"] = mape
        result["WAPE_percent"] = wape


        detailed_rows.append(
            result
        )


# =========================================================
# CREATE DETAILED DATAFRAME
# =========================================================

results = pd.DataFrame(
    detailed_rows
)

results = results.sort_values(
    ["Date", "Seed"]
)


detailed_output = (
    OUTPUT_DIR
    / "topology_v3_30run_metrics.csv"
)

results.to_csv(
    detailed_output,
    index=False,
)


# =========================================================
# CREATE 30-RUN SUMMARY
# =========================================================

summary_rows = []


for date in CHECKPOINTS:

    data = results[
        results["Date"] == date
    ]


    summary = {
        "Date": date,
        "Runs": len(data),
    }


    # -----------------------------------------------------
    # PROVINCE SUMMARY
    # -----------------------------------------------------

    for province in PROVINCES:

        simulated_column = (
            f"{province}_simulated"
        )

        observed_column = (
            f"{province}_observed"
        )

        observed_value = (
            data[
                observed_column
            ].iloc[0]
        )

        simulated_mean = (
            data[
                simulated_column
            ].mean()
        )

        simulated_sd = (
            data[
                simulated_column
            ].std()
        )

        bias = (
            simulated_mean
            - observed_value
        )

        absolute_percentage_error = (
            abs(bias)
            / observed_value
            * 100
        )


        summary[
            f"{province}_observed"
        ] = observed_value

        summary[
            f"{province}_mean"
        ] = simulated_mean

        summary[
            f"{province}_sd"
        ] = simulated_sd

        summary[
            f"{province}_bias"
        ] = bias

        summary[
            f"{province}_error_percent"
        ] = absolute_percentage_error


    # -----------------------------------------------------
    # ERROR METRICS
    # -----------------------------------------------------

    summary["MAE_mean"] = (
        data["MAE"].mean()
    )

    summary["MAE_sd"] = (
        data["MAE"].std()
    )

    summary["RMSE_mean"] = (
        data["RMSE"].mean()
    )

    summary["RMSE_sd"] = (
        data["RMSE"].std()
    )

    summary["MAPE_mean_percent"] = (
        data["MAPE_percent"].mean()
    )

    summary["MAPE_sd_percent"] = (
        data["MAPE_percent"].std()
    )

    summary["WAPE_mean_percent"] = (
        data["WAPE_percent"].mean()
    )

    summary["WAPE_sd_percent"] = (
        data["WAPE_percent"].std()
    )


    summary_rows.append(
        summary
    )


summary_df = pd.DataFrame(
    summary_rows
)


summary_output = (
    OUTPUT_DIR
    / "topology_v3_30run_summary.csv"
)

summary_df.to_csv(
    summary_output,
    index=False,
)


# =========================================================
# CREATE HUMAN-READABLE CHECKPOINT TABLE
# =========================================================

checkpoint_rows = []


for date in CHECKPOINTS:

    data = results[
        results["Date"] == date
    ]


    for province in PROVINCES:

        observed = (
            data[
                f"{province}_observed"
            ].iloc[0]
        )

        mean_simulated = (
            data[
                f"{province}_simulated"
            ].mean()
        )

        sd_simulated = (
            data[
                f"{province}_simulated"
            ].std()
        )

        difference = (
            mean_simulated
            - observed
        )

        percentage_error = (
            abs(difference)
            / observed
            * 100
        )


        checkpoint_rows.append(
            {
                "Date": date,
                "Province": province,
                "UNHCR_observed": observed,
                "FLEE_mean": mean_simulated,
                "FLEE_SD": sd_simulated,
                "Difference": difference,
                "Absolute_error_percent":
                    percentage_error,
            }
        )


checkpoint_df = pd.DataFrame(
    checkpoint_rows
)


checkpoint_output = (
    OUTPUT_DIR
    / "topology_v3_checkpoint_summary.csv"
)

checkpoint_df.to_csv(
    checkpoint_output,
    index=False,
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

pd.set_option(
    "display.max_columns",
    None
)

pd.set_option(
    "display.width",
    220
)


print()
print("=" * 70)
print("CHECKPOINT RESULTS")
print("=" * 70)

print()

print(
    checkpoint_df.to_string(
        index=False,
        float_format=lambda x: f"{x:,.2f}",
    )
)


print()
print("=" * 70)
print("VALIDATION METRICS — 30 RUN MEAN")
print("=" * 70)

print()

metric_columns = [
    "Date",
    "Runs",
    "MAE_mean",
    "MAE_sd",
    "RMSE_mean",
    "RMSE_sd",
    "MAPE_mean_percent",
    "WAPE_mean_percent",
    "WAPE_sd_percent",
]

print(
    summary_df[
        metric_columns
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:,.3f}",
    )
)


print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print(
    "\nDetailed 30-run results:"
)

print(
    detailed_output
)

print(
    "\nSummary statistics:"
)

print(
    summary_output
)

print(
    "\nCheckpoint comparison:"
)

print(
    checkpoint_output
)

print()
print(
    "Next step: "
    "04_generate_figures.py"
)

print("=" * 70)

# =========================================================
# SENSITIVITY ANALYSIS
# =========================================================

print()
print("=" * 70)
print("SENSITIVITY ANALYSIS — 10 COMMON SEEDS")
print("=" * 70)

SENSITIVITY_SEEDS = range(1001, 1011)

manifest_file = (
    OUTPUT_DIR
    / "sensitivity_manifest.csv"
)

if not manifest_file.exists():
    raise FileNotFoundError(
        f"Sensitivity manifest not found: {manifest_file}"
    )

manifest = pd.read_csv(
    manifest_file
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def load_corrected_output(file_path):
    """
    Load a FLEE output file and correct the known one-day
    printed-date offset.
    """

    df = pd.read_csv(
        file_path
    )

    df["Date"] = (
        pd.to_datetime(df["Date"])
        - pd.Timedelta(days=1)
    )

    df["Date"] = (
        df["Date"]
        .dt.strftime("%Y-%m-%d")
    )

    return df


def calculate_checkpoint_metrics(
    row
):
    """
    Calculate province and aggregate validation metrics
    for a single historical checkpoint.
    """

    observed = np.array(
        [
            row[f"{province} data"]
            for province in PROVINCES
        ],
        dtype=float,
    )

    simulated = np.array(
        [
            row[f"{province} sim"]
            for province in PROVINCES
        ],
        dtype=float,
    )

    difference = (
        simulated - observed
    )

    absolute_difference = (
        np.abs(difference)
    )

    mae = (
        absolute_difference.mean()
    )

    rmse = np.sqrt(
        np.mean(
            difference ** 2
        )
    )

    valid = observed != 0

    mape = (
        np.mean(
            absolute_difference[valid]
            / observed[valid]
        )
        * 100
    )

    wape = (
        absolute_difference.sum()
        / observed.sum()
        * 100
    )

    result = {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE_percent": mape,
        "WAPE_percent": wape,
    }

    for index, province in enumerate(
        PROVINCES
    ):

        result[
            f"{province}_observed"
        ] = observed[index]

        result[
            f"{province}_simulated"
        ] = simulated[index]

        result[
            f"{province}_difference"
        ] = difference[index]

    return result


# =========================================================
# BASELINE USING THE SAME 10 SEEDS
# =========================================================

sensitivity_rows = []


for seed in SENSITIVITY_SEEDS:

    baseline_file = (
        OUTPUT_DIR
        / f"topology_v3_seed_{seed}_raw.csv"
    )

    if not baseline_file.exists():
        raise FileNotFoundError(
            baseline_file
        )

    df = load_corrected_output(
        baseline_file
    )

    for date in CHECKPOINTS:

        checkpoint = df[
            df["Date"] == date
        ]

        if len(checkpoint) != 1:
            raise RuntimeError(
                f"Baseline seed {seed}: "
                f"checkpoint {date} not found correctly."
            )

        metrics_row = (
            calculate_checkpoint_metrics(
                checkpoint.iloc[0]
            )
        )

        metrics_row.update(
            {
                "Scenario":
                    "baseline_v3",

                "Sensitivity_type":
                    "baseline",

                "Target":
                    "baseline",

                "Percentage_change":
                    0.0,

                "Seed":
                    seed,

                "Date":
                    date,
            }
        )

        sensitivity_rows.append(
            metrics_row
        )


# =========================================================
# LOAD ALL SENSITIVITY RUNS
# =========================================================

for _, scenario_info in manifest.iterrows():

    scenario = (
        scenario_info["Scenario"]
    )

    sensitivity_type = (
        scenario_info[
            "Sensitivity_type"
        ]
    )

    target = (
        scenario_info["Target"]
    )

    percentage_change = (
        scenario_info[
            "Percentage_change"
        ]
    )


    for seed in SENSITIVITY_SEEDS:

        sensitivity_file = (
            OUTPUT_DIR
            / (
                f"sensitivity_"
                f"{scenario}_"
                f"seed_{seed}_raw.csv"
            )
        )

        if not sensitivity_file.exists():
            raise FileNotFoundError(
                sensitivity_file
            )

        df = load_corrected_output(
            sensitivity_file
        )


        for date in CHECKPOINTS:

            checkpoint = df[
                df["Date"] == date
            ]

            if len(checkpoint) != 1:
                raise RuntimeError(
                    f"{scenario} seed {seed}: "
                    f"checkpoint {date} missing."
                )

            metrics_row = (
                calculate_checkpoint_metrics(
                    checkpoint.iloc[0]
                )
            )

            metrics_row.update(
                {
                    "Scenario":
                        scenario,

                    "Sensitivity_type":
                        sensitivity_type,

                    "Target":
                        target,

                    "Percentage_change":
                        percentage_change,

                    "Seed":
                        seed,

                    "Date":
                        date,
                }
            )

            sensitivity_rows.append(
                metrics_row
            )


# =========================================================
# DETAILED SENSITIVITY RESULTS
# =========================================================

sensitivity_results = pd.DataFrame(
    sensitivity_rows
)

sensitivity_results = (
    sensitivity_results.sort_values(
        [
            "Date",
            "Scenario",
            "Seed",
        ]
    )
)


sensitivity_detailed_file = (
    OUTPUT_DIR
    / "sensitivity_10run_metrics.csv"
)

sensitivity_results.to_csv(
    sensitivity_detailed_file,
    index=False,
)


# =========================================================
# SENSITIVITY SUMMARY
# =========================================================

summary_rows = []


for (
    scenario,
    date
), data in sensitivity_results.groupby(
    [
        "Scenario",
        "Date",
    ]
):

    scenario_first = (
        data.iloc[0]
    )

    summary_row = {
        "Scenario":
            scenario,

        "Date":
            date,

        "Runs":
            len(data),

        "Sensitivity_type":
            scenario_first[
                "Sensitivity_type"
            ],

        "Target":
            scenario_first[
                "Target"
            ],

        "Percentage_change":
            scenario_first[
                "Percentage_change"
            ],

        "MAE_mean":
            data["MAE"].mean(),

        "MAE_sd":
            data["MAE"].std(),

        "RMSE_mean":
            data["RMSE"].mean(),

        "RMSE_sd":
            data["RMSE"].std(),

        "MAPE_mean_percent":
            data[
                "MAPE_percent"
            ].mean(),

        "WAPE_mean_percent":
            data[
                "WAPE_percent"
            ].mean(),

        "WAPE_sd_percent":
            data[
                "WAPE_percent"
            ].std(),
    }


    for province in PROVINCES:

        summary_row[
            f"{province}_mean"
        ] = (
            data[
                f"{province}_simulated"
            ].mean()
        )

        summary_row[
            f"{province}_sd"
        ] = (
            data[
                f"{province}_simulated"
            ].std()
        )


    summary_rows.append(
        summary_row
    )


sensitivity_summary = pd.DataFrame(
    summary_rows
)


# =========================================================
# COMPARE EACH SCENARIO WITH BASELINE
# =========================================================

baseline_lookup = (
    sensitivity_summary[
        sensitivity_summary[
            "Scenario"
        ]
        == "baseline_v3"
    ]
    .set_index("Date")
)


def baseline_wape_for_date(
    date
):

    return baseline_lookup.loc[
        date,
        "WAPE_mean_percent",
    ]


sensitivity_summary[
    "Baseline_WAPE_percent"
] = (
    sensitivity_summary["Date"]
    .apply(
        baseline_wape_for_date
    )
)


sensitivity_summary[
    "WAPE_change_vs_baseline"
] = (
    sensitivity_summary[
        "WAPE_mean_percent"
    ]
    - sensitivity_summary[
        "Baseline_WAPE_percent"
    ]
)


sensitivity_summary[
    "Absolute_WAPE_change"
] = (
    sensitivity_summary[
        "WAPE_change_vs_baseline"
    ].abs()
)


sensitivity_summary = (
    sensitivity_summary.sort_values(
        [
            "Date",
            "Absolute_WAPE_change",
        ],
        ascending=[
            True,
            False,
        ],
    )
)


sensitivity_summary_file = (
    OUTPUT_DIR
    / "sensitivity_summary.csv"
)

sensitivity_summary.to_csv(
    sensitivity_summary_file,
    index=False,
)


# =========================================================
# PROVINCE-LEVEL SENSITIVITY SUMMARY
# =========================================================

province_rows = []


for (
    scenario,
    date
), data in sensitivity_results.groupby(
    [
        "Scenario",
        "Date",
    ]
):

    first = data.iloc[0]


    for province in PROVINCES:

        observed = (
            data[
                f"{province}_observed"
            ].iloc[0]
        )

        simulated_mean = (
            data[
                f"{province}_simulated"
            ].mean()
        )

        simulated_sd = (
            data[
                f"{province}_simulated"
            ].std()
        )

        bias = (
            simulated_mean
            - observed
        )

        absolute_error_percent = (
            abs(bias)
            / observed
            * 100
        )


        province_rows.append(
            {
                "Scenario":
                    scenario,

                "Date":
                    date,

                "Sensitivity_type":
                    first[
                        "Sensitivity_type"
                    ],

                "Target":
                    first[
                        "Target"
                    ],

                "Percentage_change":
                    first[
                        "Percentage_change"
                    ],

                "Province":
                    province,

                "UNHCR_observed":
                    observed,

                "FLEE_mean":
                    simulated_mean,

                "FLEE_SD":
                    simulated_sd,

                "Bias":
                    bias,

                "Absolute_error_percent":
                    absolute_error_percent,
            }
        )


province_sensitivity = pd.DataFrame(
    province_rows
)


province_sensitivity_file = (
    OUTPUT_DIR
    / "sensitivity_province_summary.csv"
)

province_sensitivity.to_csv(
    province_sensitivity_file,
    index=False,
)


# =========================================================
# DISPLAY SENSITIVITY RESULTS
# =========================================================

display_columns = [
    "Scenario",
    "Date",
    "Percentage_change",
    "MAE_mean",
    "RMSE_mean",
    "WAPE_mean_percent",
    "WAPE_change_vs_baseline",
]


print()
print("=" * 70)
print("SENSITIVITY SUMMARY")
print("=" * 70)
print()

print(
    sensitivity_summary[
        display_columns
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:,.3f}",
    )
)


# =========================================================
# RANK MOST INFLUENTIAL ASSUMPTIONS
# =========================================================

non_baseline = (
    sensitivity_summary[
        sensitivity_summary[
            "Scenario"
        ]
        != "baseline_v3"
    ]
)


for date in CHECKPOINTS:

    ranked = (
        non_baseline[
            non_baseline[
                "Date"
            ]
            == date
        ]
        .sort_values(
            "Absolute_WAPE_change",
            ascending=False,
        )
    )


    print()
    print(
        "=" * 70
    )

    print(
        f"MOST INFLUENTIAL ASSUMPTIONS — {date}"
    )

    print(
        "=" * 70
    )

    print()

    print(
        ranked[
            [
                "Scenario",
                "WAPE_mean_percent",
                "WAPE_change_vs_baseline",
                "Absolute_WAPE_change",
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:,.3f}",
        )
    )


# =========================================================
# COMPLETION
# =========================================================

print()
print("=" * 70)
print("SENSITIVITY ANALYSIS COMPLETE")
print("=" * 70)

print()
print("Detailed sensitivity runs:")
print(
    sensitivity_detailed_file
)

print()
print("Sensitivity summary:")
print(
    sensitivity_summary_file
)

print()
print("Province sensitivity summary:")
print(
    province_sensitivity_file
)

print()
print(
    "Next step: update "
    "04_generate_figures.py "
    "with the sensitivity figure."
)

print("=" * 70)