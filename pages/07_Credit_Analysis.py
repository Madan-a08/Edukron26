import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Credit Amount Analysis")
st.write("Analysis of the amount of credit requested by applicants.")

df = apply_filters(create_features(load_data()))

# Credit Groups
credit_labels = [
    "Below 100K", "100K–300K", "300K–500K",
    "500K–700K", "700K–1M", "Above 1M"
]
df["CREDIT_GROUP"] = pd.cut(
    df["AMT_CREDIT"],
    bins=[0, 100000, 300000, 500000, 700000, 1000000, float("inf")],
    labels=credit_labels,
    include_lowest=True
)

# KPIs
total_credit = df["AMT_CREDIT"].sum()
average_credit = df["AMT_CREDIT"].mean()
median_credit = df["AMT_CREDIT"].median()
maximum_credit = df["AMT_CREDIT"].max()
minimum_credit = df["AMT_CREDIT"].min()

st.subheader("Key Performance Indicators")
cols = st.columns(3)
cols[0].metric("Total Credit", f"₹{total_credit:,.0f}")
cols[1].metric("Average Credit", f"₹{average_credit:,.0f}")
cols[2].metric("Median Credit", f"₹{median_credit:,.0f}")

cols = st.columns(2)
cols[0].metric("Maximum Credit", f"₹{maximum_credit:,.0f}")
cols[1].metric("Minimum Credit", f"₹{minimum_credit:,.0f}")

# 1. Credit Amount Distribution
st.subheader("Credit Amount Distribution")
credit_data = df[["AMT_CREDIT"]].dropna()
credit_limit = credit_data["AMT_CREDIT"].quantile(0.99)
credit_graph = credit_data[credit_data["AMT_CREDIT"] <= credit_limit]

fig = px.histogram(
    credit_graph,
    x="AMT_CREDIT",
    nbins=30,
    title="Credit Amount Distribution"
)
fig.update_xaxes(title="Credit Amount", tickformat=",",
                 range=[0, credit_limit])
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="credit_distribution")

credit_p25 = df["AMT_CREDIT"].quantile(0.25)
credit_p75 = df["AMT_CREDIT"].quantile(0.75)
st.markdown(f"""
**Insights:**
- The average credit amount is **₹{average_credit:,.0f}**, while the median is **₹{median_credit:,.0f}**.
- The middle 50% of customers have credit amounts between approximately **₹{credit_p25:,.0f} and ₹{credit_p75:,.0f}**.
- The graph uses the **99th percentile** as the upper limit so extreme credit values do not compress the main distribution.
""")

# 2. Credit Amount by TARGET
st.subheader("Credit Amount by TARGET")
target_data = df[["TARGET", "AMT_CREDIT"]].copy()
target_data["TARGET"] = target_data["TARGET"].map(
    {0: "Non-Default", 1: "Default"})

fig = px.box(
    target_data,
    x="TARGET",
    y="AMT_CREDIT",
    title="Credit Amount by TARGET"
)
fig.update_yaxes(title="Credit Amount", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_target")

target_average = df.groupby("TARGET")["AMT_CREDIT"].mean()
default_avg = target_average.get(1, 0)
non_default_avg = target_average.get(0, 0)

st.markdown(f"""
**Insights:**
- The average credit for non-default customers is approximately **₹{non_default_avg:,.0f}**.
- The average credit for default customers is approximately **₹{default_avg:,.0f}**.
- The box plot shows the spread and median credit amounts for both customer groups.
""")

# 3. Average Credit by Gender
st.subheader("Average Credit by Gender")
gender_credit = df.groupby("CODE_GENDER")["AMT_CREDIT"].mean().reset_index()
gender_credit["Gender"] = gender_credit["CODE_GENDER"].map(
    {"M": "Male", "F": "Female"})
gender_credit.columns = ["CODE_GENDER", "Average Credit", "Gender"]

fig = px.bar(
    gender_credit,
    x="Gender",
    y="Average Credit",
    title="Average Credit by Gender"
)
fig.update_yaxes(title="Average Credit", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_gender")

high_gender = gender_credit.loc[gender_credit["Average Credit"].idxmax()]
low_gender = gender_credit.loc[gender_credit["Average Credit"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_gender["Gender"]}** has the higher average credit amount at approximately **₹{high_gender["Average Credit"]:,.0f}**.
- **{low_gender["Gender"]}** has the lower average credit amount at approximately **₹{low_gender["Average Credit"]:,.0f}**.
- Average credit levels differ between the gender groups.
""")

# 4. Credit by Income Type
st.subheader("Credit by Income Type")
income_credit = (
    df.groupby("NAME_INCOME_TYPE")["AMT_CREDIT"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
income_credit.columns = ["Income Type", "Average Credit"]

fig = px.bar(
    income_credit,
    x="Income Type",
    y="Average Credit",
    title="Average Credit by Income Type"
)
fig.update_xaxes(tickangle=-30)
fig.update_yaxes(title="Average Credit", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_income_type")

high_income = income_credit.iloc[0]
low_income = income_credit.iloc[-1]

st.markdown(f"""
**Insights:**
- **{high_income["Income Type"]}** has the highest average credit at approximately **₹{high_income["Average Credit"]:,.0f}**.
- **{low_income["Income Type"]}** has the lowest average credit at approximately **₹{low_income["Average Credit"]:,.0f}**.
- Credit amounts vary across income types, showing different borrowing patterns.
""")

# 5. Credit by Education
st.subheader("Credit by Education")
education_credit = (
    df.groupby("NAME_EDUCATION_TYPE")["AMT_CREDIT"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
education_credit.columns = ["Education", "Average Credit"]

fig = px.bar(
    education_credit,
    x="Education",
    y="Average Credit",
    title="Average Credit by Education"
)
fig.update_xaxes(tickangle=-25)
fig.update_yaxes(title="Average Credit", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_education")

high_education = education_credit.iloc[0]
low_education = education_credit.iloc[-1]

st.markdown(f"""
**Insights:**
- **{high_education["Education"]}** has the highest average credit at approximately **₹{high_education["Average Credit"]:,.0f}**.
- **{low_education["Education"]}** has the lowest average credit at approximately **₹{low_education["Average Credit"]:,.0f}**.
- Average borrowing levels vary across education categories.
""")

# 6. Credit by Contract Type
st.subheader("Credit by Contract Type")
contract_credit = df.groupby("NAME_CONTRACT_TYPE")[
    "AMT_CREDIT"].mean().reset_index()
contract_credit.columns = ["Contract Type", "Average Credit"]

fig = px.bar(
    contract_credit,
    x="Contract Type",
    y="Average Credit",
    title="Average Credit by Contract Type"
)
fig.update_yaxes(title="Average Credit", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_contract")

high_contract = contract_credit.loc[contract_credit["Average Credit"].idxmax()]
low_contract = contract_credit.loc[contract_credit["Average Credit"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_contract["Contract Type"]}** has the higher average credit at approximately **₹{high_contract["Average Credit"]:,.0f}**.
- **{low_contract["Contract Type"]}** has the lower average credit at approximately **₹{low_contract["Average Credit"]:,.0f}**.
- The average borrowing amount differs between contract types.
""")

# 7. Default Rate by Credit Range
st.subheader("Default Rate by Credit Range")
credit_default = (
    df.groupby("CREDIT_GROUP", observed=True)["TARGET"]
    .mean()
    .mul(100)
    .reindex(credit_labels)
    .reset_index()
)
credit_default.columns = ["Credit Range", "Default Rate"]

fig = px.line(
    credit_default,
    x="Credit Range",
    y="Default Rate",
    markers=True,
    title="Default Rate by Credit Range"
)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="credit_default_range")

high_credit_risk = credit_default.loc[credit_default["Default Rate"].idxmax()]
low_credit_risk = credit_default.loc[credit_default["Default Rate"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_credit_risk["Credit Range"]}** has the highest observed default rate at **{high_credit_risk["Default Rate"]:.2f}%**.
- **{low_credit_risk["Credit Range"]}** has the lowest observed default rate at **{low_credit_risk["Default Rate"]:.2f}%**.
- Default rates vary across credit ranges, indicating differences in observed risk by borrowing level.
""")
