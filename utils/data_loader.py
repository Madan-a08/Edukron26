import pandas as pd


def load_data():
    df = pd.read_csv(
        r"C:\Users\likit\Desktop\home_credit_dashboard\data\application_train.csv")
    return df
