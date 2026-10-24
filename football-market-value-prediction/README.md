# Predicting Footballer Market Values

A predictive modelling case study using FIFA 23 player attributes to investigate how skills, age, playing role, and potential relate to player market value. The R analysis combines dimensionality reduction, player clustering, regression comparison, and residual diagnostics.

**Tools:** R, RStudio, psych, MASS, cluster; optional NbClust and olsrr.

**Methods:** PCA, factor analysis, parallel analysis, varimax rotation, K-means, hierarchical clustering, linear regression, backward AIC selection, and influence diagnostics.

[Read the presentation](./Predictive_modelling_Final.pdf) | [View the analysis](./main.R)

## Data and preprocessing

The presentation describes a source dataset with 161,583 records and 110 variables. The script filters this multi-edition dataset to FIFA 23, excludes goalkeepers and players with missing or non-positive market value, and uses 29 detailed skill ratings rather than the six aggregate skill categories.

- Log-transformed market value to address its right-skewed distribution.
- Constructed age-squared and four functional roles: DEF, DM, MID, and FWD.
- Sampled 3,000 players for analysis using a fixed random seed.
- Reserved the remaining 13,396 players for hold-out evaluation in the reported run.
- Estimated skill-centering and scaling parameters from the analysis sample and reused them for hold-out regression data.

The dataset is not included. The original input is the Kaggle FIFA 15-23 file described in the script as `male_players (legacy).csv`, renamed locally to `male_players_legacy.csv`.

## Analysis workflow

### Dimensionality reduction

Compared unrotated PCA, varimax-rotated PCA, and principal-axis factor analysis using `psych`. Parallel analysis supported four principal components. The presentation reports that those components retain **78.1% of skill variance**, interpreted as technical ability, defending, pace, and physical ability. Factor congruence compares the PCA and factor-analysis solutions.

### Player clustering

Standardized the component scores and assessed K-means cluster counts using within-cluster sum of squares, silhouette widths, and optional NbClust voting. Four clusters were chosen for football interpretation, including a distinction between centre-backs and athletic full-backs; this was not simply the automatic winner of every selection criterion.

The presentation reports **69% purity against playing role**, compared with a **37% majority-role baseline**. Positions are not used as clustering inputs. The script also compares hierarchical linkage on a 60-player subsample and uses an LDA projection to visualize the K-means assignments. Its comments note that this projection emphasizes separation and does not establish naturally distinct player populations.

### Regression comparison

Compared seven model specifications using `lm()` and `MASS::stepAIC()`:

| Model | Description |
| --- | --- |
| M1 | Overall-rating baseline |
| M2 | Pooled age, age-squared, position, and 29 skills |
| M3 | Pooled age, age-squared, position, and four PCA dimensions |
| M4 | Backward AIC selection from M2 |
| M5 | M4 with player potential |
| M6 | Separate age, age-squared, and skill models for each role |
| M7 | Role-specific models with player potential |

The script calculates train R-squared, hold-out R-squared, and hold-out RMSE on **natural-log market value**. These R-squared scores are not raw-euro prediction accuracy percentages.

| Model | Hold-out R-squared reported in the presentation |
| --- | ---: |
| M1: overall-rating baseline | 0.817 |
| M6: role-specific model without potential | 0.942 |
| M7: role-specific model with potential | 0.965 |

**Plot clarification:** the presentation's prediction scatterplot is annotated 0.94 because `A_08_actual_vs_predicted` in `main.R` plots M6, using `model_compare$test_R2[6]`. The final score 0.965 refers to M7. The code resolves the apparent mismatch between the model-comparison slide and scatterplot, but the numerical results have not been independently rerun here because the dataset was not supplied.

### Residual and influence analysis

Examined marginal skill correlations versus conditional regression coefficients, variance inflation factors, standardized and studentized residuals, Q-Q plots, Shapiro-Wilk testing, Cook's distance, leverage, and DFFITS. Used M6's fitted residuals to rank players valued above or below the skill-and-age model's estimates, and examined relationships with omitted attributes such as potential.

These residuals describe model discrepancies; they do not prove that branding, transfers, or other specific causes explain a player's valuation. Exponentiating a fitted log value also does not automatically provide an unbiased conditional mean in euros.

## Run locally

1. Install R. RStudio is optional but provides plot previews.
2. Install the required packages once:

```r
install.packages(c("psych", "MASS", "cluster"))
```

3. Optionally install the additional cluster-selection and diagnostic packages:

```r
install.packages(c("NbClust", "olsrr"))
```

4. Put the dataset in this folder as `male_players_legacy.csv`. If it is absent, the script offers a file-selection dialog.
5. Set the working directory to this folder and run in a fresh R session:

```r
source("main.R", echo = TRUE)
```

Or, when the CSV is already in this folder:

```sh
Rscript main.R
```

Figures are exported to `fifa_plots/`, with `A_` names for presentation figures and `B_` names for supporting diagnostics. Tables and summary metrics print to the console. The script can disable on-screen previews if the RStudio plot pane is too small while continuing PNG export.

The committed script uses the resolved `csv_path` in `read.csv()`, so the fallback chooser is used only when needed. The statistical workflow is otherwise preserved from the supplied coursework script. Exact package versions and the source dataset are not included.

## Files

| File | Purpose |
| --- | --- |
| [main.R](./main.R) | Full analysis and figure-generation script |
| [Predictive_modelling_Final.pdf](./Predictive_modelling_Final.pdf) | Original 15-slide presentation |
| [README.md](./README.md) | Methods, reported results, setup, and interpretation |

## Team

- Khusinadha Naik
- Kamale Gautham
- Pratyush Panda

Predictive Modelling coursework, October 2026.
