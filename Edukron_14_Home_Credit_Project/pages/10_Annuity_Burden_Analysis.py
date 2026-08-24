import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Annuity Burden Analysis")
st.write("Analysis of repayment burden relative to customer income.")

df = apply_filters(create_features(load_data()))

# Annuity-to-Income Ratio
df["ANNUITY_INCOME_RATIO"] = (
    df["AMT_ANNUITY"] /
    df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
)

df = df[df["ANNUITY_INCOME_RATIO"].notna()]

# Risk Groups
risk_labels = [
    "Low Repayment Burden",
    "Medium Repayment Burden",
    "High Repayment Burden",
    "Very High Repayment Burden"
]

df["RISK_GROUP"] = pd.cut(
    df["ANNUITY_INCOME_RATIO"],
    bins=[0, 0.20, 0.30, 0.40, float("inf")],
    labels=risk_labels,
    include_lowest=True
)

# KPIs
average_burden = df["ANNUITY_INCOME_RATIO"].mean()
highest_burden = df["ANNUITY_INCOME_RATIO"].max()

high_burden_default_rate = (
    df.loc[
        df["ANNUITY_INCOME_RATIO"] > 0.40,
        "TARGET"
    ].mean() * 100
)

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Annuity-to-Income Ratio",
    f"{average_burden:.2%}"
)

col2.metric(
    "Highest Annuity-to-Income Ratio",
    f"{highest_burden:.2%}"
)

col3.metric(
    "Default Rate for High Burden Customers",
    f"{high_burden_default_rate:.2f}%"
)

# 1. Annuity-to-Income Distribution
st.subheader("Annuity-to-Income Distribution")

ratio_max = df["ANNUITY_INCOME_RATIO"].quantile(0.99)

ratio_data = df[
    df["ANNUITY_INCOME_RATIO"] <= ratio_max
]

fig = px.histogram(
    ratio_data,
    x="ANNUITY_INCOME_RATIO",
    nbins=30,
    title="Annuity-to-Income Ratio Distribution"
)

fig.update_xaxes(
    title="Annuity-to-Income Ratio",
    tickformat=".0%"
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_income_distribution"
)

st.markdown(f"""
**Insights:**
- The average annuity-to-income ratio is **{average_burden:.2%}**.
- Most customers have their annuity concentrated in the lower burden range.
- Very high ratios are less common and represent customers with greater repayment pressure.
""")

# 2. Default Rate by Ratio
st.subheader("Default Rate by Repayment Burden")

ratio_default = (
    df.groupby(
        "RISK_GROUP",
        observed=True
    )["TARGET"]
    .mean()
    .mul(100)
    .reindex(risk_labels)
    .reset_index()
)

ratio_default.columns = [
    "Risk Group",
    "Default Rate"
]

fig = px.line(
    ratio_default,
    x="Risk Group",
    y="Default Rate",
    markers=True,
    title="Default Rate by Repayment Burden"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_rate_repayment_burden"
)

highest_risk = ratio_default.loc[
    ratio_default["Default Rate"].idxmax()
]

lowest_risk = ratio_default.loc[
    ratio_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{highest_risk["Risk Group"]}** has the highest default rate at **{highest_risk["Default Rate"]:.2f}%**.
- **{lowest_risk["Risk Group"]}** has the lowest default rate at **{lowest_risk["Default Rate"]:.2f}%**.
- Higher repayment burden can indicate greater pressure on customer income.
""")

# 3. Ratio by Gender
st.subheader("Ratio by Gender")

gender_ratio = (
    df.groupby("CODE_GENDER")["ANNUITY_INCOME_RATIO"]
    .mean()
    .reset_index()
)

gender_ratio["Gender"] = gender_ratio["CODE_GENDER"].map({
    "M": "Male",
    "F": "Female"
})

gender_ratio.columns = [
    "CODE_GENDER",
    "Average Ratio",
    "Gender"
]

fig = px.bar(
    gender_ratio,
    x="Gender",
    y="Average Ratio",
    title="Average Annuity-to-Income Ratio by Gender"
)

fig.update_yaxes(
    title="Average Annuity-to-Income Ratio",
    tickformat=".0%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_income_gender"
)

high_gender = gender_ratio.loc[
    gender_ratio["Average Ratio"].idxmax()
]

low_gender = gender_ratio.loc[
    gender_ratio["Average Ratio"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{high_gender["Gender"]}** has the higher average repayment burden at **{high_gender["Average Ratio"]:.2%}**.
- **{low_gender["Gender"]}** has the lower average repayment burden at **{low_gender["Average Ratio"]:.2%}**.
- The difference indicates that repayment burden varies across gender groups.
""")

# 4. Ratio by Income Type
st.subheader("Ratio by Income Type")

income_ratio = (
    df.groupby("NAME_INCOME_TYPE")["ANNUITY_INCOME_RATIO"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

income_ratio.columns = [
    "Income Type",
    "Average Ratio"
]

fig = px.bar(
    income_ratio,
    x="Income Type",
    y="Average Ratio",
    title="Average Annuity-to-Income Ratio by Income Type"
)

fig.update_xaxes(tickangle=-30)

fig.update_yaxes(
    title="Average Annuity-to-Income Ratio",
    tickformat=".0%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_income_type"
)

high_income = income_ratio.iloc[0]
low_income = income_ratio.iloc[-1]

st.markdown(f"""
**Insights:**
- **{high_income["Income Type"]}** has the highest average repayment burden at **{high_income["Average Ratio"]:.2%}**.
- **{low_income["Income Type"]}** has the lowest average repayment burden at **{low_income["Average Ratio"]:.2%}**.
- Income source is associated with differences in annuity burden across customer groups.
""")

# 5. Ratio by Education
st.subheader("Ratio by Education")

education_ratio = (
    df.groupby("NAME_EDUCATION_TYPE")["ANNUITY_INCOME_RATIO"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

education_ratio.columns = [
    "Education",
    "Average Ratio"
]

fig = px.bar(
    education_ratio,
    x="Education",
    y="Average Ratio",
    title="Average Annuity-to-Income Ratio by Education"
)

fig.update_xaxes(tickangle=-30)

fig.update_yaxes(
    title="Average Annuity-to-Income Ratio",
    tickformat=".0%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_education"
)

high_education = education_ratio.iloc[0]
low_education = education_ratio.iloc[-1]

st.markdown(f"""
**Insights:**
- **{high_education["Education"]}** has the highest average repayment burden at **{high_education["Average Ratio"]:.2%}**.
- **{low_education["Education"]}** has the lowest average repayment burden at **{low_education["Average Ratio"]:.2%}**.
- Repayment burden differs across education groups.
""")

# 6. Ratio vs TARGET
st.subheader("Ratio vs TARGET")

target_ratio = df[
    ["TARGET", "ANNUITY_INCOME_RATIO"]
].copy()

target_ratio["TARGET"] = target_ratio["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

fig = px.box(
    target_ratio,
    x="TARGET",
    y="ANNUITY_INCOME_RATIO",
    title="Annuity-to-Income Ratio vs TARGET"
)

fig.update_yaxes(
    title="Annuity-to-Income Ratio",
    tickformat=".0%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="annuity_income_target"
)

default_median = target_ratio.loc[
    target_ratio["TARGET"] == "Default",
    "ANNUITY_INCOME_RATIO"
].median()

non_default_median = target_ratio.loc[
    target_ratio["TARGET"] == "Non-Default",
    "ANNUITY_INCOME_RATIO"
].median()

st.markdown(f"""
**Insights:**
- The median repayment burden for defaulters is **{default_median:.2%}**.
- The median repayment burden for non-defaulters is **{non_default_median:.2%}**.
- The box plot shows how repayment burden differs between default and non-default customers.
""")

# Risk Group Summary
st.subheader("Repayment Burden Risk Groups")

risk_summary = (
    df.groupby(
        "RISK_GROUP",
        observed=True
    )
    .agg(
        Customers=("TARGET", "count"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reindex(risk_labels)
    .reset_index()
)

risk_summary["Default_Rate"] *= 100

risk_summary.columns = [
    "Risk Group",
    "Customers",
    "Defaults",
    "Default Rate"
]

st.dataframe(
    risk_summary,
    use_container_width=True,
    hide_index=True
)
