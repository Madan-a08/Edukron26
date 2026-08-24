import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features

st.title("Gender Analysis")
st.write("Comparison of credit characteristics and default risk across genders.")

df = create_features(load_data())

# Filter
st.sidebar.header("Gender Filter")
gender = st.sidebar.multiselect(
    "Gender",
    df["CODE_GENDER"].dropna().unique(),
    format_func=lambda x: {"M": "Male", "F": "Female"}.get(x, x),
    key="gender_filter"
)

if gender:
    df = df[df["CODE_GENDER"].isin(gender)]

df["Gender"] = df["CODE_GENDER"].map({"M": "Male", "F": "Female"})

# KPIs
male_applicants = (df["CODE_GENDER"] == "M").sum()
female_applicants = (df["CODE_GENDER"] == "F").sum()
male_default_rate = df.loc[df["CODE_GENDER"] == "M", "TARGET"].mean() * 100
female_default_rate = df.loc[df["CODE_GENDER"] == "F", "TARGET"].mean() * 100

st.subheader("Key Performance Indicators")
cols = st.columns(4)
cols[0].metric("Male Applicants", f"{male_applicants:,}")
cols[1].metric("Female Applicants", f"{female_applicants:,}")
cols[2].metric("Male Default Rate", f"{male_default_rate:.2f}%")
cols[3].metric("Female Default Rate", f"{female_default_rate:.2f}%")

# 1. Applicants by Gender
st.subheader("Applicants by Gender")
applicant_data = df["Gender"].value_counts().reset_index()
applicant_data.columns = ["Gender", "Applicants"]

fig = px.pie(
    applicant_data,
    names="Gender",
    values="Applicants",
    hole=0.4,
    title="Applicants by Gender"
)
fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Applicants: %{value:,}<br>Percentage: %{percent}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True, key="gender_applicants")

top_gender = applicant_data.iloc[0]
gender_share = top_gender["Applicants"] / len(df) * 100

st.markdown(f"""
**Insights:**
- **{top_gender["Gender"]}** has the highest number of applicants with **{top_gender["Applicants"]:,}** customers.
- {top_gender["Gender"]} represents approximately **{gender_share:.2f}%** of the filtered applicants.
- The gender distribution shows the composition of the current applicant population.
""")

# 2. Default Customers by Gender
st.subheader("Default Customers by Gender")
default_data = df[df["TARGET"] == 1].groupby(
    "Gender").size().reset_index(name="Defaults")

fig = px.bar(
    default_data,
    x="Gender",
    y="Defaults",
    text="Defaults",
    title="Default Customers by Gender"
)
fig.update_traces(textposition="outside")
fig.update_yaxes(title="Number of Defaults")
st.plotly_chart(fig, use_container_width=True, key="gender_defaults")

top_default_gender = default_data.loc[default_data["Defaults"].idxmax()]

st.markdown(f"""
**Insights:**
- **{top_default_gender["Gender"]}** has the highest number of default customers with **{top_default_gender["Defaults"]:,}** defaults.
- The number of defaults depends partly on the size of each gender's applicant population.
- This chart shows default counts, while the next chart compares default rates more fairly.
""")

# 3. Default Rate by Gender
st.subheader("Default Rate by Gender")
default_rate_data = df.groupby(
    "Gender")["TARGET"].mean().mul(100).reset_index()
default_rate_data.columns = ["Gender", "Default Rate"]

fig = px.bar(
    default_rate_data,
    x="Gender",
    y="Default Rate",
    text="Default Rate",
    title="Default Rate by Gender"
)
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
st.plotly_chart(fig, use_container_width=True, key="gender_default_rate")

high_rate = default_rate_data.loc[default_rate_data["Default Rate"].idxmax()]
low_rate = default_rate_data.loc[default_rate_data["Default Rate"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_rate["Gender"]}** has the higher default rate at **{high_rate["Default Rate"]:.2f}%**.
- **{low_rate["Gender"]}** has the lower default rate at **{low_rate["Default Rate"]:.2f}%**.
- The difference between the two groups is **{high_rate["Default Rate"] - low_rate["Default Rate"]:.2f} percentage points**.
""")

# 4. Average Income by Gender
st.subheader("Average Income by Gender")
income_data = df.groupby("Gender")["AMT_INCOME_TOTAL"].mean().reset_index()
income_data.columns = ["Gender", "Average Income"]

fig = px.bar(
    income_data,
    x="Gender",
    y="Average Income",
    text="Average Income",
    title="Average Income by Gender"
)
fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
fig.update_yaxes(title="Average Income", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="gender_income")

high_income = income_data.loc[income_data["Average Income"].idxmax()]
low_income = income_data.loc[income_data["Average Income"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_income["Gender"]}** has the higher average income at approximately **₹{high_income["Average Income"]:,.0f}**.
- **{low_income["Gender"]}** has the lower average income at approximately **₹{low_income["Average Income"]:,.0f}**.
- The difference indicates variation in average income between genders.
""")

# 5. Average Credit by Gender
st.subheader("Average Credit by Gender")
credit_data = df.groupby("Gender")["AMT_CREDIT"].mean().reset_index()
credit_data.columns = ["Gender", "Average Credit"]

fig = px.bar(
    credit_data,
    x="Gender",
    y="Average Credit",
    text="Average Credit",
    title="Average Credit by Gender"
)
fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
fig.update_yaxes(title="Average Credit", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="gender_credit")

high_credit = credit_data.loc[credit_data["Average Credit"].idxmax()]
low_credit = credit_data.loc[credit_data["Average Credit"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_credit["Gender"]}** has the higher average credit amount at approximately **₹{high_credit["Average Credit"]:,.0f}**.
- **{low_credit["Gender"]}** has the lower average credit amount at approximately **₹{low_credit["Average Credit"]:,.0f}**.
- Average credit levels differ between the gender groups.
""")

# 6. Average Annuity by Gender
st.subheader("Average Annuity by Gender")
annuity_data = df.groupby("Gender")["AMT_ANNUITY"].mean().reset_index()
annuity_data.columns = ["Gender", "Average Annuity"]

fig = px.bar(
    annuity_data,
    x="Gender",
    y="Average Annuity",
    text="Average Annuity",
    title="Average Annuity by Gender"
)
fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
fig.update_yaxes(title="Average Annuity", tickformat=",")
st.plotly_chart(fig, use_container_width=True, key="gender_annuity")

high_annuity = annuity_data.loc[annuity_data["Average Annuity"].idxmax()]
low_annuity = annuity_data.loc[annuity_data["Average Annuity"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_annuity["Gender"]}** has the higher average annuity at approximately **₹{high_annuity["Average Annuity"]:,.0f}**.
- **{low_annuity["Gender"]}** has the lower average annuity at approximately **₹{low_annuity["Average Annuity"]:,.0f}**.
- Average annuity levels show the difference in typical repayment obligations between genders.
""")

# Gender Comparison
st.subheader("Gender Comparison")
comparison = df.groupby("Gender").agg(
    Customers=("Gender", "size"),
    Defaults=("TARGET", "sum"),
    Default_Rate=("TARGET", "mean"),
    Avg_Income=("AMT_INCOME_TOTAL", "mean"),
    Avg_Credit=("AMT_CREDIT", "mean"),
    Avg_Annuity=("AMT_ANNUITY", "mean")
).reset_index()

comparison["Default_Rate"] *= 100
comparison.columns = [
    "Gender", "Customers", "Defaults", "Default Rate",
    "Avg Income", "Avg Credit", "Avg Annuity"
]

comparison["Customers"] = comparison["Customers"].map(lambda x: f"{x:,}")
comparison["Defaults"] = comparison["Defaults"].map(lambda x: f"{x:,}")
comparison["Default Rate"] = comparison["Default Rate"].map(
    lambda x: f"{x:.2f}%")
comparison["Avg Income"] = comparison["Avg Income"].map(lambda x: f"₹{x:,.0f}")
comparison["Avg Credit"] = comparison["Avg Credit"].map(lambda x: f"₹{x:,.0f}")
comparison["Avg Annuity"] = comparison["Avg Annuity"].map(
    lambda x: f"₹{x:,.0f}")

st.dataframe(comparison, use_container_width=True, hide_index=True)
