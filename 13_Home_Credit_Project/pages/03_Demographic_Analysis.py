import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features

st.title("Customer Demographic Analysis")
st.write("Analysis of demographic characteristics of Home Credit applicants.")

df = create_features(load_data())

# Filters
st.sidebar.header("Demographic Filters")

gender = st.sidebar.multiselect(
    "Gender",
    df["CODE_GENDER"].dropna().unique(),
    key="demo_gender"
)

age_min, age_max = int(df["AGE"].min()), int(df["AGE"].max())

age_range = st.sidebar.slider(
    "Age",
    age_min,
    age_max,
    (age_min, age_max),
    key="demo_age"
)

family_status = st.sidebar.multiselect(
    "Family Status",
    df["NAME_FAMILY_STATUS"].dropna().unique(),
    key="demo_family"
)

education = st.sidebar.multiselect(
    "Education",
    df["NAME_EDUCATION_TYPE"].dropna().unique(),
    key="demo_education"
)

housing = st.sidebar.multiselect(
    "Housing Type",
    df["NAME_HOUSING_TYPE"].dropna().unique(),
    key="demo_housing"
)

if gender:
    df = df[df["CODE_GENDER"].isin(gender)]
if family_status:
    df = df[df["NAME_FAMILY_STATUS"].isin(family_status)]
if education:
    df = df[df["NAME_EDUCATION_TYPE"].isin(education)]
if housing:
    df = df[df["NAME_HOUSING_TYPE"].isin(housing)]
df = df[df["AGE"].between(age_range[0], age_range[1])]

# KPIs
total_customers = len(df)
average_age = df["AGE"].mean()
male_customers = (df["CODE_GENDER"] == "M").sum()
female_customers = (df["CODE_GENDER"] == "F").sum()
average_family_size = df["CNT_FAM_MEMBERS"].mean()

st.subheader("Key Performance Indicators")
cols = st.columns(4)
cols[0].metric("Total Customers", f"{total_customers:,}")
cols[1].metric("Average Age", f"{average_age:.1f} years")
cols[2].metric("Male Customers", f"{male_customers:,}")
cols[3].metric("Female Customers", f"{female_customers:,}")

cols = st.columns(2)
cols[0].metric("Average Family Size", f"{average_family_size:.1f}")
cols[1].metric("Selected Age Range", f"{age_range[0]}–{age_range[1]}")

# 1. Customers by Gender
st.subheader("Customers by Gender")
gender_data = df["CODE_GENDER"].value_counts().reset_index()
gender_data.columns = ["Gender", "Customers"]
gender_data["Gender"] = gender_data["Gender"].map({"M": "Male", "F": "Female"})

fig = px.pie(gender_data, names="Gender", values="Customers",
             hole=0.4, title="Customers by Gender",
             color="Gender", color_discrete_sequence=["#636EFA", "#EF553B"])
fig.update_traces(textinfo="label+percent+value",
                  hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>")
st.plotly_chart(fig, use_container_width=True, key="demo_gender_chart")

top_gender = gender_data.iloc[0]
st.markdown(f"""
**Insights:**
- **{top_gender["Gender"]}** has the highest number of customers with **{top_gender["Customers"]:,}** applicants.
- The gender distribution shows the composition of the selected customer population.
- The chart reflects the current filters, so the distribution changes when gender or other demographic filters are applied.
""")

# 2. Customers by Age Group
st.subheader("Customers by Age Group")
age_bins = [18, 25, 30, 35, 40, 45, 50, 55, 60, 100]
age_labels = ["18–25", "26–30", "31–35", "36–40",
              "41–45", "46–50", "51–55", "56–60", "61+"]

df["AGE_GROUP"] = pd.cut(df["AGE"], bins=age_bins,
                         labels=age_labels, include_lowest=True)

age_data = df["AGE_GROUP"].value_counts().reindex(age_labels).reset_index()
age_data.columns = ["Age Group", "Customers"]

fig = px.bar(age_data, x="Age Group", y="Customers",
             title="Customers by Age Group", color="Age Group",
             text="Customers",
             color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA",
                                      "#FFA15A", "#19D3F3", "#FF6692", "#B6E880", "#FF97FF"])
fig.update_yaxes(title="Number of Customers")
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True, key="demo_age_chart")

top_age = age_data.loc[age_data["Customers"].idxmax()]
st.markdown(f"""
**Insights:**
- The **{top_age["Age Group"]}** group contains the most customers with **{top_age["Customers"]:,}** applicants.
- Customer concentration is mainly visible across the working-age groups.
- The age distribution changes according to the selected age filter.
""")

# 3. Customers by Family Status
st.subheader("Customers by Family Status")
family_data = df["NAME_FAMILY_STATUS"].value_counts().reset_index()
family_data.columns = ["Family Status", "Customers"]
family_data["Family Status"] = family_data["Family Status"].replace({
    "Single / not married": "Single",
    "Civil marriage": "Civil Marriage",
    "Widow": "Widowed"
})

fig = px.pie(family_data, names="Family Status", values="Customers",
             hole=0.4, title="Customers by Family Status",
             color="Family Status",
             color_discrete_sequence=["#00CC96", "#EF553B", "#636EFA", "#AB63FA",
                                      "#FFA15A", "#19D3F3"])
fig.update_traces(textinfo="label+percent+value",
                  hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>")
st.plotly_chart(fig, use_container_width=True, key="demo_family_chart")

top_family = family_data.iloc[0]
st.markdown(f"""
**Insights:**
- **{top_family["Family Status"]}** is the most common family status with **{top_family["Customers"]:,}** customers.
- The chart shows how applicants are distributed across different household statuses.
- Family-status composition may change when demographic filters are applied.
""")

# 4. Customers by Education
st.subheader("Customers by Education")
education_data = df["NAME_EDUCATION_TYPE"].value_counts().reset_index()
education_data.columns = ["Education", "Customers"]

fig = px.bar(education_data, x="Education", y="Customers",
             title="Customers by Education", color="Education",
             text="Customers",
             color_discrete_sequence=["#FFA15A", "#636EFA", "#00CC96", "#EF553B",
                                      "#AB63FA", "#19D3F3"])
fig.update_xaxes(tickangle=-25)
fig.update_yaxes(title="Number of Customers")
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True, key="demo_education_chart")

top_education = education_data.iloc[0]
st.markdown(f"""
**Insights:**
- **{top_education["Education"]}** is the most common education category with **{top_education["Customers"]:,}** customers.
- The applicant population is concentrated in a smaller number of education categories.
- Education distribution reflects the characteristics of the currently selected customers.
""")

# 5. Customers by Housing Type
st.subheader("Customers by Housing Type")
housing_data = df["NAME_HOUSING_TYPE"].value_counts().reset_index()
housing_data.columns = ["Housing Type", "Customers"]

fig = px.bar(housing_data, x="Housing Type", y="Customers",
             title="Customers by Housing Type", color="Housing Type",
             text="Customers",
             color_discrete_sequence=["#19D3F3", "#FF6692", "#636EFA", "#00CC96",
                                      "#FFA15A", "#AB63FA"])
fig.update_xaxes(tickangle=-25)
fig.update_yaxes(title="Number of Customers")
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True, key="demo_housing_chart")

top_housing = housing_data.iloc[0]
st.markdown(f"""
**Insights:**
- **{top_housing["Housing Type"]}** is the most common housing category with **{top_housing["Customers"]:,}** customers.
- Applicants are distributed unevenly across housing categories.
- The housing profile reflects the current filtered customer population.
""")

# 6. Default Rate by Education
st.subheader("Default Rate by Education")
education_default = df.groupby("NAME_EDUCATION_TYPE")[
    "TARGET"].mean().mul(100).reset_index()
education_default.columns = ["Education", "Default Rate"]

fig = px.bar(education_default, x="Education", y="Default Rate",
             title="Default Rate by Education", color="Education",
             text="Default Rate",
             color_discrete_sequence=["#EF553B", "#00CC96", "#636EFA", "#FFA15A",
                                      "#AB63FA", "#19D3F3"])
fig.update_xaxes(tickangle=-25)
fig.update_yaxes(title="Default Rate (%)", ticksuffix="%")
fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
st.plotly_chart(fig, use_container_width=True, key="demo_education_default")

high_default = education_default.loc[education_default["Default Rate"].idxmax(
)]
low_default = education_default.loc[education_default["Default Rate"].idxmin()]

st.markdown(f"""
**Insights:**
- **{high_default["Education"]}** has the highest observed default rate at **{high_default["Default Rate"]:.2f}%**.
- **{low_default["Education"]}** has the lowest observed default rate at **{low_default["Default Rate"]:.2f}%**.
- The difference indicates that default rates vary across education groups.
""")
