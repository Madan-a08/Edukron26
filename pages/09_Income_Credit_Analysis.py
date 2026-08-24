import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Income vs Credit Analysis")
st.write("Analysis of credit taken by customers relative to their income.")

df = apply_filters(create_features(load_data()))

# Credit-to-Income Ratio
df["CREDIT_INCOME_RATIO"] = (
    df["AMT_CREDIT"] /
    df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
)

df = df[df["CREDIT_INCOME_RATIO"].notna()]

# Risk Groups
risk_labels = ["Low", "Moderate", "High", "Very High"]

df["RISK_GROUP"] = pd.cut(
    df["CREDIT_INCOME_RATIO"],
    bins=[0, 2, 4, 6, float("inf")],
    labels=risk_labels,
    include_lowest=True
)

# KPIs
average_ratio = df["CREDIT_INCOME_RATIO"].mean()
highest_ratio = df["CREDIT_INCOME_RATIO"].max()

high_ratio_default_rate = (
    df.loc[df["CREDIT_INCOME_RATIO"] > 6, "TARGET"].mean() * 100
)

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Credit-to-Income Ratio",
    f"{average_ratio:.2f}"
)

col2.metric(
    "Highest Credit-to-Income Ratio",
    f"{highest_ratio:.2f}"
)

col3.metric(
    "Default Rate for High Ratio Customers",
    f"{high_ratio_default_rate:.2f}%"
)

# 1. Income vs Credit
st.subheader("Income vs Credit")

income_credit = df[
    ["AMT_INCOME_TOTAL", "AMT_CREDIT"]
].dropna()

income_max = income_credit["AMT_INCOME_TOTAL"].quantile(0.99)
credit_max = income_credit["AMT_CREDIT"].quantile(0.99)

income_credit = income_credit[
    (income_credit["AMT_INCOME_TOTAL"] <= income_max) &
    (income_credit["AMT_CREDIT"] <= credit_max)
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
    range=[0, income_max],
    tickformat=","
)

fig.update_yaxes(
    title="Credit Amount",
    range=[0, credit_max],
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="income_credit_ratio_scatter"
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

# 2. Credit/Income Ratio Distribution
st.subheader("Credit/Income Ratio Distribution")

ratio_data = df[["CREDIT_INCOME_RATIO"]].dropna()

ratio_max = ratio_data[
    "CREDIT_INCOME_RATIO"
].quantile(0.99)

ratio_graph = ratio_data[
    ratio_data["CREDIT_INCOME_RATIO"] <= ratio_max
]

fig = px.histogram(
    ratio_graph,
    x="CREDIT_INCOME_RATIO",
    nbins=30,
    title="Credit/Income Ratio Distribution"
)

fig.update_xaxes(
    title="Credit-to-Income Ratio",
    range=[0, ratio_max]
)

fig.update_yaxes(
    title="Number of Customers"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="credit_income_ratio_distribution"
)

st.markdown(f"""
**Insights:**
- The average credit-to-income ratio is **{average_ratio:.2f}**.
- Most customers are concentrated in the lower ratio range.
- Extremely high ratios are limited, with the graph displaying values up to the 99th percentile.
""")

# 3. Default Rate vs Credit/Income Ratio
st.subheader("Default Rate vs Credit/Income Ratio")

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
    title="Default Rate by Credit/Income Risk Group"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="credit_income_risk_default"
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
- Customers with higher credit relative to income represent a higher borrowing-risk segment.
""")

# 4. Gender-wise Credit/Income Ratio
st.subheader("Gender-wise Credit/Income Ratio")

gender_ratio = (
    df.groupby("CODE_GENDER")["CREDIT_INCOME_RATIO"]
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
    title="Average Credit/Income Ratio by Gender"
)

fig.update_yaxes(
    title="Average Credit/Income Ratio"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="credit_income_gender"
)

high_gender = gender_ratio.loc[
    gender_ratio["Average Ratio"].idxmax()
]

low_gender = gender_ratio.loc[
    gender_ratio["Average Ratio"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{high_gender["Gender"]}** has the higher average credit-to-income ratio at **{high_gender["Average Ratio"]:.2f}**.
- **{low_gender["Gender"]}** has the lower average ratio at **{low_gender["Average Ratio"]:.2f}**.
- The comparison shows differences in borrowing relative to income between genders.
""")

# 5. Education-wise Credit/Income Ratio
st.subheader("Education-wise Credit/Income Ratio")

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

fig = px.bar(
    education_ratio,
    x="Education",
    y="Average Ratio",
    title="Average Credit/Income Ratio by Education"
)

fig.update_xaxes(
    tickangle=-30
)

fig.update_yaxes(
    title="Average Credit/Income Ratio"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="credit_income_education"
)

high_education = education_ratio.iloc[0]
low_education = education_ratio.iloc[-1]

st.markdown(f"""
**Insights:**
- **{high_education["Education"]}** has the highest average ratio at **{high_education["Average Ratio"]:.2f}**.
- **{low_education["Education"]}** has the lowest average ratio at **{low_education["Average Ratio"]:.2f}**.
- Credit exposure relative to income differs across education groups.
""")
