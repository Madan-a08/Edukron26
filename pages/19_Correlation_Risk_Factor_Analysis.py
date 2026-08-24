import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Correlation & Risk Factor Analysis")
st.write("Analysis of numerical relationships associated with loan default.")

df = load_data()
df = create_features(df)
df = apply_filters(df)

# Important numerical features
features = [
    "TARGET",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS"
]

features = [column for column in features if column in df.columns]
corr = df[features].corr()

# 1. Correlation Heatmap
st.subheader("Correlation Heatmap")

fig = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    title="Correlation Between Numerical Features",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="correlation_heatmap"
)

target_corr_values = corr["TARGET"].drop("TARGET")
strongest_corr = target_corr_values.abs().idxmax()
strongest_value = target_corr_values[strongest_corr]

st.markdown(
    f"""
**Insights:**
- **{strongest_corr}** has the strongest correlation with TARGET among the selected numerical features.
- Correlation values close to **+1 or -1** indicate stronger relationships, while values close to **0** indicate weaker linear relationships.
- The heatmap provides an overall view of relationships between numerical variables.
"""
)

# Correlation with TARGET
target_corr = (
    corr["TARGET"]
    .drop("TARGET")
    .sort_values()
    .reset_index()
)

target_corr.columns = ["Feature", "Correlation"]

# 2. Correlation with TARGET
st.subheader("Correlation with TARGET")

fig = px.bar(
    target_corr,
    x="Correlation",
    y="Feature",
    orientation="h",
    text="Correlation",
    title="Correlation of Features with TARGET",
    color="Correlation",
    color_continuous_scale="RdBu_r",
    range_color=[-1, 1]
)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_xaxes(
    title="Correlation",
    range=[-1, 1]
)

fig.update_yaxes(title="Feature")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="target_correlation"
)

positive_count = (target_corr["Correlation"] > 0).sum()
negative_count = (target_corr["Correlation"] < 0).sum()

st.markdown(
    f"""
**Insights:**
- **{positive_count} features** have a positive correlation with TARGET.
- **{negative_count} features** have a negative correlation with TARGET.
- The direction of correlation indicates whether the feature tends to increase or decrease as TARGET increases.
"""
)

# 3. Top Positive Correlations
st.subheader("Top Positive Correlations")

positive_corr = (
    target_corr[target_corr["Correlation"] > 0]
    .sort_values("Correlation", ascending=True)
    .tail(5)
)

fig = px.bar(
    positive_corr,
    x="Correlation",
    y="Feature",
    orientation="h",
    text="Correlation",
    title="Top Positive Correlations with TARGET",
    color="Correlation",
    color_continuous_scale="Reds"
)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_xaxes(title="Positive Correlation")
fig.update_yaxes(title="Feature")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="positive_correlations"
)

if not positive_corr.empty:
    top_positive = positive_corr.iloc[-1]

    st.markdown(
        f"""
**Insights:**
- **{top_positive['Feature']}** has the strongest positive correlation with TARGET at **{top_positive['Correlation']:.2f}**.
- Positive correlation means higher values of the feature are associated with higher TARGET values.
- These relationships can be investigated further as potential risk indicators.
"""
    )

# 4. Top Negative Correlations
st.subheader("Top Negative Correlations")

negative_corr = (
    target_corr[target_corr["Correlation"] < 0]
    .sort_values("Correlation")
    .head(5)
)

fig = px.bar(
    negative_corr,
    x="Correlation",
    y="Feature",
    orientation="h",
    text="Correlation",
    title="Top Negative Correlations with TARGET",
    color="Correlation",
    color_continuous_scale="Blues_r"
)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_xaxes(title="Negative Correlation")
fig.update_yaxes(title="Feature")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="negative_correlations"
)

if not negative_corr.empty:
    strongest_negative = negative_corr.iloc[0]

    st.markdown(
        f"""
**Insights:**
- **{strongest_negative['Feature']}** has the strongest negative correlation with TARGET at **{strongest_negative['Correlation']:.2f}**.
- Negative correlation means higher values of the feature are associated with lower TARGET values.
- Strong negative relationships may indicate variables associated with lower default risk.
"""
    )

# 5. Credit vs Income Scatter Plot
st.subheader("Credit vs Income")

credit_income = df[
    ["AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET"]
].dropna()

income_max = credit_income["AMT_INCOME_TOTAL"].quantile(0.99)
credit_max = credit_income["AMT_CREDIT"].quantile(0.99)

credit_income = credit_income[
    (credit_income["AMT_INCOME_TOTAL"] <= income_max) &
    (credit_income["AMT_CREDIT"] <= credit_max)
]

credit_income["Status"] = credit_income["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

fig = px.scatter(
    credit_income,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    color="Status",
    opacity=0.5,
    title="Credit vs Income",
    color_discrete_map={
        "Non-Default": "#636EFA",
        "Default": "#EF553B"
    }
)

fig.update_xaxes(
    title="Income",
    tickformat=","
)

fig.update_yaxes(
    title="Credit Amount",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="credit_income_scatter"
)

credit_income_corr = credit_income[
    ["AMT_INCOME_TOTAL", "AMT_CREDIT"]
].corr().iloc[0, 1]

st.markdown(
    f"""
**Insights:**
- Income and credit amount have a correlation of approximately **{credit_income_corr:.2f}**.
- Higher-income applicants generally tend to have higher credit amounts.
- The color separation allows default and non-default applicants to be compared across income and credit levels.
"""
)

# 6. External Score vs TARGET
st.subheader("External Score vs TARGET")

external_data = df[
    [
        "TARGET",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3"
    ]
].copy()

external_data["TARGET"] = external_data["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

external_data = external_data.melt(
    id_vars="TARGET",
    value_vars=[
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3"
    ],
    var_name="External Score",
    value_name="Score"
).dropna()

fig = px.box(
    external_data,
    x="External Score",
    y="Score",
    color="TARGET",
    title="External Scores by TARGET",
    color_discrete_map={
        "Non-Default": "#636EFA",
        "Default": "#EF553B"
    }
)

fig.update_xaxes(title="External Score")
fig.update_yaxes(title="Score")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="external_score_target"
)

default_scores = (
    external_data[external_data["TARGET"] == "Default"]
    .groupby("External Score")["Score"]
    .mean()
)

non_default_scores = (
    external_data[external_data["TARGET"] == "Non-Default"]
    .groupby("External Score")["Score"]
    .mean()
)

st.markdown(
    """
**Insights:**
- External credit scores show a visible difference between default and non-default customers.
- Lower external scores are generally associated with greater credit risk.
- EXT_SOURCE variables can therefore be useful indicators when assessing default risk.
"""
)

# Important Risk Factors
st.subheader("Important Risk Factors")

risk_factors = pd.DataFrame({
    "Potential Risk Indicator": [
        "Low External Credit Score",
        "High Credit-to-Income Ratio",
        "High Annuity-to-Income Ratio",
        "Certain Occupations",
        "Certain Income Types",
        "Younger Age Groups",
        "Regional Risk Rating",
        "Employment History"
    ],
    "Analysis": [
        "Compare low external scores with default rates.",
        "Check whether higher credit relative to income is associated with higher default.",
        "Check whether higher repayment burden is associated with higher default.",
        "Compare default rates across occupations.",
        "Compare default rates across income types.",
        "Compare default rates across age groups.",
        "Compare default rates across regional ratings.",
        "Compare employment history with default rates."
    ]
})

st.dataframe(
    risk_factors,
    use_container_width=True,
    hide_index=True
)
