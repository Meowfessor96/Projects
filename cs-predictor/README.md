# CS2 Predictive Engine v5

Predicts CS:GO / CS2 map winners from real HLTV-scraped professional
match data. Pure-Python, runs in a single Jupyter notebook.

---

## Results at a glance

Held-out test set (299 matches, Dec 2019 – Mar 2020):

| Metric                                      | Value                            |
| ------------------------------------------- | -------------------------------- |
| Accuracy                                    | **61.9%**                  |
| Brier score                                 | 0.2364                           |
| Log loss                                    | 0.6653                           |
| ROC AUC                                     | 0.633                            |
| Rank-only baseline                          | 57.5%                            |
| Random baseline                             | 50.0%                            |
| Best single ablation                        | rank + win-rate =**62.9%** |
| Champion Brier (Monte Carlo, full test set) | **0.0454**                 |

Monte Carlo champion predictions:

| Scenario                      | Matches | Actual champion | Predicted champion | P(champ) | Champion Brier | Pearson r |
| ----------------------------- | ------- | --------------- | ------------------ | -------- | -------------- | --------- |
| Full test set                 | 299     | G2              | mousesports        | 69.1%    | 0.0454         | 0.932     |
| Event 4901                    | 70      | Natus Vincere   | Natus Vincere      | 61.4%    | 0.0112         | 0.904     |
| Verification slice (last 150) | 150     | Natus Vincere   | Natus Vincere      | 86.0%    | 0.0012         | 0.924     |

Round-robin season simulation (28 common teams, 1000 seasons ×
378 matches = 378,000 simulated matches):

| Rank | Team          | Mean wins | Std  | P(1st place) |
| ---- | ------------- | --------- | ---- | ------------ |
| 1    | Astralis      | 17.77     | 2.37 | 35.7%        |
| 2    | Liquid        | 16.72     | 2.53 | 20.8%        |
| 3    | mousesports   | 16.22     | 2.54 | 17.8%        |
| 4    | Natus Vincere | 15.36     | 2.54 | 9.0%         |
| 5    | Vitality      | 14.64     | 2.43 | 4.6%         |
| 6    | fnatic        | 14.63     | 2.66 | 6.9%         |
| 7    | FURIA         | 14.40     | 2.60 | 4.5%         |
| 8    | G2            | 14.27     | 2.57 | 3.4%         |
| 9    | 100 Thieves   | 14.24     | 2.60 | 4.1%         |
| 10   | FaZe          | 14.16     | 2.47 | 5.0%         |

(Full table produced inside the notebook.)

---

## What the model does

1. **Loads real HLTV match data** (results + round-by-round economy)
   and splits it chronologically into train / test.
2. **Builds leakage-safe, time-decayed, Laplace-smoothed features** for
   each match: team win rate, per-map win rate, per-side win rate,
   momentum, win streak, and map side bias.
3. **Fits a logistic-regression blend model** on those features using
   walk-forward feature construction so no future information leaks in.
4. **Tunes the time-decay half-life** via 2-fold chronological CV on the
   training set only (best = 21 days).
5. **Evaluates on the held-out test set** (accuracy, Brier, log loss,
   ROC AUC, calibration curve, per-map accuracy, ablation study).
6. **Fits a per-team economy-state Markov model** — `P(win | economy)`
   and `P(next economy | economy)` — from real round data.
7. **Computes live match win probability** via DP over
   `(score_a, score_b, economy_a, economy_b)`.
8. **Replays tournaments** with Monte Carlo (5,000 sims) and scores the
   champion distribution with a Brier score.
9. **Simulates full round-robin seasons** over the 28 common teams.

---

## Repository layout
