import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters


st.title("Home Credit Default Risk Dashboard")

st.write(
    "Interactive analysis of customer demographics, income, "
    "credit characteristics and repayment risk."
)


# Load data

df = load_data()
df = create_features(df)
df = apply_filters(df)


# KPI calculations

total_customers = len(df)

total_features = len(df.columns)

average_age = df["AGE"].mean()

average_employment_years = (
    df["EMPLOYMENT_YEARS"].mean()
)

average_external_score = (
    df["AVERAGE_EXTERNAL_SCORE"].mean()
)

average_credit_income_ratio = (
    df["CREDIT_INCOME_RATIO"].mean()
)

average_annuity_income_ratio = (
    df["ANNUITY_INCOME_RATIO"].mean()
)

default_rate = (
    df["TARGET"].mean() * 100
)


# Customer and dataset overview

st.subheader("Customer and Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "Total Features",
    f"{total_features:,}"
)

col3.metric(
    "Average Age",
    f"{average_age:.1f} years"
)

col4.metric(
    "Average Employment",
    f"{average_employment_years:.1f} years"
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average External Score",
    f"{average_external_score:.2f}"
)

col2.metric(
    "Avg Credit / Income",
    f"{average_credit_income_ratio:.2f}"
)

col3.metric(
    "Avg Annuity / Income",
    f"{average_annuity_income_ratio:.2%}"
)

col4.metric(
    "Overall Default Rate",
    f"{default_rate:.2f}%"
)


# Customer profile

st.subheader("Customer Profile")

gender_data = (
    df["CODE_GENDER"]
    .value_counts()
    .reset_index()
)

gender_data.columns = [
    "Gender",
    "Customers"
]

gender_data["Gender"] = (
    gender_data["Gender"]
    .map({
        "M": "Male",
        "F": "Female"
    })
)


fig = px.pie(
    gender_data,
    names="Gender",
    values="Customers",
    hole=0.4,
    title="Customer Distribution by Gender",
    color="Gender",
    color_discrete_map={
        "Male": "#3498DB",
        "Female": "#E91E63"
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

st.plotly_chart(
    fig,
    use_container_width=True
)


gender_top = gender_data.iloc[0]

gender_second = gender_data.iloc[1]

st.markdown(
    f"""
**Insights:**
- The largest customer group is **{gender_top['Gender']}**.
- **{gender_second['Gender']}** represents the second-largest customer group.
- The customer distribution is mainly concentrated across these two gender groups.
"""
)


# Education distribution

st.subheader("Education Distribution")

education_data = (
    df["NAME_EDUCATION_TYPE"]
    .value_counts()
    .reset_index()
)

education_data.columns = [
    "Education",
    "Customers"
]


fig = px.bar(
    education_data,
    x="Education",
    y="Customers",
    title="Customers by Education",
    text="Customers",
    color="Education",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_traces(
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Customers: %{y:,}"
        "<extra></extra>"
    )
)

fig.update_xaxes(
    title="Education",
    tickangle=-30
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


education_top = education_data.iloc[0]

education_second = education_data.iloc[1]

st.markdown(
    f"""
**Insights:**
- The largest education category is **{education_top['Education']}**.
- **{education_second['Education']}** is the second-most common education category.
- Customer applications are concentrated in a few major education categories.
"""
)


# Income type distribution

st.subheader("Income Type Distribution")

income_data = (
    df["NAME_INCOME_TYPE"]
    .value_counts()
    .reset_index()
)

income_data.columns = [
    "Income Type",
    "Customers"
]


fig = px.bar(
    income_data,
    x="Income Type",
    y="Customers",
    title="Customers by Income Type",
    text="Customers",
    color="Income Type",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig.update_traces(
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Customers: %{y:,}"
        "<extra></extra>"
    )
)

fig.update_xaxes(
    title="Income Type",
    tickangle=-30
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


income_top = income_data.iloc[0]

income_second = income_data.iloc[1]

st.markdown(
    f"""
**Insights:**
- The largest income category is **{income_top['Income Type']}**.
- **{income_second['Income Type']}** is the second-most common income type.
- The customer base is concentrated in a small number of income types.
"""
)


# Overall customer summary

st.subheader("Overall Customer Summary")

most_common_gender = (
    df["CODE_GENDER"]
    .mode()[0]
)

most_common_gender = {
    "M": "Male",
    "F": "Female"
}.get(
    most_common_gender,
    most_common_gender
)


most_common_education = (
    df["NAME_EDUCATION_TYPE"]
    .mode()[0]
)

most_common_income = (
    df["NAME_INCOME_TYPE"]
    .mode()[0]
)


summary = pd.DataFrame({

    "Metric": [

        "Total Customers",
        "Average Age",
        "Average Employment Years",
        "Average External Score",
        "Average Credit-to-Income Ratio",
        "Average Annuity-to-Income Ratio",
        "Overall Default Rate",
        "Most Common Gender",
        "Most Common Education",
        "Most Common Income Type"

    ],

    "Value": [

        f"{total_customers:,}",
        f"{average_age:.1f} years",
        f"{average_employment_years:.1f} years",
        f"{average_external_score:.2f}",
        f"{average_credit_income_ratio:.2f}",
        f"{average_annuity_income_ratio:.2%}",
        f"{default_rate:.2f}%",
        most_common_gender,
        most_common_education,
        most_common_income

    ]

})


st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# dashboard

st.subheader("Dashboard Pages")

pages = pd.DataFrame({

    "Page": [

        "01 - Executive Overview",
        "02 - Target / Default Analysis",
        "03 - Demographic Analysis",
        "04 - Age Analysis",
        "05 - Gender Analysis",
        "06 - Income Analysis",
        "07 - Credit Amount Analysis",
        "08 - Annuity Analysis",
        "09 - Income vs Credit Analysis",
        "10 - Annuity Burden Analysis",
        "11 - Education Analysis",
        "12 - Employment Analysis",
        "13 - Family & Children Analysis",
        "14 - Housing & Asset Analysis",
        "15 - Contract Type Analysis",
        "16 - External Credit Score Analysis",
        "17 - Regional Risk Analysis",
        "18 - Missing Value Analysis",
        "19 - Correlation & Risk Factor Analysis",
        "20 - Customer Risk Explorer"

    ],

    "Focus": [

        "Overall loan applicants and credit risk",
        "Customer default risk",
        "Customer demographic characteristics",
        "Age and credit risk",
        "Credit characteristics by gender",
        "Customer income and credit risk",
        "Credit amount analysis",
        "Loan payment obligations",
        "Credit relative to income",
        "Repayment burden relative to income",
        "Education and credit risk",
        "Employment and work history",
        "Family size, children and credit risk",
        "Housing and asset ownership",
        "Loan contract characteristics",
        "External credit scores and default risk",
        "Regional characteristics and risk",
        "Data quality and missing values",
        "Correlation and important risk factors",
        "Individual customer risk exploration"

    ]

})


st.dataframe(
    pages,
    use_container_width=True,
    hide_index=True
)
