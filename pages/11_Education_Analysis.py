import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Education Analysis")
st.write("Analysis of applicants according to education level.")

df = apply_filters(create_features(load_data()))

# Credit-to-Income Ratio
df["CREDIT_INCOME_RATIO"] = (
    df["AMT_CREDIT"] /
    df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
)

# KPI Calculations
education_count = df["NAME_EDUCATION_TYPE"].value_counts()
most_common_education = education_count.idxmax()

education_income = df.groupby(
    "NAME_EDUCATION_TYPE"
)["AMT_INCOME_TOTAL"].mean()

highest_income_education = education_income.idxmax()

education_default = df.groupby(
    "NAME_EDUCATION_TYPE"
)["TARGET"].mean()

lowest_default_education = education_default.idxmin()
highest_default_education = education_default.idxmax()

# KPI Cards
st.subheader("Key Performance Indicators")

col1, col2 = st.columns(2)

col1.metric(
    "Most Common Education",
    most_common_education
)

col2.metric(
    "Highest Income Education",
    highest_income_education
)

col1, col2 = st.columns(2)

col1.metric(
    "Lowest Default Education",
    lowest_default_education
)

col2.metric(
    "Highest Default Education",
    highest_default_education
)

# 1. Customers by Education
st.subheader("Customers by Education")

education_count = (
    df["NAME_EDUCATION_TYPE"]
    .value_counts()
    .reset_index()
)

education_count.columns = [
    "Education",
    "Customers"
]

fig = px.bar(
    education_count,
    x="Education",
    y="Customers",
    title="Customers by Education"
)

fig.update_xaxes(
    title="Education",
    tickangle=-25
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="education_customers"
)

common_count = education_count.iloc[0]
least_count = education_count.iloc[-1]

st.markdown(f"""
**Insights:**
- **{common_count["Education"]}** has the highest number of customers.
- **{least_count["Education"]}** has the lowest number of customers.
- The customer population is concentrated in a few major education categories.
""")

# 2. Default Rate by Education
st.subheader("Default Rate by Education")

education_default_data = (
    df.groupby("NAME_EDUCATION_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)

education_default_data.columns = [
    "Education",
    "Default Rate"
]

fig = px.bar(
    education_default_data,
    x="Education",
    y="Default Rate",
    title="Default Rate by Education"
)

fig.update_xaxes(
    title="Education",
    tickangle=-25
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="education_default_rate"
)

highest_default = education_default_data.iloc[0]
lowest_default = education_default_data.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_default["Education"]}** has the highest default rate at **{highest_default["Default Rate"]:.2f}%**.
- **{lowest_default["Education"]}** has the lowest default rate at **{lowest_default["Default Rate"]:.2f}%**.
- Default risk varies across education categories.
""")

# 3. Income by Education
st.subheader("Income by Education")

income_max = df["AMT_INCOME_TOTAL"].quantile(0.99)

income_graph = df[
    df["AMT_INCOME_TOTAL"] <= income_max
]

fig = px.box(
    income_graph,
    x="NAME_EDUCATION_TYPE",
    y="AMT_INCOME_TOTAL",
    title="Income Distribution by Education"
)

fig.update_xaxes(
    title="Education",
    tickangle=-25
)

fig.update_yaxes(
    title="Income",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="education_income_distribution"
)

income_sorted = education_income.sort_values(ascending=False)

st.markdown(f"""
**Insights:**
- **{income_sorted.index[0]}** has the highest average income.
- **{income_sorted.index[-1]}** has the lowest average income.
- Income distributions overlap across education groups, although their typical income levels differ.
""")

# 4. Credit by Education
st.subheader("Credit by Education")

credit_max = df["AMT_CREDIT"].quantile(0.99)

credit_graph = df[
    df["AMT_CREDIT"] <= credit_max
]

fig = px.box(
    credit_graph,
    x="NAME_EDUCATION_TYPE",
    y="AMT_CREDIT",
    title="Credit Distribution by Education"
)

fig.update_xaxes(
    title="Education",
    tickangle=-25
)

fig.update_yaxes(
    title="Credit Amount",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="education_credit_distribution"
)

education_credit = (
    df.groupby("NAME_EDUCATION_TYPE")["AMT_CREDIT"]
    .mean()
    .sort_values(ascending=False)
)

st.markdown(f"""
**Insights:**
- **{education_credit.index[0]}** has the highest average credit amount.
- **{education_credit.index[-1]}** has the lowest average credit amount.
- Credit amounts show variation within each education group, as visible from the box ranges.
""")

# 5. Annuity by Education
st.subheader("Annuity by Education")

annuity_max = df["AMT_ANNUITY"].quantile(0.99)

annuity_graph = df[
    df["AMT_ANNUITY"] <= annuity_max
]

fig = px.box(
    annuity_graph,
    x="NAME_EDUCATION_TYPE",
    y="AMT_ANNUITY",
    title="Annuity Distribution by Education"
)

fig.update_xaxes(
    title="Education",
    tickangle=-25
)

fig.update_yaxes(
    title="Annuity",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="education_annuity_distribution"
)

education_annuity = (
    df.groupby("NAME_EDUCATION_TYPE")["AMT_ANNUITY"]
    .mean()
    .sort_values(ascending=False)
)

st.markdown(f"""
**Insights:**
- **{education_annuity.index[0]}** has the highest average annuity.
- **{education_annuity.index[-1]}** has the lowest average annuity.
- Annuity amounts vary across education groups and also show variation within groups.
""")

# 6. Credit-to-Income Ratio by Education
st.subheader("Credit-to-Income Ratio by Education")

education_ratio = (
    df.groupby(
        "NAME_EDUCATION_TYPE"
    )["CREDIT_INCOME_RATIO"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

education_ratio.columns = [
    "Education",
    "Average Ratio"
]

fig = px.line(
    education_ratio,
    x="Education",
    y="Average Ratio",
    markers=True,
    title="Credit-to-Income Ratio by Education"
)

fig.update_xaxes(
    title="Education",
    tickangle=-25
)

fig.update_yaxes(
    title="Average Credit-to-Income Ratio"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="education_credit_income_ratio"
)

high_ratio = education_ratio.iloc[0]
low_ratio = education_ratio.iloc[-1]

st.markdown(f"""
**Insights:**
- **{high_ratio["Education"]}** has the highest average credit-to-income ratio at **{high_ratio["Average Ratio"]:.2f}**.
- **{low_ratio["Education"]}** has the lowest average ratio at **{low_ratio["Average Ratio"]:.2f}**.
- A higher ratio indicates greater credit exposure relative to customer income.
""")
