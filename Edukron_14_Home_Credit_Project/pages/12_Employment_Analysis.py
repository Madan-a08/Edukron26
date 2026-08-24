import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Employment Analysis")
st.write("Analysis of employment status and work history in relation to credit risk.")

df = apply_filters(create_features(load_data()))

# Clean DAYS_EMPLOYED
df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, pd.NA)
df["EMPLOYMENT_YEARS"] = df["DAYS_EMPLOYED"].abs() / 365

# KPIs
average_employment_years = df["EMPLOYMENT_YEARS"].mean()

most_common_occupation = (
    df["OCCUPATION_TYPE"].dropna().mode()[0]
)

most_common_income_type = df["NAME_INCOME_TYPE"].mode()[0]

occupation_risk = (
    df.groupby("OCCUPATION_TYPE")["TARGET"]
    .mean()
)

highest_risk_occupation = occupation_risk.idxmax()

st.subheader("Key Performance Indicators")

col1, col2 = st.columns(2)

col1.metric(
    "Average Employment Years",
    f"{average_employment_years:.1f} years"
)

col2.metric(
    "Most Common Occupation",
    most_common_occupation
)

col1, col2 = st.columns(2)

col1.metric(
    "Most Common Income Type",
    most_common_income_type
)

col2.metric(
    "Highest Risk Occupation",
    highest_risk_occupation
)

# 1. Employment Years Distribution
st.subheader("Employment Years Distribution")

employment_data = df[["EMPLOYMENT_YEARS"]].dropna()

employment_max = employment_data[
    "EMPLOYMENT_YEARS"
].quantile(0.99)

employment_graph = employment_data[
    employment_data["EMPLOYMENT_YEARS"] <= employment_max
]

fig = px.histogram(
    employment_graph,
    x="EMPLOYMENT_YEARS",
    nbins=30,
    title="Employment Years Distribution"
)

fig.update_xaxes(
    title="Employment Years"
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="employment_distribution"
)

median_employment = df["EMPLOYMENT_YEARS"].median()

st.markdown(f"""
**Insights:**
- The average employment experience is **{average_employment_years:.1f} years**.
- The median employment experience is **{median_employment:.1f} years**.
- The distribution is concentrated toward lower employment durations, with extreme values limited using the 99th percentile.
""")

# 2. Default Rate by Employment Years
st.subheader("Default Rate by Employment Years")

df["EMPLOYMENT_GROUP"] = df["EMPLOYMENT_YEARS"].round()

employment_default = (
    df.dropna(subset=["EMPLOYMENT_GROUP"])
    .groupby("EMPLOYMENT_GROUP")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

employment_default.columns = [
    "Employment Years",
    "Default Rate"
]

fig = px.line(
    employment_default,
    x="Employment Years",
    y="Default Rate",
    markers=True,
    title="Default Rate by Employment Years"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="employment_default_rate"
)

highest_employment_risk = employment_default.loc[
    employment_default["Default Rate"].idxmax()
]

lowest_employment_risk = employment_default.loc[
    employment_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- The highest observed default rate occurs around **{highest_employment_risk["Employment Years"]:.0f} years** of employment at **{highest_employment_risk["Default Rate"]:.2f}%**.
- The lowest observed default rate occurs around **{lowest_employment_risk["Employment Years"]:.0f} years** at **{lowest_employment_risk["Default Rate"]:.2f}%**.
- Default risk does not necessarily change consistently with every additional year of employment.
""")

# 3. Applications by Income Type
st.subheader("Applications by Income Type")

income_type = (
    df["NAME_INCOME_TYPE"]
    .value_counts()
    .reset_index()
)

income_type.columns = [
    "Income Type",
    "Applications"
]

income_type["Percentage"] = (
    income_type["Applications"] /
    len(df) * 100
)

fig = px.bar(
    income_type,
    x="Income Type",
    y="Applications",
    title="Applications by Income Type"
)

fig.update_xaxes(
    title="Income Type",
    tickangle=-30
)

fig.update_yaxes(
    title="Number of Applications"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="applications_income_type"
)

highest_income_type = income_type.iloc[0]

st.markdown(f"""
**Insights:**
- **{highest_income_type["Income Type"]}** has the highest number of applications.
- It represents approximately **{highest_income_type["Percentage"]:.2f}%** of the filtered customers.
- The distribution shows that applications are concentrated in specific income categories.
""")

# 4. Default Rate by Income Type
st.subheader("Default Rate by Income Type")

income_default = (
    df.groupby("NAME_INCOME_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)

income_default.columns = [
    "Income Type",
    "Default Rate"
]

fig = px.line(
    income_default,
    x="Income Type",
    y="Default Rate",
    markers=True,
    title="Default Rate by Income Type"
)

fig.update_xaxes(
    title="Income Type",
    tickangle=-30
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_income_type"
)

highest_income_risk = income_default.iloc[0]
lowest_income_risk = income_default.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_income_risk["Income Type"]}** has the highest default rate at **{highest_income_risk["Default Rate"]:.2f}%**.
- **{lowest_income_risk["Income Type"]}** has the lowest default rate at **{lowest_income_risk["Default Rate"]:.2f}%**.
- Default risk varies considerably across different income sources.
""")

# 5. Applications by Occupation
st.subheader("Applications by Occupation")

occupation = (
    df["OCCUPATION_TYPE"]
    .dropna()
    .value_counts()
    .reset_index()
)

occupation.columns = [
    "Occupation",
    "Applications"
]

fig = px.bar(
    occupation,
    x="Occupation",
    y="Applications",
    title="Applications by Occupation"
)

fig.update_xaxes(
    title="Occupation",
    tickangle=-35
)

fig.update_yaxes(
    title="Number of Applications"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="applications_occupation"
)

highest_occupation = occupation.iloc[0]
lowest_occupation = occupation.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_occupation["Occupation"]}** has the highest number of applications.
- **{lowest_occupation["Occupation"]}** has the lowest number of applications among the recorded occupations.
- Application volume varies substantially across occupation categories.
""")

# 6. Default Rate by Occupation
st.subheader("Default Rate by Occupation")

occupation_default = (
    df.groupby("OCCUPATION_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)

occupation_default.columns = [
    "Occupation",
    "Default Rate"
]

fig = px.bar(
    occupation_default,
    x="Occupation",
    y="Default Rate",
    title="Default Rate by Occupation"
)

fig.update_xaxes(
    title="Occupation",
    tickangle=-35
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_occupation"
)

highest_occupation_risk = occupation_default.iloc[0]
lowest_occupation_risk = occupation_default.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_occupation_risk["Occupation"]}** has the highest default rate at **{highest_occupation_risk["Default Rate"]:.2f}%**.
- **{lowest_occupation_risk["Occupation"]}** has the lowest default rate at **{lowest_occupation_risk["Default Rate"]:.2f}%**.
- Occupation appears to be an important segment for comparing customer credit risk.
""")

# 7. Default Rate by Organization Type
st.subheader("Default Rate by Organization Type")

organization_default = (
    df.groupby("ORGANIZATION_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)

organization_default.columns = [
    "Organization Type",
    "Default Rate"
]

fig = px.bar(
    organization_default,
    x="Organization Type",
    y="Default Rate",
    title="Default Rate by Organization Type"
)

fig.update_xaxes(
    title="Organization Type",
    tickangle=-45
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_organization"
)

highest_org_risk = organization_default.iloc[0]
lowest_org_risk = organization_default.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_org_risk["Organization Type"]}** has the highest default rate at **{highest_org_risk["Default Rate"]:.2f}%**.
- **{lowest_org_risk["Organization Type"]}** has the lowest default rate at **{lowest_org_risk["Default Rate"]:.2f}%**.
- Organization type can help identify segments with comparatively higher or lower default risk.
""")
