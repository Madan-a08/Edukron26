import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("External Credit Score Analysis")
st.write("Analysis of external credit scores and their relationship with credit risk.")

df = load_data()
df = create_features(df)
df = apply_filters(df)

df["AVERAGE_EXTERNAL_SCORE"] = df[
    ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
].mean(axis=1)

# KPIs
average_score_1 = df["EXT_SOURCE_1"].mean()
average_score_2 = df["EXT_SOURCE_2"].mean()
average_score_3 = df["EXT_SOURCE_3"].mean()

missing_external_scores = df[
    ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
].isna().all(axis=1).sum()

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average EXT_SOURCE_1", f"{average_score_1:.2f}")
col2.metric("Average EXT_SOURCE_2", f"{average_score_2:.2f}")
col3.metric("Average EXT_SOURCE_3", f"{average_score_3:.2f}")
col4.metric("Missing External Scores", f"{missing_external_scores:,}")

# 1. EXT_SOURCE_1 Distribution
st.subheader("EXT_SOURCE_1 Distribution")

score_1 = df[["EXT_SOURCE_1"]].dropna()

fig = px.histogram(
    score_1,
    x="EXT_SOURCE_1",
    nbins=30,
    title="EXT_SOURCE_1 Distribution",
    color_discrete_sequence=["#636EFA"]
)
fig.update_xaxes(title="EXT_SOURCE_1 Score")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="ext_source_1_distribution")

source1_median = df["EXT_SOURCE_1"].median()
source1_min = df["EXT_SOURCE_1"].min()
source1_max = df["EXT_SOURCE_1"].max()

st.markdown(
    f"""
**Insights:**
- The average EXT_SOURCE_1 score is **{average_score_1:.2f}**.
- The median EXT_SOURCE_1 score is **{source1_median:.2f}**.
- Scores range from approximately **{source1_min:.2f} to {source1_max:.2f}**.
"""
)

# 2. EXT_SOURCE_2 Distribution
st.subheader("EXT_SOURCE_2 Distribution")

score_2 = df[["EXT_SOURCE_2"]].dropna()

fig = px.histogram(
    score_2,
    x="EXT_SOURCE_2",
    nbins=30,
    title="EXT_SOURCE_2 Distribution",
    color_discrete_sequence=["#00CC96"]
)
fig.update_xaxes(title="EXT_SOURCE_2 Score")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="ext_source_2_distribution")

source2_median = df["EXT_SOURCE_2"].median()
source2_min = df["EXT_SOURCE_2"].min()
source2_max = df["EXT_SOURCE_2"].max()

st.markdown(
    f"""
**Insights:**
- The average EXT_SOURCE_2 score is **{average_score_2:.2f}**.
- The median EXT_SOURCE_2 score is **{source2_median:.2f}**.
- Scores range from approximately **{source2_min:.2f} to {source2_max:.2f}**.
"""
)

# 3. EXT_SOURCE_3 Distribution
st.subheader("EXT_SOURCE_3 Distribution")

score_3 = df[["EXT_SOURCE_3"]].dropna()

fig = px.histogram(
    score_3,
    x="EXT_SOURCE_3",
    nbins=30,
    title="EXT_SOURCE_3 Distribution",
    color_discrete_sequence=["#EF553B"]
)
fig.update_xaxes(title="EXT_SOURCE_3 Score")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="ext_source_3_distribution")

source3_median = df["EXT_SOURCE_3"].median()
source3_min = df["EXT_SOURCE_3"].min()
source3_max = df["EXT_SOURCE_3"].max()

st.markdown(
    f"""
**Insights:**
- The average EXT_SOURCE_3 score is **{average_score_3:.2f}**.
- The median EXT_SOURCE_3 score is **{source3_median:.2f}**.
- Scores range from approximately **{source3_min:.2f} to {source3_max:.2f}**.
"""
)

# 4. External Scores by TARGET
st.subheader("External Scores by TARGET")

score_target = df[
    ["TARGET", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
].dropna(
    how="all",
    subset=["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
).copy()

score_target["TARGET"] = score_target["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

score_target = score_target.melt(
    id_vars="TARGET",
    value_vars=["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"],
    var_name="External Score",
    value_name="Score"
)

fig = px.box(
    score_target,
    x="External Score",
    y="Score",
    color="TARGET",
    title="External Scores by TARGET",
    color_discrete_map={
        "Non-Default": "#00CC96",
        "Default": "#EF553B"
    }
)
fig.update_xaxes(title="External Score")
fig.update_yaxes(title="Score")
st.plotly_chart(fig, use_container_width=True, key="external_scores_target")

default_scores = score_target[score_target["TARGET"] == "Default"].groupby(
    "External Score"
)["Score"].mean()

non_default_scores = score_target[
    score_target["TARGET"] == "Non-Default"
].groupby("External Score")["Score"].mean()

lowest_default_score = default_scores.idxmin()
lowest_default_value = default_scores.min()

highest_non_default_score = non_default_scores.idxmax()
highest_non_default_value = non_default_scores.max()

st.markdown(
    f"""
**Insights:**
- Among defaulters, **{lowest_default_score}** has the lowest average score at approximately **{lowest_default_value:.2f}**.
- Among non-defaulters, **{highest_non_default_score}** has the highest average score at approximately **{highest_non_default_value:.2f}**.
- External scores generally help distinguish customers with different levels of credit risk.
"""
)

# 5. EXT_SOURCE_1 vs EXT_SOURCE_2
st.subheader("EXT_SOURCE_1 vs EXT_SOURCE_2")

score_12 = df[
    ["EXT_SOURCE_1", "EXT_SOURCE_2"]
].dropna()

correlation_12 = score_12["EXT_SOURCE_1"].corr(score_12["EXT_SOURCE_2"])

fig = px.scatter(
    score_12,
    x="EXT_SOURCE_1",
    y="EXT_SOURCE_2",
    opacity=0.35,
    title="EXT_SOURCE_1 vs EXT_SOURCE_2",
    color_discrete_sequence=["#AB63FA"]
)
fig.update_xaxes(title="EXT_SOURCE_1")
fig.update_yaxes(title="EXT_SOURCE_2")
st.plotly_chart(fig, use_container_width=True, key="ext_source_1_vs_2")

st.markdown(
    f"""
**Insights:**
- The correlation between EXT_SOURCE_1 and EXT_SOURCE_2 is **{correlation_12:.2f}**.
- The scatter plot shows how the two external scores move relative to each other.
- A positive correlation indicates that higher values of one score tend to be associated with higher values of the other.
"""
)

# 6. EXT_SOURCE_2 vs EXT_SOURCE_3
st.subheader("EXT_SOURCE_2 vs EXT_SOURCE_3")

score_23 = df[
    ["EXT_SOURCE_2", "EXT_SOURCE_3"]
].dropna()

correlation_23 = score_23["EXT_SOURCE_2"].corr(score_23["EXT_SOURCE_3"])

fig = px.scatter(
    score_23,
    x="EXT_SOURCE_2",
    y="EXT_SOURCE_3",
    opacity=0.35,
    title="EXT_SOURCE_2 vs EXT_SOURCE_3",
    color_discrete_sequence=["#FFA15A"]
)
fig.update_xaxes(title="EXT_SOURCE_2")
fig.update_yaxes(title="EXT_SOURCE_3")
st.plotly_chart(fig, use_container_width=True, key="ext_source_2_vs_3")

st.markdown(
    f"""
**Insights:**
- The correlation between EXT_SOURCE_2 and EXT_SOURCE_3 is **{correlation_23:.2f}**.
- The plot shows the relationship between the two external credit scores.
- The concentration of points indicates the most common score combinations among applicants.
"""
)

# 7. External Score vs Default Rate
st.subheader("External Score vs Default Rate")

score_risk = df[
    ["AVERAGE_EXTERNAL_SCORE", "TARGET"]
].dropna()

score_risk["Score Group"] = pd.cut(
    score_risk["AVERAGE_EXTERNAL_SCORE"],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    labels=[
        "0.00–0.20",
        "0.21–0.40",
        "0.41–0.60",
        "0.61–0.80",
        "0.81–1.00"
    ],
    include_lowest=True
)

default_by_score = (
    score_risk.groupby(
        "Score Group",
        observed=False
    )["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

default_by_score.columns = [
    "Score Group",
    "Default Rate"
]

fig = px.line(
    default_by_score,
    x="Score Group",
    y="Default Rate",
    markers=True,
    text="Default Rate",
    title="Default Rate by Average External Score",
    color_discrete_sequence=["#EF553B"]
)
fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="top center"
)
fig.update_xaxes(title="Average External Score")
fig.update_yaxes(title="Default Rate (%)")
st.plotly_chart(fig, use_container_width=True,
                key="external_score_default_rate")

valid_rates = default_by_score.dropna()

if not valid_rates.empty:
    highest_risk = valid_rates.loc[
        valid_rates["Default Rate"].idxmax()
    ]
    lowest_risk = valid_rates.loc[
        valid_rates["Default Rate"].idxmin()
    ]

    st.markdown(
        f"""
**Insights:**
- The **{highest_risk['Score Group']}** score group has the highest default rate at **{highest_risk['Default Rate']:.2f}%**.
- The **{lowest_risk['Score Group']}** score group has the lowest default rate at **{lowest_risk['Default Rate']:.2f}%**.
- The graph shows that external credit scores can be used as an indicator of customer default risk.
"""
    )
