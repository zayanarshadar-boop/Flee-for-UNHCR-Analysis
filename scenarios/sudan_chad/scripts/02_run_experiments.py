"""
02_run_experiments.py

Runs the Sudan-Chad FLEE Topology V3 experiments.

Experiments:
1. Baseline model: 30 seeded stochastic runs.
2. One-at-a-time sensitivity analysis:
   - El Geneina population ±20%
   - Foro Baranga population ±20%
   - Kulbus population ±20%
   - Route distances ±20%

Sensitivity experiments use 10 common random seeds to reduce
the influence of stochastic variation when comparing scenarios.
"""

from pathlib import Path
from shutil import copytree, rmtree
import csv
import os
import random
import runpy
import subprocess
import sys

import numpy as np


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[3]

SCENARIO = ROOT / "scenarios" / "sudan_chad"

BASELINE_INPUT = (
    SCENARIO / "input_csv_topology_v3"
)

DATA_DIR = (
    SCENARIO / "source_data_province"
)

SETTINGS_FILE = (
    SCENARIO / "simsetting.yml"
)

OUTPUT_DIR = (
    SCENARIO / "output"
)

SENSITIVITY_DIR = (
    SCENARIO / "sensitivity_models"
)

FLEE_RUNNER = (
    ROOT / "runscripts" / "run.py"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SENSITIVITY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# RANDOM SEEDS
# =========================================================

BASELINE_SEEDS = range(
    1001,
    1031,
)

SENSITIVITY_SEEDS = range(
    1001,
    1011,
)


# =========================================================
# SEEDED RUNNER
# =========================================================

SEEDED_RUNNER = r"""
import random
import runpy
import sys
import numpy as np

seed = int(sys.argv[1])

random.seed(seed)
np.random.seed(seed)

runner = sys.argv[5]

sys.argv = [
    runner,
    sys.argv[2],
    sys.argv[3],
    "0",
    sys.argv[4],
]

runpy.run_path(
    runner,
    run_name="__main__"
)
"""


# =========================================================
# PYTHON ENVIRONMENT
# =========================================================

env = os.environ.copy()

existing_pythonpath = env.get(
    "PYTHONPATH",
    ""
)

if existing_pythonpath:

    env["PYTHONPATH"] = (
        f"{ROOT}"
        f"{os.pathsep}"
        f"{existing_pythonpath}"
    )

else:

    env["PYTHONPATH"] = str(ROOT)


# =========================================================
# RUN ONE FLEE EXPERIMENT
# =========================================================

def run_flee(
    input_dir,
    output_file,
    seed,
):
    """
    Execute one reproducible seeded FLEE run.
    """

    command = [
        sys.executable,
        "-c",
        SEEDED_RUNNER,
        str(seed),
        str(input_dir),
        str(DATA_DIR),
        str(SETTINGS_FILE),
        str(FLEE_RUNNER),
    ]

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as output:

        result = subprocess.run(
            command,
            stdout=output,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT,
            env=env,
        )

    if result.returncode != 0:

        print(result.stderr)

        raise RuntimeError(
            f"FLEE failed for seed {seed}"
        )


# =========================================================
# BASELINE 30-RUN EXPERIMENT
# =========================================================

print()
print("=" * 70)
print("FLEE TOPOLOGY V3 EXPERIMENT PIPELINE")
print("=" * 70)

print()
print("Checking 30-run baseline...")


for seed in BASELINE_SEEDS:

    output_file = (
        OUTPUT_DIR
        / f"topology_v3_seed_{seed}_raw.csv"
    )

    # Do not rerun completed simulations.
    if (
        output_file.exists()
        and output_file.stat().st_size > 0
    ):

        print(
            f"Baseline seed {seed}: "
            f"already exists — skipped"
        )

        continue

    print(
        f"Running baseline seed {seed}..."
    )

    run_flee(
        BASELINE_INPUT,
        output_file,
        seed,
    )


print()
print("Baseline complete.")


# =========================================================
# HELPER — CREATE MODEL COPY
# =========================================================

def create_model_copy(
    model_name,
):
    """
    Create a clean sensitivity model copied from V3.
    """

    destination = (
        SENSITIVITY_DIR / model_name
    )

    if destination.exists():
        rmtree(destination)

    copytree(
        BASELINE_INPUT,
        destination,
    )

    return destination


# =========================================================
# HELPER — ALTER ORIGIN POPULATION
# =========================================================

def modify_population(
    model_dir,
    location_name,
    multiplier,
):
    """
    Change one conflict-origin population while leaving
    all other model parameters unchanged.
    """

    file = (
        model_dir / "locations.csv"
    )

    lines = file.read_text(
        encoding="utf-8"
    ).splitlines()

    new_lines = []

    found = False

    for line in lines:

        if line.startswith(
            f'"{location_name}",'
        ):

            parts = line.split(",")

            old_population = int(
                parts[-1]
            )

            new_population = int(
                round(
                    old_population
                    * multiplier
                )
            )

            parts[-1] = str(
                new_population
            )

            line = ",".join(parts)

            found = True

            print(
                f"{location_name}: "
                f"{old_population:,} -> "
                f"{new_population:,}"
            )

        new_lines.append(line)

    if not found:

        raise RuntimeError(
            f"Location not found: "
            f"{location_name}"
        )

    file.write_text(
        "\n".join(new_lines) + "\n",
        encoding="utf-8",
    )


# =========================================================
# HELPER — ALTER ROUTE DISTANCES
# =========================================================

def modify_route_distances(
    model_dir,
    multiplier,
):
    """
    Scale every route distance by a common factor.
    """

    file = (
        model_dir / "routes.csv"
    )

    lines = file.read_text(
        encoding="utf-8"
    ).splitlines()

    new_lines = [
        lines[0]
    ]

    for line in lines[1:]:

        if not line.strip():
            continue

        parts = line.split(",")

        old_distance = float(
            parts[2]
        )

        new_distance = int(
            round(
                old_distance
                * multiplier
            )
        )

        parts[2] = str(
            new_distance
        )

        new_lines.append(
            ",".join(parts)
        )

    file.write_text(
        "\n".join(new_lines) + "\n",
        encoding="utf-8",
    )


# =========================================================
# DEFINE SENSITIVITY SCENARIOS
# =========================================================

sensitivity_scenarios = [
    (
        "el_geneina_minus20",
        "population",
        "El_Geneina",
        0.80,
    ),
    (
        "el_geneina_plus20",
        "population",
        "El_Geneina",
        1.20,
    ),
    (
        "foro_baranga_minus20",
        "population",
        "Foro_Baranga",
        0.80,
    ),
    (
        "foro_baranga_plus20",
        "population",
        "Foro_Baranga",
        1.20,
    ),
    (
        "kulbus_minus20",
        "population",
        "Kulbus",
        0.80,
    ),
    (
        "kulbus_plus20",
        "population",
        "Kulbus",
        1.20,
    ),
    (
        "routes_minus20",
        "routes",
        None,
        0.80,
    ),
    (
        "routes_plus20",
        "routes",
        None,
        1.20,
    ),
]


# =========================================================
# MANIFEST
# =========================================================

manifest_rows = []


# =========================================================
# RUN SENSITIVITY EXPERIMENTS
# =========================================================

print()
print("=" * 70)
print("SENSITIVITY ANALYSIS")
print("=" * 70)


for (
    scenario_name,
    sensitivity_type,
    target,
    multiplier,
) in sensitivity_scenarios:

    print()
    print("-" * 70)
    print(
        f"Scenario: {scenario_name}"
    )
    print("-" * 70)

    model_dir = create_model_copy(
        scenario_name
    )

    if sensitivity_type == "population":

        modify_population(
            model_dir,
            target,
            multiplier,
        )

    elif sensitivity_type == "routes":

        modify_route_distances(
            model_dir,
            multiplier,
        )

    else:

        raise RuntimeError(
            "Unknown sensitivity type"
        )


    manifest_rows.append(
        {
            "Scenario":
                scenario_name,

            "Sensitivity_type":
                sensitivity_type,

            "Target":
                target
                if target
                else "all_routes",

            "Multiplier":
                multiplier,

            "Percentage_change":
                (multiplier - 1)
                * 100,
        }
    )


    for seed in SENSITIVITY_SEEDS:

        output_file = (
            OUTPUT_DIR
            / (
                f"sensitivity_"
                f"{scenario_name}_"
                f"seed_{seed}_raw.csv"
            )
        )

        print(
            f"  Seed {seed}..."
        )

        run_flee(
            model_dir,
            output_file,
            seed,
        )


# =========================================================
# SAVE SENSITIVITY MANIFEST
# =========================================================

manifest_file = (
    OUTPUT_DIR
    / "sensitivity_manifest.csv"
)

with manifest_file.open(
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Scenario",
            "Sensitivity_type",
            "Target",
            "Multiplier",
            "Percentage_change",
        ],
    )

    writer.writeheader()

    writer.writerows(
        manifest_rows
    )


# =========================================================
# COMPLETION
# =========================================================

print()
print("=" * 70)
print("ALL EXPERIMENTS COMPLETE")
print("=" * 70)

print()
print(
    "Baseline runs:"
)
print(
    "  30 seeded simulations"
)

print()
print(
    "Sensitivity scenarios:"
)
print(
    f"  {len(sensitivity_scenarios)}"
)

print()
print(
    "Sensitivity runs:"
)
print(
    f"  {len(sensitivity_scenarios) * len(list(SENSITIVITY_SEEDS))}"
)

print()
print(
    "Sensitivity manifest:"
)
print(
    manifest_file
)

print()
print(
    "Next step:"
)
print(
    "Run 03_analyse_results.py "
    "after adding sensitivity analysis."
)

print("=" * 70)