import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Family & Children Analysis")
st.write("Analysis of household characteristics and their relationship with credit risk.")

df = apply_filters(create_features(load_data()))

# KPIs
average_children = df["CNT_CHILDREN"].mean()
average_family_members = df["CNT_FAM_MEMBERS"].mean()
customers_with_children = (df["CNT_CHILDREN"] > 0).sum()
customers_without_children = (df["CNT_CHILDREN"] == 0).sum()

family_risk = df.groupby("NAME_FAMILY_STATUS")["TARGET"].mean()
highest_risk_family = family_risk.idxmax()

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col1.metric("Average Children", f"{average_children:.1f}")
col2.metric("Average Family Members", f"{average_family_members:.1f}")
col3.metric("Customers with Children", f"{customers_with_children:,}")

col1, col2 = st.columns(2)
col1.metric("Customers without Children", f"{customers_without_children:,}")
col2.metric("Highest Risk Family Type", highest_risk_family)

# 1. Customers by Number of Children
st.subheader("Customers by Number of Children")

children_data = (
    df["CNT_CHILDREN"]
    .value_counts()
    .sort_index()
    .reset_index()
)
children_data.columns = ["Children", "Customers"]

fig = px.bar(
    children_data,
    x="Children",
    y="Customers",
    title="Customers by Number of Children"
)
fig.update_xaxes(title="Number of Children")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="customers_children")

most_common_children = children_data.loc[
    children_data["Customers"].idxmax()
]

st.markdown(f"""
**Insights:**
- Customers with **{most_common_children["Children"]:.0f} children** form the largest group.
- The average number of children is **{average_children:.1f}**.
- Customers without children account for **{customers_without_children:,}** applicants.
""")

# 2. Default Rate by Number of Children
st.subheader("Default Rate by Number of Children")

children_default = (
    df.groupby("CNT_CHILDREN")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)
children_default.columns = ["Children", "Default Rate"]

fig = px.line(
    children_default,
    x="Children",
    y="Default Rate",
    markers=True,
    title="Default Rate by Number of Children"
)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_children")

highest_children_risk = children_default.loc[
    children_default["Default Rate"].idxmax()
]
lowest_children_risk = children_default.loc[
    children_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- The highest default rate is **{highest_children_risk["Default Rate"]:.2f}%** for customers with **{highest_children_risk["Children"]:.0f} children**.
- The lowest default rate is **{lowest_children_risk["Default Rate"]:.2f}%** for customers with **{lowest_children_risk["Children"]:.0f} children**.
- Default risk varies across different numbers of children.
""")

# 3. Customers by Family Size
st.subheader("Customers by Family Size")

family_size = (
    df["CNT_FAM_MEMBERS"]
    .round()
    .value_counts()
    .sort_index()
    .reset_index()
)
family_size.columns = ["Family Size", "Customers"]

fig = px.bar(
    family_size,
    x="Family Size",
    y="Customers",
    title="Customers by Family Size"
)
fig.update_xaxes(title="Family Members")
fig.update_yaxes(title="Number of Customers")
st.plotly_chart(fig, use_container_width=True, key="customers_family_size")

largest_family_group = family_size.loc[
    family_size["Customers"].idxmax()
]

st.markdown(f"""
**Insights:**
- A family size of **{largest_family_group["Family Size"]:.0f} members** is the most common.
- The average family size is **{average_family_members:.1f} members**.
- Most applicants are concentrated in smaller family-size groups.
""")

# 4. Default Rate by Family Size
st.subheader("Default Rate by Family Size")

family_default = (
    df.groupby("CNT_FAM_MEMBERS")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)
family_default.columns = ["Family Size", "Default Rate"]

fig = px.line(
    family_default,
    x="Family Size",
    y="Default Rate",
    markers=True,
    title="Default Rate by Family Size"
)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_family_size")

highest_family_size_risk = family_default.loc[
    family_default["Default Rate"].idxmax()
]
lowest_family_size_risk = family_default.loc[
    family_default["Default Rate"].idxmin()
]

st.markdown(f"""
**Insights:**
- The highest default rate is **{highest_family_size_risk["Default Rate"]:.2f}%** for a family size of **{highest_family_size_risk["Family Size"]:.0f}**.
- The lowest default rate is **{lowest_family_size_risk["Default Rate"]:.2f}%** for a family size of **{lowest_family_size_risk["Family Size"]:.0f}**.
- Family size shows differences in observed default risk.
""")

# 5. Applications by Family Status
st.subheader("Applications by Family Status")

family_status = (
    df["NAME_FAMILY_STATUS"]
    .value_counts()
    .reset_index()
)
family_status.columns = ["Family Status", "Applications"]

fig = px.pie(
    family_status,
    names="Family Status",
    values="Applications",
    hole=0.4,
    title="Applications by Family Status"
)
fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Applications: %{value:,}<br>Percentage: %{percent}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True,
                key="applications_family_status")

largest_family_status = family_status.iloc[0]
status_percentage = (
    largest_family_status["Applications"] / len(df) * 100
)

st.markdown(f"""
**Insights:**
- **{largest_family_status["Family Status"]}** has the highest number of applications.
- It represents approximately **{status_percentage:.2f}%** of the filtered applicants.
- Applications are concentrated in a limited number of family-status categories.
""")

# 6. Default Rate by Family Status
st.subheader("Default Rate by Family Status")

family_status_default = (
    df.groupby("NAME_FAMILY_STATUS")["TARGET"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)
family_status_default.columns = ["Family Status", "Default Rate"]

fig = px.bar(
    family_status_default,
    x="Family Status",
    y="Default Rate",
    title="Default Rate by Family Status"
)
fig.update_xaxes(title="Family Status", tickangle=-20)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="default_family_status")

highest_status_risk = family_status_default.iloc[0]
lowest_status_risk = family_status_default.iloc[-1]

st.markdown(f"""
**Insights:**
- **{highest_status_risk["Family Status"]}** has the highest default rate at **{highest_status_risk["Default Rate"]:.2f}%**.
- **{lowest_status_risk["Family Status"]}** has the lowest default rate at **{lowest_status_risk["Default Rate"]:.2f}%**.
- Family status can be used to identify segments with different observed credit-risk levels.
""")

# 7. Income vs Family Size
st.subheader("Income vs Family Size")

income_family = df[
    ["CNT_FAM_MEMBERS", "AMT_INCOME_TOTAL"]
].dropna()

income_max = income_family["AMT_INCOME_TOTAL"].quantile(0.99)

income_family_graph = income_family[
    income_family["AMT_INCOME_TOTAL"] <= income_max
]

fig = px.scatter(
    income_family_graph,
    x="CNT_FAM_MEMBERS",
    y="AMT_INCOME_TOTAL",
    opacity=0.4,
    title="Income vs Family Size"
)
fig.update_xaxes(title="Family Size")
fig.update_yaxes(title="Income", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="income_family_size")

correlation = income_family_graph[
    ["CNT_FAM_MEMBERS", "AMT_INCOME_TOTAL"]
].corr().iloc[0, 1]

avg_income_small = income_family_graph.loc[
    income_family_graph["CNT_FAM_MEMBERS"] <= 3,
    "AMT_INCOME_TOTAL"
].mean()

avg_income_large = income_family_graph.loc[
    income_family_graph["CNT_FAM_MEMBERS"] > 3,
    "AMT_INCOME_TOTAL"
].mean()

st.markdown(f"""
**Insights:**
- The correlation between family size and income is **{correlation:.2f}**.
- Average income for families with **3 or fewer members** is approximately **₹{avg_income_small:,.0f}**.
- Average income for families with **more than 3 members** is approximately **₹{avg_income_large:,.0f}**.
""")
