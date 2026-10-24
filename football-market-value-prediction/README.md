# Predicting Footballer Market Values

A predictive modelling case study using FIFA 23 player attributes to investigate how skills, age, playing role, and potential relate to player market value. The project combines dimensionality reduction, player clustering, and regression, comparing pooled models with separate models for different playing roles.

**Tools:** R, RStudio

**Methods:** Principal Component Analysis (PCA), parallel analysis, varimax rotation, K-means clustering, linear regression, role-specific modelling, and residual analysis.

[Read the project presentation](./Predictive_modelling_Final.pdf)

## Questions

- Can 29 correlated skill ratings be summarized into a smaller set of interpretable dimensions?
- Do those dimensions reveal groups of players with similar skill profiles?
- Do role-specific regression models predict market value better than a pooled model?
- Which players have large differences between their recorded and predicted values?

## Data and preprocessing

The presentation describes a source dataset with 161,583 player records and 110 variables, then focuses the analysis on FIFA 23 outfield players with positive market value. That source count is not the number used to fit the models.

- Excluded goalkeepers and players with zero market value.
- Log-transformed market value to address its strongly right-skewed distribution.
- Used 3,000 players for modelling and 13,396 players for hold-out validation.
- Grouped playing positions into four functional roles: defenders (DEF), defensive midfielders (DM), midfielders (MID), and forwards (FWD).
- Examined 29 skill-related variables alongside age, position, and player potential.

## Workflow

### 1. Dimensionality reduction

Used parallel analysis to select four principal components from the 29 skill variables. The retained components explain **78.1% of variance**. Varimax rotation supported interpretation of the dimensions as technical ability, defending, pace, and physical ability.

### 2. Player clustering

Applied K-means to the reduced skill representation. Assessed the number of clusters using within-cluster sum of squares, silhouette scores, and NbClust voting. The four interpreted groups were technical midfielders, attackers, athletic full-backs / box-to-box players, and centre-backs.

The presentation reports **69% cluster purity against playing position**, compared with a **37% baseline**. Positions were not inputs to the clustering stage; this comparison was used to interpret the resulting groups.

### 3. Regression comparison

Compared seven model specifications, including an overall-rating baseline, pooled skill models, a PCA-based model, stepwise selection, and role-specific models with and without player potential.

| Model | Description |
| --- | --- |
| M1 | Overall-rating baseline |
| M2 | Pooled model using age, position, and 29 skills |
| M3 | Pooled model using four PCA dimensions |
| M4 | Stepwise version of the pooled model |
| M5 | M4 with player potential |
| M6 | Separate models by role using age and skills |
| M7 | Role-specific models with player potential |

The performance summary on slide 11 reports the following hold-out scores:

| Model | Reported hold-out R-squared |
| --- | ---: |
| M1: overall-rating baseline | 0.817 |
| M6: role-specific model without potential | 0.942 |
| M7: role-specific model with potential | 0.965 |

**Report discrepancy:** slide 12's predicted-versus-actual plot is annotated with hold-out R-squared = 0.94, while slide 11 and the conclusion report 0.965 for M7. The supplied presentation does not establish whether that plot shows M6 or a different evaluation. These values are reproduced as reported, rather than independently verified or reconciled. The exact evaluation scale should also be checked against the original analysis before reusing the final score.

### 4. Residual analysis

Compared recorded and predicted values to identify players priced above or below model estimates. These residuals support further investigation; they do not by themselves establish that branding, a transfer, or another specific factor caused the difference.

## Repository contents

| File | Purpose |
| --- | --- |
| [Predictive_modelling_Final.pdf](./Predictive_modelling_Final.pdf) | Original 15-slide project presentation |
| [README.md](./README.md) | Project overview, methods, reported results, and limitations |

This folder currently contains the presentation and documentation. The R scripts, dataset, fitted models, package versions, and train/validation split details have not been supplied, so the analysis cannot yet be reproduced from this folder alone.

## Team

- Khusinadha Naik
- Kamale Gautham
- Pratyush Panda

Predictive Modelling coursework, October 2026.
