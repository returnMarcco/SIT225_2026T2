import pandas as pd
import plotly.express as px
import pandas as pd


# -------------------------
# 1. Load wrangled CSV
# -------------------------

df = pd.read_csv(
    "movement_events_simulated.csv",
    parse_dates=[
        "timestamp",
        "simulated_timestamp",
        "simulated_date"
    ]
)


# ==========================================================
# DESCRIPTIVE STATISTICS
# UNAGGREGATED SIMULATED DATA
# ==========================================================

print("SIMULATED MOVEMENT RECORD STATISTICS")
print("------------------------------------")

mean_movement = df["movement"].mean()
median_movement = df["movement"].median()
std_movement = df["movement"].std()
variance_movement = df["movement"].var()

min_movement = df["movement"].min()
max_movement = df["movement"].max()
movement_range = max_movement - min_movement

print("Mean:", mean_movement)
print("Median:", median_movement)
print("Standard deviation:", std_movement)
print("Variance:", variance_movement)
print("Minimum:", min_movement)
print("Maximum:", max_movement)
print("Range:", movement_range)

percentiles = (
    df["movement"]
    .quantile([
        0.25,
        0.50,
        0.75,
        0.90,
        0.95
    ])
)

print("\nMOVEMENT PERCENTILES")
print("--------------------")
print(percentiles)
df["warm_binary"] = (
    df["season_group"]
    .map({
        "Cooler": 0,
        "Warmer": 1
    })
)

# Correlation on unaggregated simulated data
correlation = (
    df["warm_binary"]
    .corr(df["movement"])
)

print("UNAGGREGATED MOVEMENT CORRELATION")
print("---------------------------------")
print("Point-biserial correlation:", correlation)

# VISUALISATIONS

# ==========================================================
# 1. TIME SERIES LINE PLOT
# Pre-aggregated simulated data
# ==========================================================

plot_df = df.sort_values("simulated_date")

fig = px.line(
    plot_df,
    x="simulated_date",
    y="movement",
    title="Movement Detection Across the Simulated Year",
    labels={
        "simulated_date": "Simulated Date",
        "movement": "Movement Detection"
    }
)

fig.update_yaxes(
    tickvals=[0, 1],
    ticktext=["No Movement", "Movement"]
)

fig.show()


# ==========================================================
# 2. DISTRIBUTION HISTOGRAM
# Pre-aggregated simulated data
# ==========================================================

fig = px.histogram(
    df,
    x="movement",
    title="Distribution of Simulated Movement Records",
    labels={
        "movement": "Movement Detection",
        "count": "Number of Records"
    }
)

fig.update_xaxes(
    tickvals=[0, 1],
    ticktext=["No Movement", "Movement"]
)

fig.show()


# ==========================================================
# 3. RELATIONSHIP BOX PLOT
# Pre-aggregated simulated data
# ==========================================================

fig = px.box(
    df,
    x="season_group",
    y="movement",
    points="all",
    title="Relationship Between Season Group and Movement Detection",
    labels={
        "season_group": "Season Group",
        "movement": "Movement Detection"
    }
)

fig.update_yaxes(
    tickvals=[0, 1],
    ticktext=["No Movement", "Movement"]
)

fig.show()

import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf


# ==========================================================
# H2 STATISTICAL ANALYSIS
# ==========================================================

# Aggregate movement events into nightly counts
nightly_df = (
    df.groupby(
        [
            "simulated_date",
            "simulated_season",
            "season_group"
        ]
    )["movement"]
    .sum()
    .reset_index(name="event_count")
)


# ----------------------------------------------------------
# Encode seasonal group
#
# Cooler = 0
# Warmer = 1
# ----------------------------------------------------------

nightly_df["warm_binary"] = (
    nightly_df["season_group"]
    .map({
        "Cooler": 0,
        "Warmer": 1
    })
)


# ----------------------------------------------------------
# Descriptive comparison
# ----------------------------------------------------------

h2_stats = (
    nightly_df
    .groupby("season_group")["event_count"]
    .agg([
        "count",
        "mean",
        "median",
        "std",
        "var",
        "min",
        "max"
    ])
)

print("\nH2: WARMER VS COOLER NIGHTLY ACTIVITY")
print("-------------------------------------")
print(h2_stats)


# ----------------------------------------------------------
# Poisson assumption / dispersion check
# ----------------------------------------------------------

overall_mean = nightly_df["event_count"].mean()
overall_variance = nightly_df["event_count"].var()

dispersion_ratio = (
    overall_variance / overall_mean
)

print("\nPOISSON DISPERSION CHECK")
print("------------------------")
print("Mean:", overall_mean)
print("Variance:", overall_variance)
print("Variance / Mean:", dispersion_ratio)


# ----------------------------------------------------------
# Poisson regression
# ----------------------------------------------------------

poisson_model = smf.glm(
    formula="event_count ~ warm_binary",
    data=nightly_df,
    family=sm.families.Poisson()
).fit()

print("\nPOISSON REGRESSION")
print("------------------")
print(poisson_model.summary())


# ----------------------------------------------------------
# Extract H2 result
# ----------------------------------------------------------

coefficient = poisson_model.params["warm_binary"]
p_value = poisson_model.pvalues["warm_binary"]

ci_lower, ci_upper = (
    poisson_model
    .conf_int()
    .loc["warm_binary"]
)

irr = np.exp(coefficient)

irr_ci_lower = np.exp(ci_lower)
irr_ci_upper = np.exp(ci_upper)

percentage_change = (
    (irr - 1) * 100
)

print("\nH2 TEST RESULTS")
print("---------------")

print("Coefficient:", coefficient)
print("P-value:", p_value)

print("Incidence Rate Ratio:", irr)

print(
    "95% IRR Confidence Interval:",
    irr_ci_lower,
    "to",
    irr_ci_upper
)

print(
    "Estimated percentage change in warmer periods:",
    percentage_change,
    "%"
)


# ----------------------------------------------------------
# Hypothesis decision
# ----------------------------------------------------------

alpha = 0.05

print("\nH2 DECISION")
print("-----------")

if p_value < alpha and coefficient > 0:

    print(
        "Reject H0. The results support H2: "
        "warmer periods have a significantly higher "
        "expected nightly pest-event rate."
    )

elif p_value < alpha and coefficient < 0:

    print(
        "Reject H0, but the observed effect is opposite "
        "to H2: warmer periods have a significantly lower "
        "expected nightly pest-event rate."
    )

else:

    print(
        "Fail to reject H0. There is insufficient "
        "statistical evidence that warmer periods have "
        "a higher expected nightly pest-event rate."
    )