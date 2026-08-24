import streamlit as st


def apply_filters(df):

    st.sidebar.header("Filters")

    # CATEGORICAL FILTERS

    # Gender
    gender = st.sidebar.multiselect(
        "Gender",
        options=df["CODE_GENDER"].dropna().unique()
    )

    # Education
    education = st.sidebar.multiselect(
        "Education",
        options=df["NAME_EDUCATION_TYPE"].dropna().unique()
    )

    # Income Type
    income_type = st.sidebar.multiselect(
        "Income Type",
        options=df["NAME_INCOME_TYPE"].dropna().unique()
    )

    # Contract Type
    contract_type = st.sidebar.multiselect(
        "Contract Type",
        options=df["NAME_CONTRACT_TYPE"].dropna().unique()
    )

    # NUMERICAL FILTERS

    # Age Range
    age_range = st.sidebar.slider(
        "Age Range",
        min_value=int(df["AGE"].min()),
        max_value=int(df["AGE"].max()),
        value=(
            int(df["AGE"].min()),
            int(df["AGE"].max())
        )
    )

    # Income Range
    income_range = st.sidebar.slider(
        "Income Range",
        min_value=float(df["AMT_INCOME_TOTAL"].min()),
        max_value=float(df["AMT_INCOME_TOTAL"].max()),
        value=(
            float(df["AMT_INCOME_TOTAL"].min()),
            float(df["AMT_INCOME_TOTAL"].max())
        )
    )

    # Credit Range
    credit_range = st.sidebar.slider(
        "Credit Range",
        min_value=float(df["AMT_CREDIT"].min()),
        max_value=float(df["AMT_CREDIT"].max()),
        value=(
            float(df["AMT_CREDIT"].min()),
            float(df["AMT_CREDIT"].max())
        )
    )

    # APPLY CATEGORICAL FILTERS

    if gender:
        df = df[
            df["CODE_GENDER"].isin(gender)
        ]

    if education:
        df = df[
            df["NAME_EDUCATION_TYPE"].isin(education)
        ]

    if income_type:
        df = df[
            df["NAME_INCOME_TYPE"].isin(income_type)
        ]

    if contract_type:
        df = df[
            df["NAME_CONTRACT_TYPE"].isin(contract_type)
        ]

    # APPLY NUMERICAL FILTERS

    df = df[
        (df["AGE"] >= age_range[0]) &
        (df["AGE"] <= age_range[1])
    ]

    df = df[
        (df["AMT_INCOME_TOTAL"] >= income_range[0]) &
        (df["AMT_INCOME_TOTAL"] <= income_range[1])
    ]

    df = df[
        (df["AMT_CREDIT"] >= credit_range[0]) &
        (df["AMT_CREDIT"] <= credit_range[1])
    ]

    return df
