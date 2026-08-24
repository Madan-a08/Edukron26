import streamlit as st
import pandas as pd

from utils.data_loader import load_data
from utils.features import create_features


st.title("Customer Risk Explorer")

st.write(
    "Search and explore individual customer risk profiles and filtered applicant records."
)


# =====================================================
# LOAD DATA
# =====================================================

df = load_data()
df = create_features(df)


# =====================================================
# RISK INDICATORS
# =====================================================

df["CREDIT_INCOME_RATIO"] = (
    df["AMT_CREDIT"] /
    df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
)

df["ANNUITY_INCOME_RATIO"] = (
    df["AMT_ANNUITY"] /
    df["AMT_INCOME_TOTAL"].replace(0, pd.NA)
)

df["CREDIT_GOODS_RATIO"] = (
    df["AMT_CREDIT"] /
    df["AMT_GOODS_PRICE"].replace(0, pd.NA)
)

df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(
    365243,
    pd.NA
)

df["EMPLOYMENT_YEARS"] = (
    df["DAYS_EMPLOYED"].abs() / 365
)

df["AVERAGE_EXTERNAL_SCORE"] = df[
    [
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3"
    ]
].mean(axis=1)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Customer Filters")


# Customer ID

search_id = st.sidebar.text_input(
    "Search Customer ID",
    key="customer_id_search"
)


# TARGET

target_filter = st.sidebar.multiselect(
    "TARGET",
    [0, 1],
    format_func=lambda x:
        "Non-Default" if x == 0 else "Default",
    key="target_filter"
)


# Gender

gender_filter = st.sidebar.multiselect(
    "Gender",
    sorted(df["CODE_GENDER"].dropna().unique()),
    format_func=lambda x:
        "Male" if x == "M"
        else "Female" if x == "F"
        else x,
    key="gender_filter"
)


# Age

age_data = df["AGE"].dropna()

age_min = int(age_data.min())
age_max = int(age_data.max())

use_age = st.sidebar.checkbox(
    "Enable Age Filter",
    key="use_age"
)

if use_age:

    age_filter = st.sidebar.slider(
        "Age",
        age_min,
        age_max,
        (age_min, age_max),
        key="age_range"
    )


# Income Type

income_filter = st.sidebar.multiselect(
    "Income Type",
    sorted(
        df["NAME_INCOME_TYPE"]
        .dropna()
        .unique()
    ),
    key="income_type_filter"
)


# Education

education_filter = st.sidebar.multiselect(
    "Education",
    sorted(
        df["NAME_EDUCATION_TYPE"]
        .dropna()
        .unique()
    ),
    key="education_filter"
)


# Occupation

occupation_filter = st.sidebar.multiselect(
    "Occupation",
    sorted(
        df["OCCUPATION_TYPE"]
        .dropna()
        .unique()
    ),
    key="occupation_filter"
)


# Contract

contract_filter = st.sidebar.multiselect(
    "Contract Type",
    sorted(
        df["NAME_CONTRACT_TYPE"]
        .dropna()
        .unique()
    ),
    key="contract_filter"
)


# Housing

housing_filter = st.sidebar.multiselect(
    "Housing Type",
    sorted(
        df["NAME_HOUSING_TYPE"]
        .dropna()
        .unique()
    ),
    key="housing_filter"
)


# Car

car_filter = st.sidebar.multiselect(
    "Car Ownership",
    ["Y", "N"],
    format_func=lambda x:
        "Owns Car" if x == "Y"
        else "Does Not Own Car",
    key="car_filter"
)


# Property

property_filter = st.sidebar.multiselect(
    "Property Ownership",
    ["Y", "N"],
    format_func=lambda x:
        "Owns Property" if x == "Y"
        else "Does Not Own Property",
    key="property_filter"
)


# Income Range

income_data = df["AMT_INCOME_TOTAL"].dropna()

income_min = float(income_data.min())
income_max = float(income_data.max())

use_income = st.sidebar.checkbox(
    "Enable Income Filter",
    key="use_income"
)

if use_income:

    income_filter = st.sidebar.slider(
        "Income Range",
        income_min,
        income_max,
        (income_min, income_max),
        key="income_range"
    )


# Credit Range

credit_data = df["AMT_CREDIT"].dropna()

credit_min = float(credit_data.min())
credit_max = float(credit_data.max())

use_credit = st.sidebar.checkbox(
    "Enable Credit Filter",
    key="use_credit"
)

if use_credit:

    credit_filter = st.sidebar.slider(
        "Credit Range",
        credit_min,
        credit_max,
        (credit_min, credit_max),
        key="credit_range"
    )


# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()


if search_id.strip():

    filtered_df = filtered_df[
        filtered_df["SK_ID_CURR"]
        .astype(str)
        .str.contains(
            search_id.strip(),
            na=False
        )
    ]


if target_filter:

    filtered_df = filtered_df[
        filtered_df["TARGET"].isin(
            target_filter
        )
    ]


if gender_filter:

    filtered_df = filtered_df[
        filtered_df["CODE_GENDER"].isin(
            gender_filter
        )
    ]


if use_age:

    filtered_df = filtered_df[
        filtered_df["AGE"].between(
            age_filter[0],
            age_filter[1]
        )
    ]


if income_filter:

    filtered_df = filtered_df[
        filtered_df["NAME_INCOME_TYPE"].isin(
            income_filter
        )
    ]


if education_filter:

    filtered_df = filtered_df[
        filtered_df["NAME_EDUCATION_TYPE"].isin(
            education_filter
        )
    ]


if occupation_filter:

    filtered_df = filtered_df[
        filtered_df["OCCUPATION_TYPE"].isin(
            occupation_filter
        )
    ]


if contract_filter:

    filtered_df = filtered_df[
        filtered_df["NAME_CONTRACT_TYPE"].isin(
            contract_filter
        )
    ]


if housing_filter:

    filtered_df = filtered_df[
        filtered_df["NAME_HOUSING_TYPE"].isin(
            housing_filter
        )
    ]


if car_filter:

    filtered_df = filtered_df[
        filtered_df["FLAG_OWN_CAR"].isin(
            car_filter
        )
    ]


if property_filter:

    filtered_df = filtered_df[
        filtered_df["FLAG_OWN_REALTY"].isin(
            property_filter
        )
    ]


if use_income:

    filtered_df = filtered_df[
        filtered_df["AMT_INCOME_TOTAL"].between(
            income_filter[0],
            income_filter[1]
        )
    ]


if use_credit:

    filtered_df = filtered_df[
        filtered_df["AMT_CREDIT"].between(
            credit_filter[0],
            credit_filter[1]
        )
    ]


# =====================================================
# FILTERED CUSTOMERS
# =====================================================

st.subheader("Filtered Customers")

st.metric(
    "Customers Found",
    f"{len(filtered_df):,}"
)


# =====================================================
# CUSTOMER PROFILE
# =====================================================

if len(filtered_df) > 0:

    customer_ids = (
        filtered_df["SK_ID_CURR"]
        .dropna()
        .astype(int)
        .tolist()
    )

    selected_customer = st.selectbox(
        "Select Customer",
        customer_ids,
        key="selected_customer"
    )

    customer = filtered_df[
        filtered_df["SK_ID_CURR"] ==
        selected_customer
    ].iloc[0]

    st.subheader("Customer Risk Profile")

    target = (
        "Default"
        if customer["TARGET"] == 1
        else "Non-Default"
    )

    gender = {
        "M": "Male",
        "F": "Female"
    }.get(
        customer["CODE_GENDER"],
        customer["CODE_GENDER"]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Customer ID",
        int(customer["SK_ID_CURR"])
    )

    col2.metric(
        "TARGET",
        target
    )

    col3.metric(
        "Age",
        f"{customer['AGE']:.1f} years"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Gender",
        gender
    )

    col2.metric(
        "Income",
        f"₹{customer['AMT_INCOME_TOTAL']:,.0f}"
    )

    col3.metric(
        "Credit Amount",
        f"₹{customer['AMT_CREDIT']:,.0f}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Annuity",
        f"₹{customer['AMT_ANNUITY']:,.0f}"
    )

    col2.metric(
        "Education",
        customer["NAME_EDUCATION_TYPE"]
    )

    col3.metric(
        "Occupation",
        customer["OCCUPATION_TYPE"]
        if pd.notna(customer["OCCUPATION_TYPE"])
        else "Unknown"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Family Status",
        customer["NAME_FAMILY_STATUS"]
    )

    col2.metric(
        "Number of Children",
        int(customer["CNT_CHILDREN"])
    )

    col3.metric(
        "Housing Type",
        customer["NAME_HOUSING_TYPE"]
    )

    # =================================================
    # EXTERNAL SCORES
    # =================================================

    st.subheader("External Credit Scores")

    scores = pd.DataFrame({
        "Score": [
            "EXT_SOURCE_1",
            "EXT_SOURCE_2",
            "EXT_SOURCE_3",
            "Average External Score"
        ],
        "Value": [
            customer["EXT_SOURCE_1"],
            customer["EXT_SOURCE_2"],
            customer["EXT_SOURCE_3"],
            customer["AVERAGE_EXTERNAL_SCORE"]
        ]
    })

    scores["Value"] = scores["Value"].round(3)

    st.dataframe(
        scores,
        use_container_width=True,
        hide_index=True
    )

    # =================================================
    # RISK INDICATORS
    # =================================================

    st.subheader("Calculated Risk Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Credit-to-Income Ratio",
        f"{customer['CREDIT_INCOME_RATIO']:.2f}"
    )

    col2.metric(
        "Annuity-to-Income Ratio",
        f"{customer['ANNUITY_INCOME_RATIO']:.2f}"
    )

    col3.metric(
        "Credit-to-Goods Ratio",
        f"{customer['CREDIT_GOODS_RATIO']:.2f}"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Employment Years",
        f"{customer['EMPLOYMENT_YEARS']:.1f}"
    )

    col2.metric(
        "Average External Score",
        f"{customer['AVERAGE_EXTERNAL_SCORE']:.3f}"
    )


else:

    st.warning(
        "No customers match the selected filters."
    )


# =====================================================
# APPLICANT TABLE
# =====================================================

st.subheader("Filtered Applicant Records")


columns = [
    "SK_ID_CURR",
    "TARGET",
    "AGE",
    "CODE_GENDER",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "NAME_EDUCATION_TYPE",
    "OCCUPATION_TYPE",
    "NAME_FAMILY_STATUS",
    "CNT_CHILDREN",
    "NAME_HOUSING_TYPE",
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3"
]


columns = [
    col
    for col in columns
    if col in filtered_df.columns
]


table = filtered_df[columns].copy()


table["TARGET"] = table["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})


table["CODE_GENDER"] = table[
    "CODE_GENDER"
].map({
    "M": "Male",
    "F": "Female"
})


st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)
