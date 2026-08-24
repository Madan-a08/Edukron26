import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Contract Type Analysis")
st.write("Analysis of credit applications according to loan contract type.")

df = apply_filters(create_features(load_data()))

# Credit-to-Income Ratio
df["CREDIT_INCOME_RATIO"] = (
    df["AMT_CREDIT"] /
    df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
)

# KPIs
cash_applications = (df["NAME_CONTRACT_TYPE"] == "Cash loans").sum()
revolving_applications = (df["NAME_CONTRACT_TYPE"] == "Revolving loans").sum()

cash_default_rate = (
    df.loc[df["NAME_CONTRACT_TYPE"] == "Cash loans", "TARGET"].mean() * 100
)

revolving_default_rate = (
    df.loc[df["NAME_CONTRACT_TYPE"] == "Revolving loans", "TARGET"].mean() *
    100
)

st.subheader("Key Performance Indicators")

col1, col2 = st.columns(2)
col1.metric("Cash Loan Applications", f"{cash_applications:,}")
col2.metric("Revolving Loan Applications", f"{revolving_applications:,}")

col1, col2 = st.columns(2)
col1.metric("Cash Loan Default Rate", f"{cash_default_rate:.2f}%")
col2.metric("Revolving Loan Default Rate", f"{revolving_default_rate:.2f}%")

# 1. Applications by Contract Type
st.subheader("Applications by Contract Type")

contract_count = (
    df["NAME_CONTRACT_TYPE"]
    .value_counts()
    .reset_index()
)
contract_count.columns = ["Contract Type", "Applications"]
contract_count["Percentage"] = (
    contract_count["Applications"] / len(df) * 100
)

fig = px.pie(
    contract_count,
    names="Contract Type",
    values="Applications",
    hole=0.4,
    title="Applications by Contract Type"
)

fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Applications: %{value:,}<br>Percentage: %{percent}<extra></extra>"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="applications_contract_type"
)

most_common_contract = contract_count.iloc[0]
contract_percentage = most_common_contract["Applications"] / len(df) * 100

st.markdown(f"""
**Insights:**
- **{most_common_contract["Contract Type"]}** has the highest number of applications.
- It represents approximately **{contract_percentage:.2f}%** of all filtered applications.
- Revolving loans account for **{revolving_applications:,}** applications.
""")

# 2. Default Rate by Contract Type
st.subheader("Default Rate by Contract Type")

contract_default = (
    df.groupby("NAME_CONTRACT_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)
contract_default.columns = ["Contract Type", "Default Rate"]

fig = px.bar(
    contract_default,
    x="Contract Type",
    y="Default Rate",
    text="Default Rate",
    title="Default Rate by Contract Type"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_rate_contract_type"
)

highest_contract_risk = contract_default.loc[
    contract_default["Default Rate"].idxmax()
]

lowest_contract_risk = contract_default.loc[
    contract_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{highest_contract_risk["Contract Type"]}** has the higher default rate at **{highest_contract_risk["Default Rate"]:.2f}%**.
- **{lowest_contract_risk["Contract Type"]}** has the lower default rate at **{lowest_contract_risk["Default Rate"]:.2f}%**.
- Contract type therefore shows a difference in observed default risk.
""")

# 3. Average Credit by Contract Type
st.subheader("Average Credit by Contract Type")

credit_contract = (
    df.groupby("NAME_CONTRACT_TYPE")["AMT_CREDIT"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
credit_contract.columns = ["Contract Type", "Average Credit"]

fig = px.bar(
    credit_contract,
    x="Contract Type",
    y="Average Credit",
    text="Average Credit",
    title="Average Credit by Contract Type"
)

fig.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside"
)

fig.update_yaxes(
    title="Average Credit",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="average_credit_contract_type"
)

highest_credit_contract = credit_contract.iloc[0]
lowest_credit_contract = credit_contract.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_credit_contract["Contract Type"]}** has the highest average credit of **₹{highest_credit_contract["Average Credit"]:,.0f}**.
- **{lowest_credit_contract["Contract Type"]}** has the lowest average credit of **₹{lowest_credit_contract["Average Credit"]:,.0f}**.
- Average credit differs between the two contract types.
""")

# 4. Average Income by Contract Type
st.subheader("Average Income by Contract Type")

income_contract = (
    df.groupby("NAME_CONTRACT_TYPE")["AMT_INCOME_TOTAL"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
income_contract.columns = ["Contract Type", "Average Income"]

fig = px.bar(
    income_contract,
    x="Contract Type",
    y="Average Income",
    text="Average Income",
    title="Average Income by Contract Type"
)

fig.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside"
)

fig.update_yaxes(
    title="Average Income",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="average_income_contract_type"
)

highest_income_contract = income_contract.iloc[0]
lowest_income_contract = income_contract.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_income_contract["Contract Type"]}** has the highest average income at **₹{highest_income_contract["Average Income"]:,.0f}**.
- **{lowest_income_contract["Contract Type"]}** has the lowest average income at **₹{lowest_income_contract["Average Income"]:,.0f}**.
- Income levels vary between contract types.
""")

# 5. Average Annuity by Contract Type
st.subheader("Average Annuity by Contract Type")

annuity_contract = (
    df.groupby("NAME_CONTRACT_TYPE")["AMT_ANNUITY"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
annuity_contract.columns = ["Contract Type", "Average Annuity"]

fig = px.bar(
    annuity_contract,
    x="Contract Type",
    y="Average Annuity",
    text="Average Annuity",
    title="Average Annuity by Contract Type"
)

fig.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside"
)

fig.update_yaxes(
    title="Average Annuity",
    tickformat=","
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="average_annuity_contract_type"
)

highest_annuity_contract = annuity_contract.iloc[0]
lowest_annuity_contract = annuity_contract.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_annuity_contract["Contract Type"]}** has the highest average annuity of **₹{highest_annuity_contract["Average Annuity"]:,.0f}**.
- **{lowest_annuity_contract["Contract Type"]}** has the lowest average annuity of **₹{lowest_annuity_contract["Average Annuity"]:,.0f}**.
- The difference indicates different repayment obligations across contract types.
""")

# 6. Credit-to-Income Ratio by Contract Type
st.subheader("Credit-to-Income Ratio by Contract Type")

ratio_data = df[
    ["NAME_CONTRACT_TYPE", "CREDIT_INCOME_RATIO"]
].dropna()

ratio_max = ratio_data["CREDIT_INCOME_RATIO"].quantile(0.99)

ratio_graph = ratio_data[
    ratio_data["CREDIT_INCOME_RATIO"] <= ratio_max
]

fig = px.box(
    ratio_graph,
    x="NAME_CONTRACT_TYPE",
    y="CREDIT_INCOME_RATIO",
    title="Credit-to-Income Ratio by Contract Type"
)

fig.update_xaxes(
    title="Contract Type"
)

fig.update_yaxes(
    title="Credit-to-Income Ratio"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="credit_income_ratio_contract_type"
)

ratio_contract = (
    ratio_data.groupby("NAME_CONTRACT_TYPE")["CREDIT_INCOME_RATIO"]
    .mean()
    .sort_values(ascending=False)
)

highest_ratio_contract = ratio_contract.index[0]
lowest_ratio_contract = ratio_contract.index[-1]

st.markdown(f"""
**Insights:**
- **{highest_ratio_contract}** has the higher average credit-to-income ratio of **{ratio_contract.iloc[0]:.2f}**.
- **{lowest_ratio_contract}** has the lower average ratio of **{ratio_contract.iloc[-1]:.2f}**.
- A higher ratio indicates that the requested credit is larger relative to customer income.
""")
