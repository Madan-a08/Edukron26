import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features

st.title("Age Analysis")
st.write("Analysis of the relationship between age and credit risk.")

df = create_features(load_data())

# Filters
st.sidebar.header("Age Analysis Filters")

gender = st.sidebar.multiselect(
    "Gender", df["CODE_GENDER"].dropna().unique(), key="age_gender")
age_min, age_max = int(df["AGE"].min()), int(df["AGE"].max())
age_range = st.sidebar.slider(
    "Age", age_min, age_max, (age_min, age_max), key="age_range")
family_status = st.sidebar.multiselect(
    "Family Status", df["NAME_FAMILY_STATUS"].dropna().unique(), key="age_family")
education = st.sidebar.multiselect(
    "Education", df["NAME_EDUCATION_TYPE"].dropna().unique(), key="age_education")
housing = st.sidebar.multiselect(
    "Housing Type", df["NAME_HOUSING_TYPE"].dropna().unique(), key="age_housing")

if gender:
    df = df[df["CODE_GENDER"].isin(gender)]
if family_status:
    df = df[df["NAME_FAMILY_STATUS"].isin(family_status)]
if education:
    df = df[df["NAME_EDUCATION_TYPE"].isin(education)]
if housing:
    df = df[df["NAME_HOUSING_TYPE"].isin(housing)]
df = df[df["AGE"].between(*age_range)]

# Age Groups
age_labels = ["18–25", "26–30", "31–35", "36–40",
              "41–45", "46–50", "51–55", "56–60", "61+"]
df["AGE_GROUP"] = pd.cut(
    df["AGE"],
    bins=[18, 25, 30, 35, 40, 45, 50, 55, 60, 100],
    labels=age_labels,
    include_lowest=True
)

# KPIs
average_age = df["AGE"].mean()
youngest_customer = df["AGE"].min()
oldest_customer = df["AGE"].max()
age_risk = df.groupby("AGE_GROUP", observed=True)["TARGET"].mean().mul(100)
highest_risk_age_group = age_risk.idxmax()

st.subheader("Key Performance Indicators")
cols = st.columns(4)
cols[0].metric("Average Age", f"{average_age:.1f} years")
cols[1].metric("Youngest Customer", f"{youngest_customer:.1f} years")
cols[2].metric("Oldest Customer", f"{oldest_customer:.1f} years")
cols[3].metric("Highest Risk Age Group", highest_risk_age_group)

# 1. Age Distribution
st.subheader("Age Distribution")
fig = px.histogram(df, x="AGE", nbins=30, title="Age Distribution")
fig.update_xaxes(title="Age")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="age_distribution")

age_median = df["AGE"].median()
st.markdown(f"""
**Insights:**
- The average customer age is **{average_age:.1f} years**, while the median age is **{age_median:.1f} years**.
- Customers range from **{youngest_customer:.1f} to {oldest_customer:.1f} years**.
- The distribution shows where the majority of applicants are concentrated by age.
""")

# 2. Applications by Age Group
st.subheader("Applications by Age Group")
age_data = df["AGE_GROUP"].value_counts().reindex(age_labels).reset_index()
age_data.columns = ["Age Group", "Applications"]

fig = px.bar(age_data, x="Age Group", y="Applications",
             title="Applications by Age Group")
fig.update_yaxes(title="Number of Applications")
st.plotly_chart(fig, use_container_width=True, key="applications_age_group")

top_age = age_data.loc[age_data["Applications"].idxmax()]
st.markdown(f"""
**Insights:**
- The **{top_age["Age Group"]}** age group has the highest number of applications with **{top_age["Applications"]:,}** customers.
- Applicant volume varies across age groups, showing where the customer population is concentrated.
- The age-group distribution reflects the currently selected filters.
""")

# 3. Default Rate by Age
st.subheader("Default Rate by Age")
age_default = df.groupby("AGE")["TARGET"].mean().mul(100).reset_index()
age_default.columns = ["Age", "Default Rate"]

fig = px.line(age_default, x="Age", y="Default Rate",
              title="Default Rate by Age")
fig.update_xaxes(title="Age")
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_rate_age")

highest_age_default = age_default.loc[age_default["Default Rate"].idxmax()]
lowest_age_default = age_default.loc[age_default["Default Rate"].idxmin()]
st.markdown(f"""
**Insights:**
- The highest observed default rate occurs at age **{highest_age_default["Age"]:.0f}**, at **{highest_age_default["Default Rate"]:.2f}%**.
- The lowest observed default rate occurs at age **{lowest_age_default["Age"]:.0f}**, at **{lowest_age_default["Default Rate"]:.2f}%**.
- Default rates fluctuate across individual ages, so isolated ages should be interpreted cautiously.
""")

# 4. Default Rate by Age Group
st.subheader("Default Rate by Age Group")
age_group_default = (
    df.groupby("AGE_GROUP", observed=True)["TARGET"]
    .mean()
    .mul(100)
    .reindex(age_labels)
    .reset_index()
)
age_group_default.columns = ["Age Group", "Default Rate"]

fig = px.bar(age_group_default, x="Age Group", y="Default Rate",
             title="Default Rate by Age Group")
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_rate_age_group")

group_high = age_group_default.loc[age_group_default["Default Rate"].idxmax()]
group_low = age_group_default.loc[age_group_default["Default Rate"].idxmin()]
st.markdown(f"""
**Insights:**
- **{group_high["Age Group"]}** has the highest observed default rate at **{group_high["Default Rate"]:.2f}%**.
- **{group_low["Age Group"]}** has the lowest observed default rate at **{group_low["Default Rate"]:.2f}%**.
- The variation between age groups indicates differences in observed credit risk across age segments.
""")

# 5. Credit Amount by Age
st.subheader("Credit Amount by Age")
credit_age = df[["AGE", "AMT_CREDIT"]].dropna()

fig = px.scatter(
    credit_age,
    x="AGE",
    y="AMT_CREDIT",
    title="Credit Amount by Age",
    opacity=0.35
)
fig.update_xaxes(title="Age")
fig.update_yaxes(title="Credit Amount", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="credit_age")

credit_corr = credit_age["AGE"].corr(credit_age["AMT_CREDIT"])
st.markdown(f"""
**Insights:**
- The correlation between age and credit amount is **{credit_corr:.2f}**.
- Credit amounts vary considerably across customers within the same age range.
- The scatter plot shows whether credit amounts appear to increase or decrease systematically with age.
""")

# 6. Average Income by Age
st.subheader("Average Income by Age")
income_age = df.groupby("AGE")["AMT_INCOME_TOTAL"].mean().reset_index()
income_age.columns = ["Age", "Average Income"]

fig = px.line(income_age, x="Age", y="Average Income",
              title="Average Income by Age")
fig.update_xaxes(title="Age")
fig.update_yaxes(title="Average Income", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="income_age")

highest_income_age = income_age.loc[income_age["Average Income"].idxmax()]
lowest_income_age = income_age.loc[income_age["Average Income"].idxmin()]
st.markdown(f"""
**Insights:**
- The highest average income is observed at age **{highest_income_age["Age"]:.0f}**, at approximately **₹{highest_income_age["Average Income"]:,.0f}**.
- The lowest average income is observed at age **{lowest_income_age["Age"]:.0f}**, at approximately **₹{lowest_income_age["Average Income"]:,.0f}**.
- Average income varies across ages, indicating differences in earning levels within the applicant population.
""")
