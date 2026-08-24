import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features

st.title("Income Analysis")
st.write("Analysis of customer income and its relationship with credit risk.")

df = create_features(load_data())

# Filters
st.sidebar.header("Income Analysis Filters")

gender = st.sidebar.multiselect(
    "Gender",
    df["CODE_GENDER"].dropna().unique(),
    format_func=lambda x: {"M": "Male", "F": "Female"}.get(x, x),
    key="income_filter_gender"
)

education = st.sidebar.multiselect(
    "Education",
    df["NAME_EDUCATION_TYPE"].dropna().unique(),
    key="income_filter_education"
)

income_type = st.sidebar.multiselect(
    "Income Type",
    df["NAME_INCOME_TYPE"].dropna().unique(),
    key="income_filter_type"
)

occupation = st.sidebar.multiselect(
    "Occupation",
    df["OCCUPATION_TYPE"].dropna().unique(),
    key="income_filter_occupation"
)

if gender:
    df = df[df["CODE_GENDER"].isin(gender)]
if education:
    df = df[df["NAME_EDUCATION_TYPE"].isin(education)]
if income_type:
    df = df[df["NAME_INCOME_TYPE"].isin(income_type)]
if occupation:
    df = df[df["OCCUPATION_TYPE"].isin(occupation)]

# Income Groups
income_labels = [
    "Below 50K",
    "50K–100K",
    "100K–150K",
    "150K–200K",
    "200K–300K",
    "300K–500K",
    "Above 500K"
]

df["INCOME_GROUP"] = pd.cut(
    df["AMT_INCOME_TOTAL"],
    bins=[0, 50000, 100000, 150000, 200000, 300000, 500000, float("inf")],
    labels=income_labels,
    include_lowest=True
)

# KPIs
total_income = df["AMT_INCOME_TOTAL"].sum()
average_income = df["AMT_INCOME_TOTAL"].mean()
median_income = df["AMT_INCOME_TOTAL"].median()
maximum_income = df["AMT_INCOME_TOTAL"].max()
default_income = df.loc[df["TARGET"] == 1, "AMT_INCOME_TOTAL"].mean()

st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₹{total_income:,.0f}")
col2.metric("Average Income", f"₹{average_income:,.0f}")
col3.metric("Median Income", f"₹{median_income:,.0f}")

col1, col2 = st.columns(2)
col1.metric("Maximum Income", f"₹{maximum_income:,.0f}")
col2.metric("Average Income of Defaulters", f"₹{default_income:,.0f}")

# 1. Income Distribution
st.subheader("Income Distribution")

income_data = df[["AMT_INCOME_TOTAL"]].dropna()
income_limit = income_data["AMT_INCOME_TOTAL"].quantile(0.99)
income_graph = income_data[income_data["AMT_INCOME_TOTAL"] <= income_limit]

fig = px.histogram(
    income_graph,
    x="AMT_INCOME_TOTAL",
    nbins=30,
    title="Income Distribution"
)

fig.update_xaxes(
    title="Income",
    tickformat=",",
    range=[0, income_limit]
)

fig.update_yaxes(title="Number of Customers")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_distribution_chart"
)

st.markdown(f"""
**Insights:**
- Average income is **₹{average_income:,.0f}**, while median income is **₹{median_income:,.0f}**.
- The middle 50% of customers have income between **₹{df["AMT_INCOME_TOTAL"].quantile(0.25):,.0f}** and **₹{df["AMT_INCOME_TOTAL"].quantile(0.75):,.0f}**.
- The chart uses the 99th percentile to reduce the effect of extreme income values.
""")

# 2. Customers by Income Group
st.subheader("Customers by Income Group")

income_group_data = (
    df["INCOME_GROUP"]
    .value_counts()
    .reindex(income_labels)
    .fillna(0)
    .reset_index()
)

income_group_data.columns = ["Income Group", "Customers"]

fig = px.bar(
    income_group_data,
    x="Income Group",
    y="Customers",
    title="Customers by Income Group"
)

fig.update_yaxes(title="Number of Customers")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_group_chart"
)

top_group = income_group_data.loc[
    income_group_data["Customers"].idxmax()
]

st.markdown(f"""
**Insights:**
- **{top_group["Income Group"]}** has the highest number of customers.
- It contains **{top_group["Customers"]:,.0f}** customers.
- Customer distribution varies across the defined income ranges.
""")

# 3. Default Rate by Income Group
st.subheader("Default Rate by Income Group")

default_income_data = (
    df.groupby("INCOME_GROUP", observed=True)["TARGET"]
    .mean()
    .mul(100)
    .reindex(income_labels)
    .reset_index()
)

default_income_data.columns = ["Income Group", "Default Rate"]

fig = px.line(
    default_income_data,
    x="Income Group",
    y="Default Rate",
    markers=True,
    title="Default Rate by Income Group"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_default_group_chart"
)

high_risk = default_income_data.loc[
    default_income_data["Default Rate"].idxmax()
]

low_risk = default_income_data.loc[
    default_income_data["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{high_risk["Income Group"]}** has the highest default rate at **{high_risk["Default Rate"]:.2f}%**.
- **{low_risk["Income Group"]}** has the lowest default rate at **{low_risk["Default Rate"]:.2f}%**.
- Default risk differs across income groups.
""")

# 4. Income vs Credit
st.subheader("Income vs Credit")

income_credit = df[
    ["AMT_INCOME_TOTAL", "AMT_CREDIT"]
].dropna()

income_limit = income_credit["AMT_INCOME_TOTAL"].quantile(0.99)
credit_limit = income_credit["AMT_CREDIT"].quantile(0.99)

income_credit = income_credit[
    (income_credit["AMT_INCOME_TOTAL"] <= income_limit) &
    (income_credit["AMT_CREDIT"] <= credit_limit)
]

fig = px.scatter(
    income_credit,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    opacity=0.4,
    title="Income vs Credit"
)

fig.update_xaxes(
    title="Income",
    range=[0, income_limit],
    tickformat=","
)

fig.update_yaxes(
    title="Credit Amount",
    range=[0, credit_limit],
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_credit_scatter_chart"
)

correlation = income_credit["AMT_INCOME_TOTAL"].corr(
    income_credit["AMT_CREDIT"]
)

st.markdown(f"""
**Insights:**
- Income and credit have a correlation of **{correlation:.2f}**.
- Higher-income customers generally tend to receive higher credit amounts.
- The spread shows that income is not the only factor determining credit amount.
""")

# 5. Income vs Annuity
st.subheader("Income vs Annuity")

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
    title="Income vs Annuity"
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
    key="income_annuity_scatter_chart"
)

correlation = income_annuity["AMT_INCOME_TOTAL"].corr(
    income_annuity["AMT_ANNUITY"]
)

st.markdown(f"""
**Insights:**
- Income and annuity have a correlation of **{correlation:.2f}**.
- Higher-income customers generally tend to have higher annuity obligations.
- The spread indicates that annuity is influenced by factors other than income.
""")

# 6. Income by Education
st.subheader("Income by Education")

education_income = (
    df.groupby("NAME_EDUCATION_TYPE")["AMT_INCOME_TOTAL"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

education_income.columns = [
    "Education",
    "Average Income"
]

fig = px.bar(
    education_income,
    x="Education",
    y="Average Income",
    title="Average Income by Education"
)

fig.update_xaxes(tickangle=-25)
fig.update_yaxes(
    title="Average Income",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_by_education_chart"
)

highest_education = education_income.iloc[0]
lowest_education = education_income.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_education["Education"]}** has the highest average income at **₹{highest_education["Average Income"]:,.0f}**.
- **{lowest_education["Education"]}** has the lowest average income at **₹{lowest_education["Average Income"]:,.0f}**.
- Average income differs across education groups.
""")

# 7. Income by Occupation
st.subheader("Income by Occupation")

occupation_income = (
    df.dropna(subset=["OCCUPATION_TYPE"])
    .groupby("OCCUPATION_TYPE")["AMT_INCOME_TOTAL"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

occupation_income.columns = [
    "Occupation",
    "Average Income"
]

fig = px.bar(
    occupation_income,
    x="Occupation",
    y="Average Income",
    title="Average Income by Occupation"
)

fig.update_xaxes(tickangle=-30)
fig.update_yaxes(
    title="Average Income",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_by_occupation_chart"
)

highest_occupation = occupation_income.iloc[0]
lowest_occupation = occupation_income.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_occupation["Occupation"]}** has the highest average income at **₹{highest_occupation["Average Income"]:,.0f}**.
- **{lowest_occupation["Occupation"]}** has the lowest average income at **₹{lowest_occupation["Average Income"]:,.0f}**.
- Income levels vary considerably across occupations.
""")
