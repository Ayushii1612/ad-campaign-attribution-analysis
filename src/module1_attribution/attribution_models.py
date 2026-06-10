"""
Module 1 — Step 2: Multi-Touch Attribution Engine
Implements 5 models: Last Click, First Click, Linear, Time Decay, Data-Driven.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_data(path: str = "data/raw/customer_journeys.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["touchpoint_timestamp", "conversion_timestamp"])
    return df


def get_converting_journeys(df: pd.DataFrame) -> pd.DataFrame:
    converted_ids = df[df["converted"] == True]["customer_id"].unique()
    return df[df["customer_id"].isin(converted_ids)].copy()


def last_click_attribution(df: pd.DataFrame) -> pd.Series:
    conv = get_converting_journeys(df)
    last = conv.sort_values("touchpoint_timestamp").groupby("customer_id").last()
    credit = last.groupby("channel")["revenue"].sum()
    return credit / credit.sum()


def first_click_attribution(df: pd.DataFrame) -> pd.Series:
    conv = get_converting_journeys(df)
    first = conv.sort_values("touchpoint_timestamp").groupby("customer_id").first()
    credit = first.groupby("channel")["revenue"].sum()
    return credit / credit.sum()


def linear_attribution(df: pd.DataFrame) -> pd.Series:
    conv = get_converting_journeys(df)
    journey_len = conv.groupby("customer_id")["channel"].transform("count")
    conv = conv.copy()
    conv["credit"] = conv["revenue"] / journey_len
    credit = conv.groupby("channel")["credit"].sum()
    return credit / credit.sum()


def time_decay_attribution(df: pd.DataFrame, half_life_days: float = 7.0) -> pd.Series:
    conv = get_converting_journeys(df)
    conv = conv.copy()
    conv["hours_before_conv"] = (
        conv["conversion_timestamp"] - conv["touchpoint_timestamp"]
    ).dt.total_seconds() / 3600
    half_life_hours = half_life_days * 24
    conv["decay_weight"] = np.power(2, -conv["hours_before_conv"] / half_life_hours)
    total_weight = conv.groupby("customer_id")["decay_weight"].transform("sum")
    conv["credit"] = (conv["decay_weight"] / total_weight) * conv["revenue"]
    credit = conv.groupby("channel")["credit"].sum()
    return credit / credit.sum()


def data_driven_attribution(df: pd.DataFrame) -> pd.Series:
    pivot = (
        df.groupby(["customer_id", "channel"])
        .size()
        .unstack(fill_value=0)
        .clip(upper=1)
    )
    pivot["converted"] = df.groupby("customer_id")["converted"].max().astype(int)
    channels = [c for c in pivot.columns if c != "converted"]
    X = pivot[channels].values
    y = pivot["converted"].values
    model = LogisticRegression(max_iter=500)
    model.fit(X, y)
    coefficients = dict(zip(channels, model.coef_[0]))
    positive = {k: max(v, 0) for k, v in coefficients.items()}
    total = sum(positive.values()) or 1
    credit = pd.Series({k: v / total for k, v in positive.items()})
    return credit


def compare_all_models(df: pd.DataFrame) -> pd.DataFrame:
    print("Running attribution models...")
    results = pd.DataFrame({
        "Last Click":  last_click_attribution(df),
        "First Click": first_click_attribution(df),
        "Linear":      linear_attribution(df),
        "Time Decay":  time_decay_attribution(df),
        "Data-Driven": data_driven_attribution(df),
    }).fillna(0)
    results["Disagreement"] = results.std(axis=1).round(4)
    results = results.sort_values("Disagreement", ascending=False)
    os.makedirs("data/outputs", exist_ok=True)
    results.to_csv("data/outputs/attribution_comparison.csv")
    print("✅ Saved → data/outputs/attribution_comparison.csv")
    return results


def plot_comparison(results: pd.DataFrame):
    plot_data = results.drop(columns=["Disagreement"])
    plt.figure(figsize=(12, 6))
    sns.heatmap(plot_data, annot=True, fmt=".2%", cmap="YlOrRd", linewidths=0.5)
    plt.title("Attribution Credit by Model & Channel")
    plt.tight_layout()
    plt.savefig("data/outputs/attribution_heatmap.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    df = load_data()
    results = compare_all_models(df)
    print(results.to_string())
    plot_comparison(results)