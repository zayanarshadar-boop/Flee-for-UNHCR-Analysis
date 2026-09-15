"""
01_build_model.py

Builds the Sudan-Chad FLEE Topology V3 scenario used for
historical validation.

The model contains three Sudanese conflict-origin proxies:
- El Geneina
- Foro Baranga
- Kulbus

These connect to three eastern Chad entry pathways:
- Adre -> Ouaddai
- Ade -> Sila
- Tine -> Wadi Fira

Province destination nodes use non-binding capacities so that
the final UNHCR validation observations are not leaked into the model.
"""

from pathlib import Path
from shutil import copytree


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]

SCENARIO = ROOT / "scenarios" / "sudan_chad"

BASE_INPUT = SCENARIO / "input_csv_clean"
MODEL_INPUT = SCENARIO / "input_csv_topology_v3"

OUTPUT_DIR = SCENARIO / "output"
FIGURES_DIR = SCENARIO / "figures"


# ---------------------------------------------------------
# CREATE REQUIRED DIRECTORIES
# ---------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

if BASE_INPUT.exists():
    copytree(
        BASE_INPUT,
        MODEL_INPUT,
        dirs_exist_ok=True,
    )
else:
    MODEL_INPUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# LOCATIONS
# ---------------------------------------------------------

locations = """#"name","region","country","lat","lon","location_type","conflict_date","population"
"El_Geneina","West_Darfur","Sudan",13.44200,22.44600,"conflict_zone",0,679249
"Foro_Baranga","West_Darfur","Sudan",12.12964,22.60643,"conflict_zone",0,90613
"Kulbus","West_Darfur","Sudan",14.36572,22.46143,"conflict_zone",0,63239
"Adre","Ouaddai","Chad",13.46670,22.20000,"marker",,0
"Ade","Sila","Chad",12.66667,21.90000,"marker",,0
"Tine","Wadi_Fira","Chad",15.01771,22.81857,"marker",,0
"Ouaddai","Ouaddai","Chad",13.58300,20.83300,"camp",,1000000
"Sila","Sila","Chad",12.22500,21.41400,"camp",,1000000
"Wadi_Fira","Wadi_Fira","Chad",15.11600,22.25000,"camp",,1000000
"""

(MODEL_INPUT / "locations.csv").write_text(
    locations,
    encoding="utf-8",
)


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

routes = """#"name1","name2","distance","forced_redirection"
"El_Geneina","Adre",27,0
"Foro_Baranga","Ade",97,0
"Kulbus","Tine",82,0
"Adre","Ouaddai",148,0
"Ade","Sila",72,0
"Tine","Wadi_Fira",62,0
"""

(MODEL_INPUT / "routes.csv").write_text(
    routes,
    encoding="utf-8",
)


# ---------------------------------------------------------
# CONFLICT SCHEDULE
# ---------------------------------------------------------

conflict_file = MODEL_INPUT / "conflicts.csv"

with conflict_file.open("w", encoding="utf-8") as f:
    f.write("#Day,El_Geneina,Foro_Baranga,Kulbus\n")

    for day in range(145):
        f.write(f"{day},1.0,1.0,1.0\n")


# ---------------------------------------------------------
# SIMULATION PERIOD
# ---------------------------------------------------------

simulation_period = """StartDate,2023-04-15
Length,145
"""

(MODEL_INPUT / "sim_period.csv").write_text(
    simulation_period,
    encoding="utf-8",
)


# ---------------------------------------------------------
# MODEL SUMMARY
# ---------------------------------------------------------

print()
print("=" * 60)
print("SUDAN-CHAD FLEE TOPOLOGY V3")
print("=" * 60)

print(f"\nProject root:")
print(ROOT)

print(f"\nModel input directory:")
print(MODEL_INPUT)

print("\nConflict origins:")
print("  El Geneina   population = 679,249")
print("  Foro Baranga population = 90,613")
print("  Kulbus       population = 63,239")

print("\nChad pathways:")
print("  El Geneina   -> Adre -> Ouaddai")
print("  Foro Baranga -> Ade  -> Sila")
print("  Kulbus       -> Tine -> Wadi Fira")

print("\nDestination capacities:")
print("  Ouaddai   = 1,000,000")
print("  Sila      = 1,000,000")
print("  Wadi Fira = 1,000,000")
print("  (non-binding modelling capacities)")

print("\nSimulation:")
print("  Start date = 2023-04-15")
print("  Days       = 145")
print("  Final validation date = 2023-09-06")

print()
print("Model construction completed successfully.")
print("=" * 60)