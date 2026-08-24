import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Executive Overview")
st.write("Overall picture of loan applicants and credit risk.")

df = apply_filters(create_features(load_data()))

# KPIs
total_applications = len(df)
total_defaults = (df["TARGET"] == 1).sum()
total_non_defaults = (df["TARGET"] == 0).sum()
default_rate = df["TARGET"].mean() * 100
total_credit = df["AMT_CREDIT"].sum()
average_credit = df["AMT_CREDIT"].mean()
average_income = df["AMT_INCOME_TOTAL"].mean()
average_annuity = df["AMT_ANNUITY"].mean()

st.subheader("Key Performance Indicators")
cols = st.columns(4)
cols[0].metric("Total Applications", f"{total_applications:,}")
cols[1].metric("Total Default Customers", f"{total_defaults:,}")
cols[2].metric("Total Non-Default Customers", f"{total_non_defaults:,}")
cols[3].metric("Default Rate", f"{default_rate:.2f}%")

cols = st.columns(2)
cols[0].metric("Total Credit Amount", f"₹{total_credit:,.0f}")
cols[1].metric("Average Credit Amount", f"₹{average_credit:,.0f}")

cols = st.columns(2)
cols[0].metric("Average Income", f"₹{average_income:,.0f}")
cols[1].metric("Average Annuity", f"₹{average_annuity:,.0f}")

# 1. Default vs Non-Default
st.subheader("Default vs Non-Default Customers")
default_data = df["TARGET"].value_counts().sort_index().reset_index()
default_data.columns = ["TARGET", "Customers"]
default_data["Status"] = default_data["TARGET"].map(
    {0: "Non-Default", 1: "Default"})

fig = px.pie(default_data, names="Status", values="Customers",
             hole=0.4, title="Default vs Non-Default Customers", color="Status")
fig.update_traces(textinfo="percent+label+value",
                  hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>")
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
**Insights:**
- The overall default rate is **{default_rate:.2f}%**.
- **{total_defaults:,}** customers are classified as default, compared with **{total_non_defaults:,}** non-default customers.
- Non-default customers form the larger share of the applicant population.
""")

# 2. Applications by Gender
st.subheader("Total Applications by Gender")
gender_data = df["CODE_GENDER"].value_counts().reset_index()
gender_data.columns = ["Gender", "Applications"]
gender_data["Gender"] = gender_data["Gender"].map({"M": "Male", "F": "Female"})
gender_data["Percentage"] = gender_data["Applications"] / \
    total_applications * 100

fig = px.bar(gender_data, x="Gender", y="Applications",
             title="Total Applications by Gender", color="Gender", text="Applications")
fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Applications: %{y:,}<br>Percentage: %{customdata:.2f}%<extra></extra>",
    customdata=gender_data["Percentage"]
)
st.plotly_chart(fig, use_container_width=True)

top_gender = gender_data.loc[gender_data["Applications"].idxmax()]
st.markdown(f"""
**Insights:**
- **{top_gender["Gender"]}** has the highest number of applications with **{top_gender["Applications"]:,}** customers.
- {top_gender["Gender"]} represents approximately **{top_gender["Percentage"]:.2f}%** of all applications.
- The gender distribution shows the relative composition of the applicant population.
""")

# 3. Applications by Contract Type
st.subheader("Applications by Contract Type")
contract_data = df["NAME_CONTRACT_TYPE"].value_counts().reset_index()
contract_data.columns = ["Contract Type", "Applications"]
contract_data["Percentage"] = contract_data["Applications"] / \
    total_applications * 100

fig = px.bar(contract_data, x="Contract Type", y="Applications",
             title="Applications by Contract Type", color="Contract Type", text="Applications")
fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Applications: %{y:,}<br>Percentage: %{customdata:.2f}%<extra></extra>",
    customdata=contract_data["Percentage"]
)
st.plotly_chart(fig, use_container_width=True)

top_contract = contract_data.iloc[0]
st.markdown(f"""
**Insights:**
- **{top_contract["Contract Type"]}** has the highest number of applications with **{top_contract["Applications"]:,}** customers.
- It represents approximately **{top_contract["Percentage"]:.2f}%** of all applications.
- The contract mix indicates which loan product is most commonly used by applicants.
""")

# 4. Applications by Income Type
st.subheader("Applications by Income Type")
income_data = df["NAME_INCOME_TYPE"].value_counts().reset_index()
income_data.columns = ["Income Type", "Applications"]
income_data["Percentage"] = income_data["Applications"] / \
    total_applications * 100

fig = px.bar(income_data, x="Income Type", y="Applications",
             title="Applications by Income Type", color="Income Type", text="Applications")
fig.update_xaxes(tickangle=-30)
fig.update_traces(
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Applications: %{y:,}<br>Percentage: %{customdata:.2f}%<extra></extra>",
    customdata=income_data["Percentage"]
)
st.plotly_chart(fig, use_container_width=True)

top_income = income_data.iloc[0]
st.markdown(f"""
**Insights:**
- **{top_income["Income Type"]}** is the most common income type with **{top_income["Applications"]:,}** applications.
- It accounts for approximately **{top_income["Percentage"]:.2f}%** of all applicants.
- The distribution shows that applications are concentrated in a limited number of income categories.
""")

# 5. Credit Amount Distribution
st.subheader("Credit Amount Distribution")
fig = px.histogram(df, x="AMT_CREDIT", nbins=30,
                   title="Credit Amount Distribution")
fig.update_xaxes(title="Credit Amount", tickformat=",")
fig.update_yaxes(title="Number of Applications")
fig.update_traces(
    marker_color="#636EFA",
    hovertemplate="Credit Amount: %{x:,.0f}<br>Applications: %{y:,}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True)

credit_median = df["AMT_CREDIT"].median()
credit_max = df["AMT_CREDIT"].max()
st.markdown(f"""
**Insights:**
- The median credit amount is approximately **₹{credit_median:,.0f}**.
- Most applications are concentrated around the lower and middle credit ranges.
- The maximum credit amount reaches approximately **₹{credit_max:,.0f}**, indicating a smaller number of high-value applications.
""")

# 6. Overall Applicant Summary
st.subheader("Overall Applicant Summary")
most_common_income = df["NAME_INCOME_TYPE"].mode()[0]
most_common_education = df["NAME_EDUCATION_TYPE"].mode()[0]
highest_risk_income = df.groupby("NAME_INCOME_TYPE")["TARGET"].mean().idxmax()
highest_risk_rate = df.groupby("NAME_INCOME_TYPE")["TARGET"].mean().max() * 100

summary = pd.DataFrame({
    "Metric": [
        "Overall Default Rate",
        "Average Customer Income",
        "Average Loan Amount",
        "Most Common Income Type",
        "Most Common Education Level",
        "Highest Risk Customer Segment"
    ],
    "Value": [
        f"{default_rate:.2f}%",
        f"₹{average_income:,.0f}",
        f"₹{average_credit:,.0f}",
        most_common_income,
        most_common_education,
        f"{highest_risk_income} ({highest_risk_rate:.2f}% default rate)"
    ]
})
st.dataframe(summary, use_container_width=True, hide_index=True)
