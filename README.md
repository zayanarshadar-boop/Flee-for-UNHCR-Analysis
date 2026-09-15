# Historical Validation of FLEE for Sudan–Chad Displacement

## Project Overview

This repository contains the computational work developed for an MSc Data Science dissertation evaluating the historical performance of the **FLEE agent-based forced-displacement modelling framework** during the 2023 Sudan conflict.

The study investigates whether FLEE can reproduce historically observed displacement patterns from Sudan into eastern Chad using publicly available humanitarian displacement data, primarily from UNHCR.

The dissertation-specific implementation is located at:

```text
scenarios/sudan_chad/
```

The wider repository also contains the FLEE framework required to run and reproduce the simulations.

---

## Research Focus

The study evaluates simulated refugee distributions across three eastern Chad destination regions:

- Ouaddaï
- Sila
- Wadi Fira

Two historical validation checkpoints are used:

- **3 July 2023**
- **6 September 2023**

The final model configuration is referred to as **Topology V3**.

The analysis focuses primarily on the spatial distribution of displaced populations across destination regions.

---

## Final Model Structure

Topology V3 represents three conflict-origin proxies in western Sudan and three corresponding displacement pathways into eastern Chad:

```text
El Geneina   -> Adre -> Ouaddai
Foro Baranga -> Ade  -> Sila
Kulbus       -> Tine -> Wadi Fira
```

The Sudanese origin locations are modelled as conflict zones.

The Chad destination nodes use deliberately high, non-binding modelling capacities so that final historical validation observations are not used as model constraints.

This prevents target leakage during validation.

---

## Dissertation Project Location

The dissertation-specific files are located in:

```text
scenarios/sudan_chad/
```

The main project structure is:

```text
scenarios/sudan_chad/
│
├── README.md
├── simsetting.yml
│
├── input_csv_topology_v3/
│   ├── locations.csv
│   ├── routes.csv
│   ├── conflicts.csv
│   ├── closures.csv
│   └── sim_period.csv
│
├── source_data_province/
│   ├── data_layout.csv
│   ├── total.csv
│   ├── Ouaddai.csv
│   ├── Sila.csv
│   └── Wadi_Fira.csv
│
├── scripts/
│   ├── 01_build_model.py
│   ├── 02_run_experiments.py
│   ├── 03_analyse_results.py
│   └── 04_generate_figures.py
│
├── output/
├── figures/
├── sensitivity_models/
└── raw_data/
```

---

## Main Analysis Pipeline

The dissertation workflow consists of four main Python scripts.

### 1. Build the Model

```bash
python scenarios/sudan_chad/scripts/01_build_model.py
```

This script constructs the final Topology V3 configuration, including:

- conflict-origin locations
- displacement pathways
- destination nodes
- conflict schedules
- simulation period
- non-binding destination capacities

---

### 2. Run the Experiments

```bash
python scenarios/sudan_chad/scripts/02_run_experiments.py
```

This script performs:

- 30 seeded baseline FLEE simulations
- 8 sensitivity scenarios
- 10 seeds for each sensitivity scenario

The baseline simulations use seeds:

```text
1001–1030
```

The sensitivity analysis contains:

```text
8 scenarios × 10 seeds = 80 simulations
```

---

### 3. Analyse the Results

```bash
python scenarios/sudan_chad/scripts/03_analyse_results.py
```

This script compares simulated and historical observations and calculates:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Percentage Error (MAPE)
- Weighted Absolute Percentage Error (WAPE)
- stochastic mean and standard deviation
- province-level errors
- checkpoint comparisons
- sensitivity-analysis results

A one-day date alignment correction is applied during analysis because of the way the installed FLEE runner records simulation dates.

The original simulation outputs are preserved.

---

### 4. Generate Dissertation Figures

```bash
python scenarios/sudan_chad/scripts/04_generate_figures.py
```

This generates the main dissertation figures at 300 DPI.

The figures are stored in:

```text
scenarios/sudan_chad/figures/
```

The main figures are:

```text
figure_1_observed_vs_simulated.png
figure_2_province_error.png
figure_3_wape_comparison.png
figure_4_stochastic_uncertainty.png
figure_5_sensitivity_analysis.png
```

---

## Historical Validation Data

The core historical validation dataset is located in:

```text
scenarios/sudan_chad/source_data_province/
```

### 3 July 2023

| Region | Observed population |
|---|---:|
| Ouaddaï | 138,653 |
| Sila | 47,280 |
| Wadi Fira | 6,540 |
| Total | 192,473 |

### 6 September 2023

| Region | Observed population |
|---|---:|
| Ouaddaï | 319,545 |
| Sila | 63,808 |
| Wadi Fira | 28,983 |
| Total | 412,336 |

The simulation period begins on:

```text
15 April 2023
```

and the final validation date is:

```text
6 September 2023
```

---

## Baseline Validation Results

Thirty stochastic baseline simulations were performed.

### 3 July 2023

Mean WAPE:

```text
27.43%
```

### 6 September 2023

Mean WAPE:

```text
9.22%
```

The September checkpoint therefore showed substantially closer agreement between simulated and observed spatial distributions than the July checkpoint.

The September province-level percentage errors were approximately:

```text
Ouaddai     5.22%
Sila       29.80%
Wadi Fira   8.03%
```

Sila remained the main source of residual model error.

The stochastic standard deviations across the 30 runs were small relative to the simulated populations, indicating that most remaining disagreement is associated with model structure and assumptions rather than random simulation variation.

---

## Sensitivity Analysis

Sensitivity testing was conducted for:

```text
El Geneina population -20%
El Geneina population +20%

Foro Baranga population -20%
Foro Baranga population +20%

Kulbus population -20%
Kulbus population +20%

All route distances -20%
All route distances +20%
```

The results indicate that model performance is considerably more sensitive to assumptions about the relative populations of the conflict-origin locations than to moderate changes in route distances.

The sensitivity scenarios are used to evaluate model robustness and should not be interpreted as post-hoc parameter calibration.

---

## Important Methodological Note

An earlier model configuration used final historical destination values as destination capacities.

Although this produced apparently low validation error, the configuration was identified as a potential case of **target leakage**, because validation information had effectively been introduced into the model.

That configuration is retained only as a diagnostic comparison and is not used as the final validation result.

The final Topology V3 model uses non-binding destination capacities instead.

---

## Reproducibility

The analysis was developed using Python 3.12 within Ubuntu 24.04 under WSL2.

Environment information and the FLEE source commit used during the study are stored within:

```text
scenarios/sudan_chad/
```

Relevant files include:

```text
python_version.txt
flee_commit.txt
```

The project is designed so that the main dissertation workflow can be reproduced using the four scripts listed above.

---

## Interpretation

This project should be interpreted as a **historical validation study**, not as an independent forecast of the total number of displaced people.

In the historical-validation configuration, observed displacement totals contribute to the number of simulated agents entering the model.

The principal validation question is therefore whether FLEE reproduces the observed **spatial allocation of displaced populations across destination regions**.

---

## Data and Ethics

The study uses secondary, publicly available, aggregated humanitarian data.

No human participants, interviews, questionnaires, interventions, personal data, or identifiable individual-level information are used.

---

## Dissertation

**Programme:** MSc Data Science  
**Module:** CS5500 Dissertation

**Project title:**

> Historical Validation of the FLEE Toolkit for Modelling Conflict-Driven Displacement: A Hindsight Analysis of the Sudan Displacement Crisis

**Student:** Syed Zayan Arshad

---

## FLEE Framework

This dissertation builds upon the open-source **FLEE** forced-displacement simulation framework.

The repository contains the FLEE framework alongside the dissertation-specific Sudan–Chad scenario so that the analysis can be reproduced using the same modelling environment.

The original FLEE project is developed and maintained independently by its authors and contributors.
