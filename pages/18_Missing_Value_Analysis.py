import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.features import create_features
from utils.filters import apply_filters

st.title("Missing Value Analysis")
st.write("Analysis of missing values to understand data quality before machine-learning models.")

df = load_data()
df = create_features(df)
df = apply_filters(df)

# Missing Value Summary
missing_count = df.isna().sum()
missing_percent = df.isna().mean() * 100

missing_data = pd.DataFrame({
    "Column": df.columns,
    "Missing Count": missing_count.values,
    "Missing %": missing_percent.values,
    "Data Type": df.dtypes.astype(str).values
}).sort_values("Missing Count", ascending=False)

# KPIs
total_rows = len(df)
total_columns = len(df.columns)
total_missing = int(missing_count.sum())
columns_with_missing = (missing_count > 0).sum()
columns_over_50 = (missing_percent > 50).sum()

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", f"{total_rows:,}")
col2.metric("Total Columns", f"{total_columns:,}")
col3.metric("Total Missing Values", f"{total_missing:,}")

col1, col2 = st.columns(2)
col1.metric("Columns with Missing Values", f"{columns_with_missing:,}")
col2.metric("Columns with >50% Missing Data", f"{columns_over_50:,}")

# 1. Top 20 Columns with Missing Values
st.subheader("Top 20 Columns with Missing Values")

top_missing = (
    missing_data[missing_data["Missing Count"] > 0]
    .head(20)
    .sort_values("Missing Count")
)

fig = px.bar(
    top_missing,
    x="Missing Count",
    y="Column",
    orientation="h",
    text="Missing Count",
    title="Top 20 Columns with Missing Values",
    color="Missing Count",
    color_continuous_scale="Reds"
)

fig.update_traces(textposition="outside")
fig.update_xaxes(title="Missing Values")
fig.update_yaxes(title="Column")
st.plotly_chart(fig, use_container_width=True, key="top_missing_values")

top_column = top_missing.loc[top_missing["Missing Count"].idxmax()]

st.markdown(
    f"""
**Insights:**
- **{top_column['Column']}** has the highest number of missing values among the displayed columns.
- The top missing columns require attention before using the dataset for machine-learning models.
- Missing-value treatment should depend on the meaning and data type of each column.
"""
)

# 2. Top 20 Columns by Missing Percentage
st.subheader("Missing Percentage by Column")

percentage_data = (
    missing_data[missing_data["Missing %"] > 0]
    .head(20)
    .sort_values("Missing %")
)

fig = px.bar(
    percentage_data,
    x="Missing %",
    y="Column",
    orientation="h",
    text="Missing %",
    title="Top 20 Columns by Missing Percentage",
    color="Missing %",
    color_continuous_scale="Oranges"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)
fig.update_xaxes(title="Missing Percentage (%)")
fig.update_yaxes(title="Column")
st.plotly_chart(fig, use_container_width=True, key="missing_percentage")

highest_missing = percentage_data.loc[
    percentage_data["Missing %"].idxmax()
]

st.markdown(
    f"""
**Insights:**
- **{highest_missing['Column']}** has the highest missing percentage among the displayed columns.
- Columns with a very high percentage of missing values may provide limited predictive information.
- Columns with moderate missingness can generally be considered for suitable imputation methods.
"""
)

# 3. Missing Values Heatmap
st.subheader("Missing Values Heatmap")

heatmap_data = (
    missing_data[missing_data["Missing %"] > 0]
    .head(30)
    .sort_values("Missing %", ascending=False)
)

fig = px.imshow(
    heatmap_data.set_index("Column")[["Missing %"]].T,
    labels={
        "x": "Column",
        "y": "",
        "color": "Missing %"
    },
    aspect="auto",
    color_continuous_scale="Viridis",
    title="Missing Value Percentage Heatmap"
)

fig.update_xaxes(tickangle=-45)
fig.update_yaxes(showticklabels=False)

st.plotly_chart(fig, use_container_width=True, key="missing_heatmap")

st.markdown(
    """
**Insights:**
- Darker areas indicate columns with a higher percentage of missing values.
- Missingness is concentrated in a subset of columns rather than being evenly distributed.
- The heatmap helps quickly identify columns that require priority during data preprocessing.
"""
)

# 4. Missing Value Distribution
st.subheader("Columns by Missing Value Category")

category_data = pd.DataFrame({
    "Category": [
        "No Missing Values",
        "1–25% Missing",
        "25–50% Missing",
        "Above 50% Missing"
    ],
    "Columns": [
        (missing_percent == 0).sum(),
        ((missing_percent > 0) & (missing_percent <= 25)).sum(),
        ((missing_percent > 25) & (missing_percent <= 50)).sum(),
        (missing_percent > 50).sum()
    ]
})

fig = px.bar(
    category_data,
    x="Category",
    y="Columns",
    text="Columns",
    title="Columns by Missing Value Category",
    color="Category"
)

fig.update_traces(textposition="outside")
fig.update_xaxes(title="Missing Value Category")
fig.update_yaxes(title="Number of Columns")

st.plotly_chart(
    fig,
    use_container_width=True,
    key="missing_categories"
)

largest_category = category_data.loc[
    category_data["Columns"].idxmax()
]

st.markdown(
    f"""
**Insights:**
- The largest category is **{largest_category['Category']}**, containing **{largest_category['Columns']} columns**.
- This provides an overall view of the dataset's missing-value quality.
- Columns above 50% missing data should be reviewed carefully before modeling.
"""
)

# 5. Missing Value Details
st.subheader("Missing Value Details")

table_data = missing_data.copy()
table_data["Missing %"] = table_data["Missing %"].round(2)

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)

# 6. Important Actions
st.subheader("Important Actions")

st.write(
    "Use the missing-value percentage and column meaning to decide the appropriate treatment."
)

actions = pd.DataFrame({
    "Missing Value Situation": [
        "Very high missing percentage",
        "Numeric column with moderate missing values",
        "Numeric column with skewed values",
        "Categorical column",
        "Missingness itself may be meaningful"
    ],
    "Possible Action": [
        "Drop the column",
        "Fill with Mean",
        "Fill with Median",
        "Fill with Mode or 'Unknown'",
        "Create Missing Indicator"
    ]
})

st.dataframe(
    actions,
    use_container_width=True,
    hide_index=True
)
