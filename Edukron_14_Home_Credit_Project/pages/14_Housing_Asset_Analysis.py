import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Housing & Asset Analysis")
st.write("Analysis of property and vehicle ownership and their relationship with credit risk.")

df = apply_filters(create_features(load_data()))

# KPIs
car_owners = (df["FLAG_OWN_CAR"] == "Y").sum()
property_owners = (df["FLAG_OWN_REALTY"] == "Y").sum()
both_owners = (
    (df["FLAG_OWN_CAR"] == "Y") &
    (df["FLAG_OWN_REALTY"] == "Y")
).sum()
property_default_rate = (
    df.loc[df["FLAG_OWN_REALTY"] == "Y", "TARGET"].mean() * 100
)

st.subheader("Key Performance Indicators")

col1, col2 = st.columns(2)
col1.metric("Car Owners", f"{car_owners:,}")
col2.metric("Property Owners", f"{property_owners:,}")

col1, col2 = st.columns(2)
col1.metric("Customers Owning Both", f"{both_owners:,}")
col2.metric("Default Rate of Property Owners", f"{property_default_rate:.2f}%")

# 1. Car Ownership Distribution
st.subheader("Car Ownership Distribution")

car_data = (
    df["FLAG_OWN_CAR"]
    .map({"Y": "Owns Car", "N": "Does Not Own Car"})
    .value_counts()
    .reset_index()
)
car_data.columns = ["Car Ownership", "Customers"]

fig = px.pie(
    car_data,
    names="Car Ownership",
    values="Customers",
    hole=0.4,
    title="Car Ownership Distribution"
)
fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True,
                key="car_ownership_distribution")

car_majority = car_data.iloc[0]
car_percentage = car_majority["Customers"] / len(df) * 100

st.markdown(f"""
**Insights:**
- **{car_majority["Car Ownership"]}** represents the majority of applicants.
- This group contains **{car_percentage:.2f}%** of customers.
- Total car owners: **{car_owners:,}**.
""")

# 2. Property Ownership Distribution
st.subheader("Property Ownership Distribution")

property_data = (
    df["FLAG_OWN_REALTY"]
    .map({"Y": "Owns Property", "N": "Does Not Own Property"})
    .value_counts()
    .reset_index()
)
property_data.columns = ["Property Ownership", "Customers"]

fig = px.pie(
    property_data,
    names="Property Ownership",
    values="Customers",
    hole=0.4,
    title="Property Ownership Distribution"
)
fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True,
                key="property_ownership_distribution")

property_majority = property_data.iloc[0]
property_percentage = property_majority["Customers"] / len(df) * 100

st.markdown(f"""
**Insights:**
- **{property_majority["Property Ownership"]}** represents the majority of applicants.
- This group accounts for **{property_percentage:.2f}%** of customers.
- Total property owners: **{property_owners:,}**.
""")

# 3. Default Rate by Car Ownership
st.subheader("Default Rate by Car Ownership")

car_default = (
    df.groupby("FLAG_OWN_CAR")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)
car_default["FLAG_OWN_CAR"] = car_default["FLAG_OWN_CAR"].map({
    "Y": "Owns Car",
    "N": "Does Not Own Car"
})
car_default.columns = ["Car Ownership", "Default Rate"]

fig = px.bar(
    car_default,
    x="Car Ownership",
    y="Default Rate",
    title="Default Rate by Car Ownership"
)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_car_ownership")

highest_car_risk = car_default.loc[
    car_default["Default Rate"].idxmax()
]
lowest_car_risk = car_default.loc[
    car_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{highest_car_risk["Car Ownership"]}** has the higher default rate at **{highest_car_risk["Default Rate"]:.2f}%**.
- **{lowest_car_risk["Car Ownership"]}** has the lower default rate at **{lowest_car_risk["Default Rate"]:.2f}%**.
- Car ownership shows a difference in observed default risk between the two groups.
""")

# 4. Default Rate by Property Ownership
st.subheader("Default Rate by Property Ownership")

property_default = (
    df.groupby("FLAG_OWN_REALTY")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)
property_default["FLAG_OWN_REALTY"] = property_default["FLAG_OWN_REALTY"].map({
    "Y": "Owns Property",
    "N": "Does Not Own Property"
})
property_default.columns = ["Property Ownership", "Default Rate"]

fig = px.bar(
    property_default,
    x="Property Ownership",
    y="Default Rate",
    title="Default Rate by Property Ownership"
)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True,
                key="default_property_ownership")

highest_property_risk = property_default.loc[
    property_default["Default Rate"].idxmax()
]
lowest_property_risk = property_default.loc[
    property_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{highest_property_risk["Property Ownership"]}** has the higher default rate at **{highest_property_risk["Default Rate"]:.2f}%**.
- **{lowest_property_risk["Property Ownership"]}** has the lower default rate at **{lowest_property_risk["Default Rate"]:.2f}%**.
- Property ownership can help distinguish customer groups with different observed default rates.
""")

# 5. Applicants by Housing Type
st.subheader("Applicants by Housing Type")

housing_data = (
    df["NAME_HOUSING_TYPE"]
    .value_counts()
    .reset_index()
)
housing_data.columns = ["Housing Type", "Applicants"]

fig = px.bar(
    housing_data,
    x="Housing Type",
    y="Applicants",
    title="Applicants by Housing Type"
)
fig.update_xaxes(title="Housing Type", tickangle=-30)
fig.update_yaxes(title="Number of Applicants")
st.plotly_chart(fig, use_container_width=True, key="applicants_housing_type")

most_common_housing = housing_data.iloc[0]
housing_percentage = most_common_housing["Applicants"] / len(df) * 100

st.markdown(f"""
**Insights:**
- **{most_common_housing["Housing Type"]}** has the highest number of applicants.
- It represents approximately **{housing_percentage:.2f}%** of the filtered customers.
- Applicant distribution varies considerably across housing categories.
""")

# 6. Default Rate by Housing Type
st.subheader("Default Rate by Housing Type")

housing_default = (
    df.groupby("NAME_HOUSING_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)
housing_default.columns = ["Housing Type", "Default Rate"]

fig = px.bar(
    housing_default,
    x="Housing Type",
    y="Default Rate",
    title="Default Rate by Housing Type"
)
fig.update_xaxes(title="Housing Type", tickangle=-30)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_housing_type")

highest_housing_risk = housing_default.iloc[0]
lowest_housing_risk = housing_default.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_housing_risk["Housing Type"]}** has the highest default rate at **{highest_housing_risk["Default Rate"]:.2f}%**.
- **{lowest_housing_risk["Housing Type"]}** has the lowest default rate at **{lowest_housing_risk["Default Rate"]:.2f}%**.
- Housing type shows noticeable differences in observed credit risk.
""")

# 7. Average Credit by Housing Type
st.subheader("Average Credit by Housing Type")

credit_max = df["AMT_CREDIT"].quantile(0.99)
credit_data = df[df["AMT_CREDIT"] <= credit_max]

fig = px.box(
    credit_data,
    x="NAME_HOUSING_TYPE",
    y="AMT_CREDIT",
    title="Credit Distribution by Housing Type"
)
fig.update_xaxes(title="Housing Type", tickangle=-30)
fig.update_yaxes(title="Credit Amount", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_housing_type")

housing_credit = (
    df.groupby("NAME_HOUSING_TYPE")["AMT_CREDIT"]
    .mean()
    .sort_values(ascending=False)
)

highest_credit_housing = housing_credit.index[0]
lowest_credit_housing = housing_credit.index[-1]

st.markdown(f"""
**Insights:**
- **{highest_credit_housing}** has the highest average credit amount.
- **{lowest_credit_housing}** has the lowest average credit amount.
- Credit amounts vary across housing types, with the box plot also showing differences in distribution.
""")
