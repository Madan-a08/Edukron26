import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Regional Risk Analysis")
st.write("Analysis of regional characteristics and their relationship with default risk.")

df = load_data()
df = create_features(df)
df = apply_filters(df)

# KPI Calculations
most_common_rating = df["REGION_RATING_CLIENT"].mode()[0]
rating_risk = df.groupby("REGION_RATING_CLIENT")["TARGET"].mean()
highest_risk_rating = rating_risk.idxmax()
average_population = df["REGION_POPULATION_RELATIVE"].mean()

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col1.metric("Most Common Region Rating", str(most_common_rating))
col2.metric("Highest Risk Region Rating", str(highest_risk_rating))
col3.metric("Average Regional Population", f"{average_population:.4f}")

# 1. Customers by Region Rating
st.subheader("Customers by Region Rating")

rating_count = (
    df["REGION_RATING_CLIENT"]
    .value_counts()
    .sort_index()
    .reset_index()
)
rating_count.columns = ["Region Rating", "Customers"]

fig = px.bar(
    rating_count,
    x="Region Rating",
    y="Customers",
    text="Customers",
    title="Customers by Region Rating",
    color="Customers",
    color_continuous_scale="Blues"
)
fig.update_traces(textposition="outside")
fig.update_xaxes(title="Region Rating")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="customers_region_rating")

top_rating = rating_count.loc[rating_count["Customers"].idxmax()]

st.markdown(
    f"""
**Insights:**
- Region rating **{top_rating['Region Rating']}** has the highest number of customers.
- The customer distribution varies across the available region ratings.
- The most common rating represents the largest applicant segment.
"""
)

# 2. Default Rate by Region Rating
st.subheader("Default Rate by Region Rating")

rating_default = (
    df.groupby("REGION_RATING_CLIENT")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)
rating_default.columns = ["Region Rating", "Default Rate"]

fig = px.bar(
    rating_default,
    x="Region Rating",
    y="Default Rate",
    text="Default Rate",
    title="Default Rate by Region Rating",
    color="Default Rate",
    color_continuous_scale="Reds"
)
fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)
fig.update_xaxes(title="Region Rating")
fig.update_yaxes(title="Default Rate (%)")
st.plotly_chart(fig, use_container_width=True, key="default_region_rating")

highest_risk = rating_default.loc[rating_default["Default Rate"].idxmax()]
lowest_risk = rating_default.loc[rating_default["Default Rate"].idxmin()]

st.markdown(
    f"""
**Insights:**
- Region rating **{highest_risk['Region Rating']}** has the highest default rate at **{highest_risk['Default Rate']:.2f}%**.
- Region rating **{lowest_risk['Region Rating']}** has the lowest default rate at **{lowest_risk['Default Rate']:.2f}%**.
- Default risk differs across regional ratings, indicating that region rating is associated with credit risk.
"""
)

# 3. Credit by Region Rating
st.subheader("Credit by Region Rating")

credit_rating = df[
    ["REGION_RATING_CLIENT", "AMT_CREDIT"]
].dropna()

credit_max = credit_rating["AMT_CREDIT"].quantile(0.99)
credit_rating = credit_rating[
    credit_rating["AMT_CREDIT"] <= credit_max
]

fig = px.box(
    credit_rating,
    x="REGION_RATING_CLIENT",
    y="AMT_CREDIT",
    title="Credit Distribution by Region Rating",
    color="REGION_RATING_CLIENT"
)
fig.update_xaxes(title="Region Rating")
fig.update_yaxes(title="Credit Amount", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_region_rating")

average_credit_rating = (
    credit_rating.groupby("REGION_RATING_CLIENT")["AMT_CREDIT"]
    .mean()
)

highest_credit_rating = average_credit_rating.idxmax()
highest_credit_value = average_credit_rating.max()

st.markdown(
    f"""
**Insights:**
- Region rating **{highest_credit_rating}** has the highest average credit amount at approximately **₹{highest_credit_value:,.0f}**.
- Credit amounts show variation across different regional ratings.
- The box plot also shows the spread and outliers in credit amounts within each rating.
"""
)

# 4. Income by Region Rating
st.subheader("Income by Region Rating")

income_rating = df[
    ["REGION_RATING_CLIENT", "AMT_INCOME_TOTAL"]
].dropna()

income_max = income_rating["AMT_INCOME_TOTAL"].quantile(0.99)
income_rating = income_rating[
    income_rating["AMT_INCOME_TOTAL"] <= income_max
]

fig = px.box(
    income_rating,
    x="REGION_RATING_CLIENT",
    y="AMT_INCOME_TOTAL",
    title="Income Distribution by Region Rating",
    color="REGION_RATING_CLIENT"
)
fig.update_xaxes(title="Region Rating")
fig.update_yaxes(title="Income", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="income_region_rating")

average_income_rating = (
    income_rating.groupby("REGION_RATING_CLIENT")["AMT_INCOME_TOTAL"]
    .mean()
)

highest_income_rating = average_income_rating.idxmax()
highest_income_value = average_income_rating.max()

st.markdown(
    f"""
**Insights:**
- Region rating **{highest_income_rating}** has the highest average income at approximately **₹{highest_income_value:,.0f}**.
- Income levels vary across regional ratings.
- The box plot highlights the distribution and variation of applicant income within each region rating.
"""
)

# 5. Region Mismatch vs Default
st.subheader("Region Mismatch vs Default")

region_mismatch = (
    df["REG_REGION_NOT_LIVE_REGION"]
    .map({
        0: "Same Region",
        1: "Different Region"
    })
    .value_counts()
    .reset_index()
)
region_mismatch.columns = ["Region Status", "Customers"]

fig = px.pie(
    region_mismatch,
    names="Region Status",
    values="Customers",
    hole=0.4,
    title="Customers by Region Mismatch",
    color="Region Status",
    color_discrete_map={
        "Same Region": "#636EFA",
        "Different Region": "#EF553B"
    }
)
fig.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Customers: %{value:,}<br>"
        "Percentage: %{percent}"
        "<extra></extra>"
    )
)
st.plotly_chart(fig, use_container_width=True, key="region_mismatch")

same_region = region_mismatch.loc[
    region_mismatch["Region Status"] == "Same Region",
    "Customers"
].iloc[0]

different_region = region_mismatch.loc[
    region_mismatch["Region Status"] == "Different Region",
    "Customers"
].iloc[0]

st.markdown(
    f"""
**Insights:**
- **{same_region:,} customers** are registered in the same region where they live.
- **{different_region:,} customers** have a different registration and living region.
- Most applicants belong to the same-region category, indicating limited regional mismatch.
"""
)

# 6. City Mismatch vs Default
st.subheader("City Mismatch vs Default")

city_mismatch = (
    df["REG_CITY_NOT_LIVE_CITY"]
    .map({
        0: "Same City",
        1: "Different City"
    })
    .value_counts()
    .reset_index()
)
city_mismatch.columns = ["City Status", "Customers"]

fig = px.pie(
    city_mismatch,
    names="City Status",
    values="Customers",
    hole=0.4,
    title="Customers by City Mismatch",
    color="City Status",
    color_discrete_map={
        "Same City": "#00CC96",
        "Different City": "#FFA15A"
    }
)
fig.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Customers: %{value:,}<br>"
        "Percentage: %{percent}"
        "<extra></extra>"
    )
)
st.plotly_chart(fig, use_container_width=True, key="city_mismatch")

same_city = city_mismatch.loc[
    city_mismatch["City Status"] == "Same City",
    "Customers"
].iloc[0]

different_city = city_mismatch.loc[
    city_mismatch["City Status"] == "Different City",
    "Customers"
].iloc[0]

st.markdown(
    f"""
**Insights:**
- **{same_city:,} customers** live in the same city as their registered address.
- **{different_city:,} customers** have a different registered and living city.
- Same-city applicants form the larger segment of the customer population.
"""
)
