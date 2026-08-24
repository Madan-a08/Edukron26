import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Annuity Analysis")
st.write("Analysis of customer loan payment obligations.")

df = apply_filters(create_features(load_data()))

# Annuity Groups
annuity_labels = [
    "Below 10K",
    "10K–20K",
    "20K–30K",
    "30K–50K",
    "50K–75K",
    "75K–100K",
    "Above 100K"
]

df["ANNUITY_GROUP"] = pd.cut(
    df["AMT_ANNUITY"],
    bins=[0, 10000, 20000, 30000, 50000, 75000, 100000, float("inf")],
    labels=annuity_labels,
    include_lowest=True
)

# KPIs
average_annuity = df["AMT_ANNUITY"].mean()
median_annuity = df["AMT_ANNUITY"].median()
maximum_annuity = df["AMT_ANNUITY"].max()
average_annuity_defaulters = df.loc[
    df["TARGET"] == 1,
    "AMT_ANNUITY"
].mean()

st.subheader("Key Performance Indicators")

col1, col2 = st.columns(2)
col1.metric("Average Annuity", f"₹{average_annuity:,.0f}")
col2.metric("Median Annuity", f"₹{median_annuity:,.0f}")

col1, col2 = st.columns(2)
col1.metric("Maximum Annuity", f"₹{maximum_annuity:,.0f}")
col2.metric("Avg Annuity for Defaulters",
            f"₹{average_annuity_defaulters:,.0f}")

# 1. Annuity Distribution
st.subheader("Annuity Distribution")

annuity_data = df[["AMT_ANNUITY"]].dropna()
annuity_limit = annuity_data["AMT_ANNUITY"].quantile(0.99)
annuity_graph = annuity_data[
    annuity_data["AMT_ANNUITY"] <= annuity_limit
]

fig = px.histogram(
    annuity_graph,
    x="AMT_ANNUITY",
    nbins=30,
    title="Annuity Distribution"
)

fig.update_xaxes(
    title="Annuity Amount",
    tickformat=",",
    range=[0, annuity_limit]
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_distribution_chart"
)

st.markdown(f"""
**Insights:**
- Average annuity is **₹{average_annuity:,.0f}**, while the median is **₹{median_annuity:,.0f}**.
- The middle 50% of customers have annuity amounts between **₹{df["AMT_ANNUITY"].quantile(0.25):,.0f}** and **₹{df["AMT_ANNUITY"].quantile(0.75):,.0f}**.
- The chart uses the 99th percentile to reduce the effect of extreme annuity values.
""")

# 2. Annuity by TARGET
st.subheader("Annuity by TARGET")

target_data = df[
    ["TARGET", "AMT_ANNUITY"]
].copy()

target_data["TARGET"] = target_data["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

fig = px.box(
    target_data,
    x="TARGET",
    y="AMT_ANNUITY",
    title="Annuity by TARGET"
)

fig.update_yaxes(
    title="Annuity Amount",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_target_chart"
)

target_annuity = df.groupby("TARGET")["AMT_ANNUITY"].mean()

non_default_annuity = target_annuity.get(0, 0)
default_annuity = target_annuity.get(1, 0)

st.markdown(f"""
**Insights:**
- Average annuity for non-default customers is **₹{non_default_annuity:,.0f}**.
- Average annuity for default customers is **₹{default_annuity:,.0f}**.
- The box plot shows the spread and median annuity for both customer groups.
""")

# 3. Annuity vs Income
st.subheader("Annuity vs Income")

income_annuity = df[
    ["AMT_INCOME_TOTAL", "AMT_ANNUITY"]
].dropna()

income_limit = income_annuity["AMT_INCOME_TOTAL"].quantile(0.99)
annuity_limit = income_annuity["AMT_ANNUITY"].quantile(0.99)

income_annuity = income_annuity[
    (income_annuity["AMT_INCOME_TOTAL"] <= income_limit) &
    (income_annuity["AMT_ANNUITY"] <= annuity_limit)
]

fig = px.scatter(
    income_annuity,
    x="AMT_INCOME_TOTAL",
    y="AMT_ANNUITY",
    opacity=0.4,
    title="Annuity vs Income"
)

fig.update_xaxes(
    title="Income",
    range=[0, income_limit],
    tickformat=","
)

fig.update_yaxes(
    title="Annuity",
    range=[0, annuity_limit],
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_income_scatter_chart"
)

correlation = income_annuity["AMT_INCOME_TOTAL"].corr(
    income_annuity["AMT_ANNUITY"]
)

st.markdown(f"""
**Insights:**
- Income and annuity have a correlation of **{correlation:.2f}**.
- Higher-income customers generally tend to have higher annuity amounts.
- The spread shows that income alone does not determine the annuity obligation.
""")

# 4. Annuity vs Credit
st.subheader("Annuity vs Credit")

credit_annuity = df[
    ["AMT_CREDIT", "AMT_ANNUITY"]
].dropna()

credit_limit = credit_annuity["AMT_CREDIT"].quantile(0.99)
annuity_limit = credit_annuity["AMT_ANNUITY"].quantile(0.99)

credit_annuity = credit_annuity[
    (credit_annuity["AMT_CREDIT"] <= credit_limit) &
    (credit_annuity["AMT_ANNUITY"] <= annuity_limit)
]

fig = px.scatter(
    credit_annuity,
    x="AMT_CREDIT",
    y="AMT_ANNUITY",
    opacity=0.4,
    title="Annuity vs Credit"
)

fig.update_xaxes(
    title="Credit Amount",
    range=[0, credit_limit],
    tickformat=","
)

fig.update_yaxes(
    title="Annuity",
    range=[0, annuity_limit],
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_credit_scatter_chart"
)

correlation = credit_annuity["AMT_CREDIT"].corr(
    credit_annuity["AMT_ANNUITY"]
)

st.markdown(f"""
**Insights:**
- Credit amount and annuity have a correlation of **{correlation:.2f}**.
- Larger credit amounts generally tend to be associated with higher annuity obligations.
- The scatter shows variation in annuity amounts for similar credit amounts.
""")

# 5. Average Annuity by Income Type
st.subheader("Average Annuity by Income Type")

income_type_annuity = (
    df.groupby("NAME_INCOME_TYPE")["AMT_ANNUITY"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

income_type_annuity.columns = [
    "Income Type",
    "Average Annuity"
]

fig = px.bar(
    income_type_annuity,
    x="Income Type",
    y="Average Annuity",
    title="Average Annuity by Income Type"
)

fig.update_xaxes(tickangle=-30)
fig.update_yaxes(
    title="Average Annuity",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_income_type_chart"
)

highest_income_type = income_type_annuity.iloc[0]
lowest_income_type = income_type_annuity.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_income_type["Income Type"]}** has the highest average annuity at **₹{highest_income_type["Average Annuity"]:,.0f}**.
- **{lowest_income_type["Income Type"]}** has the lowest average annuity at **₹{lowest_income_type["Average Annuity"]:,.0f}**.
- Annuity obligations vary across different income types.
""")

# 6. Default Rate by Annuity Group
st.subheader("Default Rate by Annuity Group")

annuity_default = (
    df.groupby(
        "ANNUITY_GROUP",
        observed=True
    )["TARGET"]
    .mean()
    .mul(100)
    .reindex(annuity_labels)
    .reset_index()
)

annuity_default.columns = [
    "Annuity Group",
    "Default Rate"
]

fig = px.line(
    annuity_default,
    x="Annuity Group",
    y="Default Rate",
    markers=True,
    title="Default Rate by Annuity Group"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_default_group_chart"
)

highest_risk = annuity_default.loc[
    annuity_default["Default Rate"].idxmax()
]

lowest_risk = annuity_default.loc[
    annuity_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{highest_risk["Annuity Group"]}** has the highest default rate at **{highest_risk["Default Rate"]:.2f}%**.
- **{lowest_risk["Annuity Group"]}** has the lowest default rate at **{lowest_risk["Default Rate"]:.2f}%**.
- Default risk varies across different annuity ranges.
""")
