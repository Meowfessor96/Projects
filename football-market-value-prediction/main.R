###############################################################################
# FIFA CASE STUDY (v3): skills, market value, player types, outliers
# Dataset : male_players (legacy).csv from Kaggle (FIFA 15-23, 110 columns)
# Methods : PCA/FA (PCA Class.R, FA.R) -> Clustering (CA.R, clustering.R)
#           -> Simple + multiple regression (store24.R) -> Outliers (outliers.R)
#
# SETUP
#   1. Save the Kaggle file as  male_players_legacy.csv  in your working folder
#   2. One-time: install.packages(c("psych", "NbClust", "MASS", "olsrr", "cluster"))
#      (NbClust and olsrr are optional: the script skips them if missing)
#   3. BEST: restart R (Ctrl+Shift+F10) and run everything in one go:
#        source("main.R", echo = TRUE)
#      (running line by line after an error leaves OLD objects in memory, and later
#       sections silently use them. If you do run by sections, run them in order.)
#
# PLOTS: every figure is drawn in RStudio AND saved as its own PNG in ./fifa_plots/
#   A_xx = candidates for the 5-minute slides
#   B_xx = backup / appendix / console-only evidence
#   The PNG is always written first. The on-screen preview is optional: if the Plots pane
#   is too small the preview switches itself off (set show_preview <- TRUE to retry).
###############################################################################

# Clean start: drop objects from earlier runs and reset the graphics device
rm(list = ls())
graphics.off()

library(psych)
library(MASS)
library(cluster)
has_nbclust <- requireNamespace("NbClust", quietly = TRUE)
has_olsrr   <- requireNamespace("olsrr",   quietly = TRUE)
if (has_nbclust) library(NbClust)
if (has_olsrr)   library(olsrr)

set.seed(123)

# ---------- helpers ----------------------------------------------------------
plot_dir <- "fifa_plots"
dir.create(plot_dir, showWarnings = FALSE)

# Save every figure as a PNG first (this always works), then try an on-screen preview.
# If the RStudio Plots pane is too small the preview fails. Repeated failed draws leave
# RStudio's device in a broken state ("invalid graphics state"), so after the FIRST failure
# previews are switched off and the device is reset.
show_preview <- TRUE
save_plot <- function(name, plot_fun, width = 1800, height = 1200, res = 200) {
  png(file.path(plot_dir, paste0(name, ".png")), width = width, height = height, res = res)
  tryCatch(plot_fun(),
           error = function(e) message("!! ", name, " could not be drawn: ", conditionMessage(e)),
           finally = dev.off())
  if (show_preview) {
    ok <- tryCatch({ plot_fun(); TRUE }, error = function(e) FALSE)
    if (!ok) {
      show_preview <<- FALSE
      try(graphics.off(), silent = TRUE)
      message("(Plots pane too small: previews are now OFF, PNGs are still saved in ", plot_dir,
              "/. Enlarge the pane and set show_preview <- TRUE to switch them back on.)")
    }
  }
  invisible(NULL)
}

# Run code on a throw-away graphics device. Used for functions that draw by themselves
# (NbClust plots its Hubert / D-index graphs and crashes on a small Plots pane).
with_null_device <- function(expr) {
  pdf(NULL)
  on.exit(dev.off())
  force(expr)
}

nice <- function(x) gsub("_", " ", x)

# Heat-map with numbers in the cells (rows = variables, columns = groups)
heat_plot <- function(M, main, zlim = NULL, digits = 2, mar = c(4, 14, 3, 1), cex_txt = 0.8) {
  op <- par(mar = mar); on.exit(par(op))
  if (is.null(zlim)) zlim <- c(-1, 1) * max(abs(M))
  pal <- colorRampPalette(c("firebrick", "white", "steelblue"))(51)
  nr <- nrow(M); nc <- ncol(M)
  image(1:nc, 1:nr, t(M[nr:1, , drop = FALSE]), col = pal, zlim = zlim,
        axes = FALSE, xlab = "", ylab = "", main = main)
  axis(1, at = 1:nc, labels = colnames(M), tick = FALSE, cex.axis = 1)
  axis(2, at = 1:nr, labels = rev(nice(rownames(M))), las = 1, tick = FALSE, cex.axis = 0.8)
  g <- expand.grid(x = 1:nc, y = 1:nr)
  # expand.grid varies x fastest: build values in the same order
  vals <- M[nr:1, , drop = FALSE]
  txt <- formatC(vals[cbind(g$y, g$x)], format = "f", digits = digits)
  text(g$x, g$y, txt, cex = cex_txt)
  box()
}

###############################################################################
# SECTION 0: LOAD AND PREPARE DATA  (not a slide; one line in "Data")
###############################################################################

csv_path <- "male_players_legacy.csv"                     # or "male_players (legacy).csv"
if (!file.exists(csv_path)) csv_path <- file.choose()     # file dialog if not found
fifa_raw <- read.csv(csv_path, stringsAsFactors = FALSE, encoding = "UTF-8")  # ~30 sec
dim(fifa_raw)
table(fifa_raw$fifa_version)

fifa <- fifa_raw[fifa_raw$fifa_version == 23, ]     # one edition only
rm(fifa_raw)

# The 29 detailed skill ratings (the 6 summary columns pace/shooting/... are
# averages of these, so we leave them out; goalkeeping columns too)
skill_vars <- c(
  "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy",
  "attacking_short_passing", "attacking_volleys",
  "skill_dribbling", "skill_curve", "skill_fk_accuracy",
  "skill_long_passing", "skill_ball_control",
  "movement_acceleration", "movement_sprint_speed", "movement_agility",
  "movement_reactions", "movement_balance",
  "power_shot_power", "power_jumping", "power_stamina", "power_strength",
  "power_long_shots",
  "mentality_aggression", "mentality_interceptions", "mentality_positioning",
  "mentality_vision", "mentality_penalties", "mentality_composure",
  "defending_marking_awareness", "defending_standing_tackle",
  "defending_sliding_tackle"
)

fifa$pos_first <- trimws(sub(",.*", "", fifa$player_positions))
fifa <- fifa[fifa$pos_first != "GK", ]                         # outfield only
fifa <- fifa[!is.na(fifa$value_eur) & fifa$value_eur > 0, ]

# Four roles: DEF (CB, full-backs), DM (CDM), MID (CM, CAM, wide mids), FWD (strikers, wingers).
# DM gets its own role because holding midfielders are valued for defending skills,
# unlike the other midfielders (checked: this raises hold-out R-squared from 0.92 to 0.94).
fifa$pos_group <- ifelse(fifa$pos_first %in% c("CB", "LB", "RB", "LWB", "RWB"), "DEF",
                         ifelse(fifa$pos_first == "CDM", "DM",
                                ifelse(fifa$pos_first %in% c("ST", "CF", "LW", "RW"), "FWD", "MID")))
fifa$pos_group <- factor(fifa$pos_group, levels = c("DEF", "DM", "MID", "FWD"))

fifa$log_value <- log(fifa$value_eur)
fifa$age_sq    <- fifa$age^2

nrow(fifa)
table(fifa$pos_group)

# Analysis sample (3000 players) + HOLD-OUT set (all the other outfield players).
# The hold-out set is never used for fitting: it tests how well the models predict
# players they have not seen.
n_sample  <- 3000
samp_idx  <- sample(nrow(fifa), n_sample)
fifa_s    <- fifa[samp_idx, ]
fifa_test <- fifa[-samp_idx, ]
rownames(fifa_s) <- make.unique(fifa_s$short_name)   # player names label the plots
nrow(fifa_test)

###############################################################################
# SECTION 1: DATA DESCRIPTION
###############################################################################

summary(fifa_s[, c("age", "overall", "potential", "value_eur", "wage_eur")])

save_plot("B_01_value_hist_raw", function() {
  hist(fifa_s$value_eur / 1e6, breaks = 50, col = "grey80", border = "white",
       main = "Market value is extremely right-skewed",
       xlab = "Value (million EUR)")
})
save_plot("B_02_value_hist_log", function() {
  hist(fifa_s$log_value, breaks = 50, col = "steelblue", border = "white",
       main = "log(Market value) is roughly symmetric",
       xlab = "log(EUR)")
})

save_plot("B_03_skill_correlation_heatmap", function() {
  heatmap(cor(fifa_s[, skill_vars]), symm = TRUE, margins = c(12, 12),
          labRow = nice(skill_vars), labCol = nice(skill_vars),
          cexRow = 0.7, cexCol = 0.7, main = "Correlation of the 29 skills")
}, width = 2000, height = 2000)

###############################################################################
# SECTION 2: PCA AND FA   (PCA Class.R, FA.R)
###############################################################################

skills <- fifa_s[, skill_vars]

# How many factors? Parallel analysis, exactly as in class
save_plot("B_04_parallel_analysis_scree", function() {
  set.seed(1)
  fa.parallel(skills, fa = "both", n.iter = 50,
              main = "Scree plots with parallel analysis")
})
# <<< Console message: 5 factors (FA) but 4 components (PCA). Our scores come from
#     PCA (principal), so we use k = 4. >>>
k_factors <- 4

pc <- principal(skills, nfactors = k_factors, rotate = "none")
pc
rc <- principal(skills, nfactors = k_factors, rotate = "varimax", scores = TRUE)
rc
print(rc$loadings, cutoff = 0.4, sort = TRUE)

fa_fit <- fa(skills, nfactors = k_factors, rotate = "varimax", fm = "pa")
print(fa_fit$loadings, cutoff = 0.4, sort = TRUE)

# PCA vs FA in one number: diagonal ~1 means the same factors came out
round(factor.congruence(rc, fa_fit), 2)

# ---- Name the factors (order must match RC1..RC4) ----
# In our run: RC1 technical, RC2 defending, RC3 pace, RC4 physical/aerial.
# The printout below lets you CHECK that against your own loadings.
factor_names <- c("Technical", "Defending", "Pace", "Physical")
stopifnot(length(factor_names) == k_factors)
L <- unclass(rc$loadings)
colnames(L) <- factor_names
for (j in 1:k_factors) {
  cat(sprintf("%-10s <- %s\n", factor_names[j],
              paste(nice(head(rownames(L)[order(-abs(L[, j]))], 4)), collapse = ", ")))
}

fs <- as.data.frame(rc$scores)
colnames(fs) <- factor_names
rownames(fs) <- rownames(fifa_s)
head(fs)

# A_01: loadings heat-map, rows grouped by the factor they belong to
dom <- apply(abs(L), 1, which.max)
ord <- order(dom, -apply(abs(L), 1, max))
save_plot("A_01_factor_loadings_heatmap", function() {
  heat_plot(L[ord, ], "Varimax-rotated loadings (4 skill dimensions)",
            zlim = c(-1, 1), digits = 2, cex_txt = 0.7)
}, width = 1500, height = 1800)

# B_05: which dimension do the skills with the highest value-correlation belong to?
cor_with_value <- cor(fifa_s[, skill_vars], fifa_s$log_value)[, 1]
cor_sorted <- sort(cor_with_value, decreasing = TRUE)
round(cor_sorted, 2)
factor_cols <- c("steelblue", "firebrick", "darkorange", "forestgreen", "purple", "grey40")[1:k_factors]
save_plot("B_05_skill_correlation_with_value", function() {
  op <- par(mar = c(4, 13, 3, 1)); on.exit(par(op))
  barplot(rev(cor_sorted), horiz = TRUE, las = 1, cex.names = 0.6,
          names.arg = rev(nice(names(cor_sorted))),
          col = factor_cols[dom[rev(names(cor_sorted))]],
          xlab = "Correlation with log(value)",
          main = "Skill correlation with market value (colour = skill dimension)")
  legend("bottomright", legend = factor_names, fill = factor_cols, bty = "n", cex = 0.8)
}, width = 1800, height = 1500)

###############################################################################
# SECTION 3: CLUSTER ANALYSIS   (CA.R, clustering.R)
###############################################################################

fs_scaled <- scale(fs)

# ---- How many clusters? Three views: elbow, silhouette, NbClust ----
wss <- sapply(1:10, function(k) {
  if (k == 1) return((nrow(fs_scaled) - 1) * sum(apply(fs_scaled, 2, var)))
  set.seed(1234)
  # iter.max defaults to 10, which gives "did not converge in 10 iterations"
  sum(kmeans(fs_scaled, k, nstart = 10, iter.max = 200)$withinss)
})
save_plot("B_06_elbow_plot", function() {
  plot(1:10, wss, type = "b", pch = 16, xlab = "Number of clusters",
       ylab = "Within groups sum of squares", main = "Elbow plot")
})

d_all <- dist(fs_scaled)
sil_width <- sapply(2:8, function(k) {
  set.seed(1234)
  km <- kmeans(fs_scaled, k, nstart = 25, iter.max = 200)
  mean(silhouette(km$cluster, d_all)[, 3])
})
names(sil_width) <- 2:8
round(sil_width, 3)     # ~0.2-0.25 everywhere: players form a continuum, not tight islands
save_plot("B_07_silhouette_by_k", function() {
  plot(2:8, sil_width, type = "b", pch = 16, xlab = "Number of clusters",
       ylab = "Average silhouette width", main = "Silhouette width by k")
})

if (has_nbclust) {
  set.seed(1234)
  idx_nb <- sample(nrow(fs_scaled), 300)   # lower to 200 if this is slow
  # NbClust draws its own plots while it runs; on a small Plots pane that raised
  # "figure margins too large" INSIDE NbClust. A throw-away device avoids it.
  nc <- tryCatch(
    with_null_device(NbClust(fs_scaled[idx_nb, ], min.nc = 2, max.nc = 8, method = "kmeans")),
    error = function(e) { message("NbClust skipped: ", conditionMessage(e)); NULL })
  if (!is.null(nc)) {
    nb_votes <- table(nc$Best.n[1, ])
    print(nb_votes)
    save_plot("B_08_nbclust_votes", function() {
      barplot(nb_votes, xlab = "Number of clusters",
              ylab = "Number of criteria", main = "Number of clusters chosen by the criteria")
    })
  }
}

# <<< Decision: silhouette is flat (k = 3-5 similar), NbClust majority said 3.
#     We use k = 4: it is the smallest k that splits defenders into two types
#     (classic centre-backs vs athletic full-backs). k = 3 gives plain DEF/MID/FWD. >>>
k_clusters <- 4

set.seed(1234)
fit.km <- kmeans(fs_scaled, k_clusters, nstart = 25, iter.max = 100)
fit.km$size
round(fit.km$centers, 2)      # read this to confirm the names below

# Cluster names are derived from the centres, so they stay correct even if k-means numbers
# the clusters differently on another machine / R version (k = 4 only; else "Cluster j").
#   Attackers             = lowest Defending
#   Centre-backs          = lowest Technical
#   Technical midfielders = lowest Physical (small, technical, not physical)
#   remaining cluster     = athletic full-backs / box-to-box (above average on defending + pace)
name_clusters <- function(ctr) {
  nm <- paste("Cluster", seq_len(nrow(ctr)))
  if (nrow(ctr) == 4) {
    pick <- c(which.min(ctr[, "Defending"]), which.min(ctr[, "Technical"]), which.min(ctr[, "Physical"]))
    if (!anyDuplicated(pick)) {
      nm[pick] <- c("Attackers", "Centre-backs", "Technical midfielders")
      nm[setdiff(1:4, pick)] <- "Athletic full-backs / box-to-box"
    }
  }
  nm
}
cluster_names <- name_clusters(fit.km$centers)
cluster_names
cl_cols <- c("#E69F00", "#56B4E9", "#009E73", "#CC79A7", "#D55E00", "#0072B2", "#F0E442", "#999999")[1:k_clusters]

# Football-terms summary per cluster (screenshot-friendly table)
cluster_summary <- data.frame(
  cluster = cluster_names,
  n = as.vector(table(fit.km$cluster)),
  median_overall = tapply(fifa_s$overall, fit.km$cluster, median),
  median_age = tapply(fifa_s$age, fit.km$cluster, median),
  median_value_EURm = round(tapply(fifa_s$value_eur, fit.km$cluster, median) / 1e6, 2),
  top_positions = sapply(seq_len(k_clusters), function(j)       # sanity check of the names
    paste(names(sort(table(fifa_s$pos_first[fit.km$cluster == j]), decreasing = TRUE))[1:3],
          collapse = ", "))
)
cluster_summary

# A_02: clusters projected on the 2 axes that best separate th  em (LDA projection).
# Plain RC1-vs-RC2 scatter overlaps too much, this view does not.
# CAUTION: these axes are CHOSEN to separate the clusters, so the picture looks cleaner than
# the data really is (silhouette ~0.23: players form a continuum, not tight islands).
lda_fit <- lda(fs_scaled, grouping = fit.km$cluster)
ld <- predict(lda_fit)$x
ld_centers <- apply(ld[, 1:2], 2, function(v) tapply(v, fit.km$cluster, mean))
save_plot("A_02_cluster_scatter", function() {
  plot(ld[, 1], ld[, 2], col = adjustcolor(cl_cols[fit.km$cluster], 0.45),
       pch = 16, cex = 0.7, xlab = "Discriminant axis 1", ylab = "Discriminant axis 2",
       main = "Player types on the 2 axes that best separate them (LDA view)")
  points(ld_centers, pch = 21, bg = cl_cols, cex = 2.5, lwd = 2)
  legend("bottomleft", legend = cluster_names, col = cl_cols, pch = 16, bty = "n", cex = 0.85)
})

# A_03: cluster profiles (mean factor score per cluster) -> how we name them
profile_mat <- t(fit.km$centers)          # factors x clusters
rownames(profile_mat) <- factor_names
save_plot("A_03_cluster_profiles", function() {
  bp <- barplot(profile_mat, beside = TRUE, names.arg = cluster_names, col = factor_cols,
                cex.names = 0.7, ylab = "Mean standardized factor score",
                ylim = c(min(profile_mat) - 0.3, max(profile_mat) + 0.6),
                main = "What each player type is good at")
  abline(h = 0)
  # Value printed on every bar. A bar of height ~0 is NOT missing: it means "average on this
  # factor" (e.g. Attackers' Pace = 0.00, because the cluster mixes quick wingers and strikers).
  v <- as.vector(profile_mat)
  text(as.vector(bp), v + ifelse(v >= 0, 0.07, -0.07), labels = sprintf("%.2f", v), cex = 0.6)
  legend("topleft", legend = factor_names, fill = factor_cols, bty = "n", cex = 0.8, ncol = 2)
}, width = 2000, height = 1200)

# A_04: do clusters recover positions the algorithm never saw?
ct.km <- table(fifa_s$pos_group, fit.km$cluster)
ct.km
round(prop.table(ct.km, 1), 2)
# Share of players who belong to the majority position group of their cluster
# (baseline = share of the biggest position group, i.e. one single cluster)
cluster_purity <- sum(apply(ct.km, 2, max)) / sum(ct.km)
round(c(cluster_purity = cluster_purity, baseline = max(rowSums(ct.km)) / sum(ct.km)), 2)
# Which first-listed positions fill each cluster (column %)? Use it to check the names.
round(prop.table(table(fifa_s$pos_first, fit.km$cluster), 2), 2)
save_plot("A_04_position_vs_cluster", function() {
  op <- par(mar = c(4, 4, 3, 1)); on.exit(par(op))
  barplot(t(prop.table(ct.km, 1)), col = cl_cols, xlim = c(0, 6.2),
          ylab = "Share of position group",
          main = "How each position group splits across the clusters",
          legend.text = cluster_names,
          args.legend = list(x = "right", bty = "n", cex = 0.8, inset = 0.0))
})

# Hierarchical clustering on a small subsample (class exercise). Ward linkage:
# average linkage (class default) chains almost everyone into one big cluster here.
set.seed(1234)
idx_h <- sample(nrow(fs_scaled), 60)
d_h <- dist(fs_scaled[idx_h, ])
table(average_linkage_sizes = cutree(hclust(d_h, method = "average"), k = k_clusters))
fit.ward <- hclust(d_h, method = "ward.D2")
save_plot("B_09_dendrogram_ward", function() {
  plot(fit.ward, hang = -1, cex = 0.6, main = "Ward linkage (60 players)", xlab = "", sub = "")
  rect.hclust(fit.ward, k = k_clusters, border = cl_cols)
}, width = 2200, height = 1100)
table(hierarchical = cutree(fit.ward, k = k_clusters), kmeans = fit.km$cluster[idx_h])

###############################################################################
# SECTION 4: REGRESSION   (store24.R)  - which skills drive market value?
###############################################################################

# Skills as z-scores (centre/scale taken from the SAMPLE, reused for the hold-out set)
sk_center <- colMeans(fifa_s[, skill_vars])
sk_scale  <- apply(fifa_s[, skill_vars], 2, sd)
make_df <- function(d, z) data.frame(
  log_value = d$log_value, overall = d$overall, potential = d$potential,
  age = d$age, age_sq = d$age_sq, pos_group = d$pos_group, z)
reg_df  <- make_df(fifa_s,
                   as.data.frame(scale(fifa_s[, skill_vars], center = sk_center, scale = sk_scale)))
test_df <- make_df(fifa_test,
                   as.data.frame(scale(fifa_test[, skill_vars], center = sk_center, scale = sk_scale)))
rownames(reg_df) <- rownames(fifa_s)

# ---- M1: simple regression ----
m1 <- lm(log_value ~ overall, data = reg_df)
summary(m1)
save_plot("A_05_simple_regression", function() {
  plot(reg_df$overall, reg_df$log_value, pch = 16, cex = 0.5,
       col = adjustcolor("grey30", 0.4), xlab = "Overall rating", ylab = "log(Market value)",
       main = "Simple regression: value vs overall rating")
  abline(m1, col = "red", lwd = 3)
  legend("topleft", bty = "n",
         legend = sprintf("slope = %.3f  (+1 rating = +%.0f%% value)\nR-squared = %.2f",
                          coef(m1)[2], (exp(coef(m1)[2]) - 1) * 100, summary(m1)$r.squared))
})

# ---- M2: pooled multiple regression: age + position + 29 skills ----
m2 <- lm(log_value ~ ., data = reg_df[, c("log_value", "age", "age_sq", "pos_group", skill_vars)])
summary(m2)

# Two lenses on skill importance: marginal (correlation) vs conditional (coefficient)
cond_coef <- coef(m2)[skill_vars]
importance <- data.frame(
  skill = nice(skill_vars),
  correlation = round(cor_with_value, 2),
  coefficient = round(cond_coef, 3),
  pct_value_change_per_SD = round((exp(cond_coef) - 1) * 100, 1),
  row.names = NULL
)
importance[order(-abs(importance$coefficient)), ][1:10, ]

vif_vals <- sort(diag(solve(cor(fifa_s[, skill_vars]))), decreasing = TRUE)
round(head(vif_vals, 6), 1)   # tackling skills overlap heavily (VIF > 10)
round(vif_vals["mentality_positioning"], 1)   # positioning is NOT among the worst VIFs

save_plot("B_10_correlation_vs_coefficient", function() {
  plot(cor_with_value, cond_coef, pch = 16, col = "steelblue",
       xlab = "Correlation with log(value)  (marginal)",
       ylab = "Regression coefficient  (holding other skills fixed)",
       main = "Marginal vs conditional skill importance")
  abline(h = 0, v = 0, lty = 2, col = "grey60")
  lab <- unique(c(names(sort(abs(cond_coef), decreasing = TRUE))[1:8],
                  names(sort(cor_with_value, decreasing = TRUE))[1:3]))
  text(cor_with_value[lab], cond_coef[lab], nice(lab), pos = 4, cex = 0.6)
})

# Only skills significant at 5%, ranked by size of effect.
# CAUTION: these are PARTIAL effects (all other skills held fixed) with ONE slope for all roles.
# A negative sign does NOT mean the skill lowers value. Example (our run): positioning has
# correlation +0.43 with log(value), pooled coefficient -0.14, but +0.23 (MID) and +0.33 (FWD)
# in the per-role models (A_06). Use A_06 for the story, B_10 to show the sign flip.
pooled_p <- summary(m2)$coefficients[skill_vars, "Pr(>|t|)"]
sig_coef <- cond_coef[pooled_p < 0.05]
top10 <- sort(head(sig_coef[order(-abs(sig_coef))], 10), decreasing = TRUE)
save_plot("B_11_top10_skills_pooled", function() {
  op <- par(mar = c(4, 13, 3, 1)); on.exit(par(op))
  barplot(rev(top10), horiz = TRUE, las = 1, cex.names = 0.7, names.arg = rev(nice(names(top10))),
          col = ifelse(rev(top10) > 0, "steelblue", "firebrick"),
          xlab = "Effect on log(value) per +1 SD of skill (others held fixed)",
          main = "Pooled model, significant skills (red = partial effect, not a penalty)")
})

# ---- M3: 4 factors instead of 29 skills (links back to Section 2) ----
f3 <- as.formula(paste("log_value ~ age + age_sq + pos_group +", paste(factor_names, collapse = " + ")))
m3 <- lm(f3, data = cbind(reg_df[, c("log_value", "age", "age_sq", "pos_group")], fs))
summary(m3)

# ---- M4: backward stepwise (store24.R) ----
m4 <- stepAIC(m2, direction = "backward", trace = 0)
length(coef(m4)) - 1          # predictors kept (of 34: age, age_sq, 3 position dummies, 29 skills)

# ---- M5: pooled + potential ----
m5 <- update(m4, . ~ . + potential, data = reg_df)

# ---- M6 / M7: one model PER ROLE (DEF, DM, MID, FWD): age + skills (+ potential) ----
# Why: the pooled model forces tackling to be worth the same for a striker as for a
# centre-back. The outlier analysis (Section 5) shows this is the main misfit.
roles <- levels(reg_df$pos_group)
m6 <- lapply(roles, function(g) lm(log_value ~ .,
                                   data = reg_df[reg_df$pos_group == g, c("log_value", "age", "age_sq", skill_vars)]))
m7 <- lapply(roles, function(g) lm(log_value ~ .,
                                   data = reg_df[reg_df$pos_group == g, c("log_value", "age", "age_sq", "potential", skill_vars)]))
names(m6) <- names(m7) <- roles

# A_06: THE headline figure - which skills matter for which role
role_coefs <- sapply(m6, function(m) coef(m)[skill_vars])           # 29 x 3
top_union <- unique(unlist(lapply(roles, function(g)
  names(sort(abs(role_coefs[, g]), decreasing = TRUE))[1:5])))
top_union <- top_union[order(-apply(abs(role_coefs[top_union, ]), 1, max))]
round(role_coefs[top_union, ], 2)
save_plot("A_06_skills_by_role_heatmap", function() {
  heat_plot(role_coefs[top_union, ], "Effect of each skill on log(value), by position group",
            digits = 2, cex_txt = 0.9)
}, width = 1700, height = 1300)

# ---- Fit and hold-out accuracy for every model ----
predict_by_role <- function(models, df) {
  p <- rep(NA_real_, nrow(df))
  for (g in names(models)) { i <- df$pos_group == g; p[i] <- predict(models[[g]], newdata = df[i, ]) }
  p
}
test_fs <- as.data.frame(predict(rc, fifa_test[, skill_vars], old.data = skills))
colnames(test_fs) <- factor_names
test_df3 <- cbind(test_df, test_fs)

r2   <- function(y, p) 1 - sum((y - p)^2) / sum((y - mean(y))^2)
perf <- function(p_train, p_test) c(
  train_R2 = r2(reg_df$log_value, p_train),
  test_R2  = r2(test_df$log_value, p_test),
  test_RMSE = sqrt(mean((test_df$log_value - p_test)^2)))

res_tab <- rbind(
  perf(fitted(m1), predict(m1, test_df)),
  perf(fitted(m2), predict(m2, test_df)),
  perf(fitted(m3), predict(m3, test_df3)),
  perf(fitted(m4), predict(m4, test_df)),
  perf(fitted(m5), predict(m5, test_df)),
  perf(predict_by_role(m6, reg_df), predict_by_role(m6, test_df)),
  perf(predict_by_role(m7, reg_df), predict_by_role(m7, test_df)))
model_compare <- data.frame(
  model = c("M1 overall only", "M2 pooled: age + position + 29 skills", "M3 pooled: 4 factors",
            "M4 : M2 stepwise", "M5 : M4 + potential", "M6 per-role: age + skills",
            "M7 : per-role + potential"),
  round(res_tab, 3),
  # RMSE is in log units: a typical prediction is off by this % (multiplicative error)
  typical_error_pct = round((exp(res_tab[, "test_RMSE"]) - 1) * 100, 0))
model_compare

save_plot("A_07_model_comparison", function() {
  op <- par(mar = c(4, 17, 3, 2)); on.exit(par(op))
  b <- barplot(rev(model_compare$test_R2), horiz = TRUE, names.arg = rev(model_compare$model),
               las = 1, cex.names = 0.7, xlim = c(0, 1.05), col = "steelblue",
               xlab = "R-squared on 13k unseen players (hold-out)",
               main = "How well each model predicts market value")
  text(rev(model_compare$test_R2), b, labels = sprintf("%.2f", rev(model_compare$test_R2)),
       pos = 4, cex = 0.8)
}, width = 1900, height = 1100)

# A_08: predicted vs actual on unseen players (best skills-only model, M6)
pred6_test <- predict_by_role(m6, test_df)
set.seed(7); show_i <- sample(nrow(test_df), 3000)
tick_val <- c(1e5, 1e6, 1e7, 1e8)
save_plot("A_08_actual_vs_predicted", function() {
  plot(pred6_test[show_i], test_df$log_value[show_i], pch = 16, cex = 0.5,
       col = adjustcolor("grey30", 0.35), axes = FALSE,
       xlab = "Predicted value (EUR)", ylab = "Actual value (EUR)",
       main = "Per-role skills model on unseen players")
  axis(1, at = log(tick_val), labels = c("0.1M", "1M", "10M", "100M"))
  axis(2, at = log(tick_val), labels = c("0.1M", "1M", "10M", "100M"), las = 1)
  box(); abline(0, 1, col = "red", lwd = 3)
  legend("topleft", bty = "n", legend = sprintf("hold-out R-squared = %.2f", model_compare$test_R2[6]))
})

###############################################################################
# SECTION 5: OUTLIERS   (outliers.R, outliers2.R)
# Residual = actual log(value) - predicted log(value)
#   positive -> valued ABOVE what skills + age justify
#   negative -> valued BELOW what skills + age justify
###############################################################################

# ---- 5a. Class-style diagnostics on the POOLED model (M4) ----
final_model <- m4
yhat   <- fitted(final_model)
t_stud <- rstudent(final_model)
d_std  <- rstandard(final_model)
h      <- hatvalues(final_model)
cooksd <- cooks.distance(final_model)

sum(abs(t_stud) > 3)                    # flagged by the |t| > 3 rule
t_stud[abs(t_stud) > 3]

save_plot("B_12_residuals_vs_fitted", function() {
  plot(yhat, d_std, pch = 16, cex = 0.5, col = adjustcolor("grey30", 0.4),
       xlab = "Fitted values", ylab = "Standardized residuals",
       main = "Pooled model: standardized residuals vs fitted")
  abline(h = c(-3, 0, 3), col = c("red", "grey50", "red"), lty = c(2, 1, 2))
  flag <- abs(d_std) > 3
  text(yhat[flag], d_std[flag], names(d_std)[flag], col = "red", cex = 0.6, pos = 3)
})
save_plot("B_13_normal_qq", function() {
  qqnorm(resid(final_model), main = "Normal Q-Q: residuals of pooled model", pch = 16, cex = 0.5)
  qqline(resid(final_model), col = 2, lwd = 2)
})
shapiro.test(resid(final_model))        # n = 3000 is allowed; expect a rejection at this n
save_plot("B_14_cooks_distance", function() {
  plot(cooksd, pch = 16, cex = 0.5, col = adjustcolor("grey30", 0.5),
       ylab = "Cook's distance", main = "Influential players (pooled model)")
  abline(h = 4 * mean(cooksd), col = "red", lty = 2)
  top_cook <- order(cooksd, decreasing = TRUE)[1:10]
  text(top_cook, cooksd[top_cook], names(cooksd)[top_cook], col = "red", cex = 0.6, pos = 4)
})
save_plot("B_15_residual_vs_leverage", function() {
  plot(h, d_std, pch = 16, cex = 0.5, col = adjustcolor("grey30", 0.4),
       xlab = "Leverage", ylab = "Standardized residuals",
       main = "Residuals vs leverage (pooled model)")
  abline(h = c(-3, 3), col = "red", lty = 2)
  abline(v = 2 * mean(h), col = "blue", lty = 2)       # 2p/n leverage rule of thumb
})
if (has_olsrr) {
  # olsrr draws with ggplot2/grid. Sending it to PNG files (not the RStudio pane) avoids
  # "invalid graphics state", which RStudio throws after earlier failed draws.
  save_ols <- function(name, f) {
    png(file.path(plot_dir, paste0(name, ".png")), width = 1800, height = 1200, res = 200)
    tryCatch({ p <- f(); if (inherits(p, "ggplot")) print(p) },
             error = function(e) message("!! ", name, " skipped: ", conditionMessage(e)),
             finally = dev.off())
  }
  save_ols("B_16_olsrr_resid_vs_leverage", function() ols_plot_resid_lev(final_model))
  save_ols("B_17_olsrr_cooksd_chart",      function() ols_plot_cooksd_chart(final_model))
}

# ---- 5b. FINAL outlier analysis: per-role models (M6) ----
role_diag <- do.call(rbind, lapply(roles, function(g) {
  m <- m6[[g]]
  data.frame(player = names(resid(m)), fitted = fitted(m), residual = resid(m),
             student_resid = rstudent(m), cooks_d = cooks.distance(m),
             leverage = hatvalues(m), dffits = dffits(m), row.names = NULL)
}))
ix <- match(role_diag$player, rownames(fifa_s))
role_diag$pos         <- fifa_s$pos_first[ix]
role_diag$age         <- fifa_s$age[ix]
role_diag$overall     <- fifa_s$overall[ix]
role_diag$potential   <- fifa_s$potential[ix]
role_diag$actual_EURm <- fifa_s$value_eur[ix] / 1e6
role_diag$expected_EURm <- exp(role_diag$fitted) / 1e6
role_diag$gap_EURm      <- role_diag$actual_EURm - role_diag$expected_EURm

n_flag <- sum(abs(role_diag$student_resid) > 3)
# flagged vs. what pure chance gives for 3000 players (P(|z| > 3) = 0.27%, about 8 players):
c(flagged = n_flag, expected_by_chance = round(2 * pnorm(-3) * nrow(role_diag), 1))
table(role_diag$pos[abs(role_diag$student_resid) > 3])   # which positions?

show_cols <- c("player", "pos", "age", "overall", "potential", "actual_EURm",
               "expected_EURm", "gap_EURm", "residual", "student_resid")
tidy <- function(d) { d[, c("actual_EURm", "expected_EURm", "gap_EURm", "residual", "student_resid")] <-
  round(d[, c("actual_EURm", "expected_EURm", "gap_EURm", "residual", "student_resid")], 2)
d }
premium  <- tidy(role_diag[order(role_diag$residual, decreasing = TRUE), ][1:10, show_cols])
discount <- tidy(role_diag[order(role_diag$residual), ][1:10, show_cols])
premium      # valued ABOVE what their skills justify
discount     # valued BELOW what their skills justify

# What do the leftovers have in common? (check, do not assume)
# NOTE: least-squares residuals are EXACTLY uncorrelated with every variable inside the model
# (age, age_sq, the 29 skills), so cor(residual, age) is always ~0 and says nothing.
# Only variables the model did NOT use can explain what is left over:
round(c(potential   = cor(role_diag$residual, role_diag$potential),
        overall     = cor(role_diag$residual, role_diag$overall),
        growth_room = cor(role_diag$residual, role_diag$potential - role_diag$overall)), 2)
# Mean residual by age band: a real check that the age curve (age + age^2) is flexible enough
round(tapply(role_diag$residual, cut(role_diag$age, c(15, 20, 24, 28, 32, 40)), mean), 2)

# Why per-role matters: the pooled model's top-10 "premium" list is mostly centre-backs
pooled_top <- names(sort(resid(m4), decreasing = TRUE))[1:10]
table(pooled = fifa_s[pooled_top, "pos_first"])
table(per_role = premium$pos)

# A_09: expected vs actual value for the 6 biggest premiums and 6 biggest discounts.
# Slide version: only players rated 65+ (otherwise 46-rated squad players with 0.1M values
# dominate the list and the figure is not meaningful for an audience).
pool <- role_diag[role_diag$overall >= 65, ]
pick <- rbind(head(pool[order(pool$residual, decreasing = TRUE), ], 6),
              head(pool[order(pool$residual), ], 6))
pick <- pick[order(pick$actual_EURm / pick$expected_EURm), ]
pick_lab <- sprintf("%s (%s, %d, ovr %d)", pick$player, pick$pos, pick$age, pick$overall)
save_plot("A_09_over_under_valued", function() {
  op <- par(mar = c(4, 16, 3, 1)); on.exit(par(op))
  yy <- seq_len(nrow(pick))
  plot(range(c(pick$actual_EURm, pick$expected_EURm)) * c(0.7, 1.4), range(yy), type = "n",
       log = "x", xaxt = "n", yaxt = "n", xlab = "Market value, million EUR (log scale)", ylab = "",
       main = "Over- and under-valued players (rated 65+) vs skill-based expectation")
  axis(1, at = c(0.05, 0.1, 0.5, 1, 5, 10, 50), labels = c("0.05", "0.1", "0.5", "1", "5", "10", "50"))
  axis(2, at = yy, labels = pick_lab, las = 1, cex.axis = 0.7)
  segments(pick$expected_EURm, yy, pick$actual_EURm, yy, col = "grey50", lwd = 2)
  points(pick$expected_EURm, yy, pch = 21, bg = "white", cex = 1.6)
  points(pick$actual_EURm, yy, pch = 16, cex = 1.6,
         col = ifelse(pick$actual_EURm > pick$expected_EURm, "firebrick", "steelblue"))
  legend("bottomright", bty = "n", cex = 0.8,
         legend = c("expected from skills + age", "actual: above expectation", "actual: below expectation"),
         pch = c(21, 16, 16), pt.bg = "white", col = c("black", "firebrick", "steelblue"))
}, width = 2000, height = 1200)

###############################################################################
# DONE: list the saved figures
###############################################################################
cat("\n===== KEY NUMBERS FOR THE SLIDES =====\n")
cat("Outfield players with a value:", nrow(fifa), "| analysis sample:", n_sample,
    "| hold-out:", nrow(fifa_test), "\n")
cat("Variance explained by the", k_factors, "components:",
    round(100 * sum(L^2) / length(skill_vars), 1), "%\n")
cat("Clusters: k =", k_clusters, "| silhouette at k:", round(sil_width[as.character(k_clusters)], 3),
    "| position purity:", round(cluster_purity, 2), "\n")
cat("Hold-out R2: overall only", model_compare$test_R2[1], "| pooled skills", model_compare$test_R2[2],
    "| per-role skills", model_compare$test_R2[6], "| per-role + potential", model_compare$test_R2[7], "\n")
cat("Outliers |t| > 3 (per-role):", n_flag, "| expected by chance:",
    round(2 * pnorm(-3) * nrow(role_diag), 1), "\n")
cat("\nPNGs saved in:", normalizePath(plot_dir), "\n")
list.files(plot_dir)
