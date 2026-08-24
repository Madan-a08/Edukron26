import pandas as pd


def create_features(df):

    df = df.copy()

    df["AGE"] = (
        abs(df["DAYS_BIRTH"]) / 365
    )

    df["DAYS_EMPLOYED"] = (
        df["DAYS_EMPLOYED"]
        .replace(365243, pd.NA)
    )

    df["DAYS_EMPLOYED"] = pd.to_numeric(
        df["DAYS_EMPLOYED"],
        errors="coerce"
    )

    df["EMPLOYMENT_YEARS"] = (
        df["DAYS_EMPLOYED"].abs() / 365
    )

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

    df["AVERAGE_EXTERNAL_SCORE"] = (
        df[
            [
                "EXT_SOURCE_1",
                "EXT_SOURCE_2",
                "EXT_SOURCE_3"
            ]
        ].mean(axis=1)
    )

    return df