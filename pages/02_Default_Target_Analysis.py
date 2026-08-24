import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Target / Default Analysis")
st.write("Analysis of the main TARGET variable and customer default risk.")

df = apply_filters(create_features(load_data()))

# KPIs
target_0 = (df["TARGET"] == 0).sum()
target_1 = (df["TARGET"] == 1).sum()
total_customers = len(df)
default_rate = df["TARGET"].mean() * 100
non_default_rate = 100 - default_rate

st.subheader("Key Performance Indicators")
cols = st.columns(4)
cols[0].metric("TARGET = 0 Customers", f"{target_0:,}")
cols[1].metric("TARGET = 1 Customers", f"{target_1:,}")
cols[2].metric("Default Rate", f"{default_rate:.2f}%")
cols[3].metric("Non-Default Rate", f"{non_default_rate:.2f}%")

# 1. TARGET Count
st.subheader("TARGET Count")
target_count = df["TARGET"].value_counts().sort_index().reset_index()
target_count.columns = ["TARGET", "Customers"]
target_count["Status"] = target_count["TARGET"].map(
    {0: "Non-Default", 1: "Default"})
target_count["Percentage"] = target_count["Customers"] / total_customers * 100

fig = px.bar(
    target_count,
    x="Status",
    y="Customers",
    title="TARGET Count",
    color="Status",
    text="Customers"
)

fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<br>Percentage: %{customdata:.2f}%<extra></extra>",
    customdata=target_count["Percentage"]
)

fig.update_yaxes(title="Number of Customers")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="target_count"
)

st.markdown(f"""
**Insights:**
- **{target_0:,}** customers are non-default, while **{target_1:,}** customers are defaults.
- Non-default customers make up **{non_default_rate:.2f}%** of the filtered dataset.
- Default customers represent **{default_rate:.2f}%** of all customers.
""")

# 2. TARGET Percentage
st.subheader("TARGET Percentage")

fig = px.pie(
    target_count,
    names="Status",
    values="Customers",
    hole=0.4,
    title="TARGET Percentage",
    color="Status"
)

fig.update_traces(
    textinfo="percent+label+value",
    hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="target_percentage"
)

st.markdown(f"""
**Insights:**
- The majority of customers are **non-default ({non_default_rate:.2f}%)**.
- Default customers account for **{default_rate:.2f}%** of the applicant population.
- The difference between the two groups indicates an imbalanced TARGET distribution.
""")

# 3. Default Rate by Gender
st.subheader("Default Rate by Gender")

gender_data = df.groupby("CODE_GENDER")["TARGET"].mean().mul(100).reset_index()

gender_data["Gender"] = gender_data["CODE_GENDER"].map(
    {"M": "Male", "F": "Female"})

gender_data.columns = ["CODE_GENDER", "Default Rate", "Gender"]

fig = px.bar(
    gender_data,
    x="Gender",
    y="Default Rate",
    title="Default Rate by Gender",
    color="Gender",
    text="Default Rate"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Default Rate: %{y:.2f}%<extra></extra>"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_gender"
)

gender_high = gender_data.loc[gender_data["Default Rate"].idxmax()]
gender_low = gender_data.loc[gender_data["Default Rate"].idxmin()]

st.markdown(f"""
**Insights:**
- **{gender_high["Gender"]}** has the higher default rate at **{gender_high["Default Rate"]:.2f}%**.
- **{gender_low["Gender"]}** has the lower default rate at **{gender_low["Default Rate"]:.2f}%**.
- The difference between the two rates is **{gender_high["Default Rate"] - gender_low["Default Rate"]:.2f} percentage points**.
""")

# 4. Default Rate by Income Type
st.subheader("Default Rate by Income Type")

income_data = df.groupby("NAME_INCOME_TYPE")[
    "TARGET"].mean().mul(100).reset_index()

income_data.columns = ["Income Type", "Default Rate"]

fig = px.bar(
    income_data,
    x="Income Type",
    y="Default Rate",
    title="Default Rate by Income Type",
    color="Income Type",
    text="Default Rate"
)

fig.update_xaxes(tickangle=-30)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Default Rate: %{y:.2f}%<extra></extra>"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_income"
)

income_high = income_data.loc[income_data["Default Rate"].idxmax()]
income_low = income_data.loc[income_data["Default Rate"].idxmin()]

st.markdown(f"""
**Insights:**
- **{income_high["Income Type"]}** has the highest default rate at **{income_high["Default Rate"]:.2f}%**.
- **{income_low["Income Type"]}** has the lowest default rate at **{income_low["Default Rate"]:.2f}%**.
- Default rates vary across income types, indicating differences in credit risk between income groups.
""")

# 5. Default Rate by Education
st.subheader("Default Rate by Education")

education_data = df.groupby("NAME_EDUCATION_TYPE")[
    "TARGET"].mean().mul(100).reset_index()

education_data.columns = ["Education", "Default Rate"]

fig = px.bar(
    education_data,
    x="Education",
    y="Default Rate",
    title="Default Rate by Education",
    color="Education",
    text="Default Rate"
)

fig.update_xaxes(tickangle=-30)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Default Rate: %{y:.2f}%<extra></extra>"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_education"
)

education_high = education_data.loc[
    education_data["Default Rate"].idxmax()
]

education_low = education_data.loc[
    education_data["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{education_high["Education"]}** has the highest default rate at **{education_high["Default Rate"]:.2f}%**.
- **{education_low["Education"]}** has the lowest default rate at **{education_low["Default Rate"]:.2f}%**.
- Default rates differ across education groups, showing variation in observed credit risk.
""")

# 6. Default Rate by Contract Type
st.subheader("Default Rate by Contract Type")

contract_data = df.groupby("NAME_CONTRACT_TYPE")[
    "TARGET"].mean().mul(100).reset_index()

contract_data.columns = ["Contract Type", "Default Rate"]

fig = px.bar(
    contract_data,
    x="Contract Type",
    y="Default Rate",
    title="Default Rate by Contract Type",
    color="Contract Type",
    text="Default Rate"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Default Rate: %{y:.2f}%<extra></extra>"
)

fig.update_yaxes(
    title="Default Rate (%)",
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="default_contract"
)

contract_high = contract_data.loc[
    contract_data["Default Rate"].idxmax()
]

contract_low = contract_data.loc[
    contract_data["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- **{contract_high["Contract Type"]}** has the higher default rate at **{contract_high["Default Rate"]:.2f}%**.
- **{contract_low["Contract Type"]}** has the lower default rate at **{contract_low["Default Rate"]:.2f}%**.
- The difference between contract types shows that observed default risk is not identical across loan products.
""")
