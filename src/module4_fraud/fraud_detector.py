"""
Module 4 — Attribution Fraud Detection
Detects: click velocity anomalies, impossible conversion paths,
suspicious publisher traffic. Calculates financial impact.
"""

import pandas as pd
import numpy as np
import os


def detect_click_velocity_fraud(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour_bucket"] = df["touchpoint_timestamp"].dt.floor("H")
    clicks_per_hour = (
        df.groupby(["campaign_id", "hour_bucket"])
        .size()
        .reset_index(name="clicks_in_hour")
    )
    median_clicks = clicks_per_hour["clicks_in_hour"].median()
    threshold = median_clicks * 10
    suspicious = clicks_per_hour[clicks_per_hour["clicks_in_hour"] > threshold].copy()
    suspicious["fraud_type"] = "Click Velocity Anomaly"
    suspicious["description"] = f">{threshold:.0f} clicks/hour (10x median {median_clicks:.0f})"
    print(f"[Velocity] Found {len(suspicious)} suspicious campaign-hour pairs")
    return suspicious


def detect_impossible_paths(df: pd.DataFrame) -> pd.DataFrame:
    conv = df[df["converted"] == True].copy()
    impossible = conv[conv["conversion_timestamp"] < conv["touchpoint_timestamp"]].copy()
    impossible["fraud_type"] = "Impossible Conversion Path"
    impossible["description"] = "conversion_timestamp is BEFORE touchpoint_timestamp"
    print(f"[Impossible Paths] Found {len(impossible)} suspicious records")
    return impossible[["customer_id", "channel", "campaign_id",
                        "touchpoint_timestamp", "conversion_timestamp",
                        "fraud_type", "description"]]


def detect_suspicious_publisher_patterns(df: pd.DataFrame) -> pd.DataFrame:
    channel_stats = df.groupby("channel").agg(
        total_clicks=("customer_id", "count"),
        total_converts=("converted", "sum"),
        total_spend=("ad_spend", "sum"),
    ).reset_index()
    channel_stats["conversion_rate"] = (
        channel_stats["total_converts"] / channel_stats["total_clicks"]
    )
    mean_cvr = channel_stats["conversion_rate"].mean()
    flagged = channel_stats[channel_stats["conversion_rate"] < mean_cvr * 0.3].copy()
    flagged["fraud_type"] = "Suspicious Publisher Traffic"
    flagged["description"] = f"CVR < 30% of mean ({mean_cvr:.4f}). Likely click inflation."
    print(f"[Publisher] Flagged {len(flagged)} channels with suspicious traffic patterns")
    return flagged


def calculate_fraud_impact(velocity_df, impossible_df, publisher_df, df) -> pd.DataFrame:
    impact = []
    if len(velocity_df) > 0:
        flagged_campaigns = velocity_df["campaign_id"].unique()
        spend = df[df["campaign_id"].isin(flagged_campaigns)]["ad_spend"].sum()
        impact.append({"fraud_type": "Click Velocity", "estimated_loss_inr": round(spend, 2)})
    if len(impossible_df) > 0:
        lost_rev = df[df["customer_id"].isin(impossible_df["customer_id"])]["revenue"].sum()
        impact.append({"fraud_type": "Impossible Paths", "estimated_loss_inr": round(lost_rev, 2)})
    if len(publisher_df) > 0:
        spend = publisher_df["total_spend"].sum()
        impact.append({"fraud_type": "Suspicious Publisher", "estimated_loss_inr": round(spend, 2)})

    impact_df = pd.DataFrame(impact)
    total = impact_df["estimated_loss_inr"].sum()
    impact_df.loc[len(impact_df)] = ["TOTAL", total]

    os.makedirs("data/outputs", exist_ok=True)
    impact_df.to_csv("data/outputs/fraud_impact.csv", index=False)
    print(f"\n✅ Saved → data/outputs/fraud_impact.csv")
    print(f"   💸 Total estimated fraud loss: ₹{total:,.0f}")
    return impact_df


def recommend_blacklist(publisher_df: pd.DataFrame) -> list:
    blacklist = publisher_df["channel"].tolist()
    print(f"\n🚫 Recommended blacklist: {blacklist}")
    return blacklist


if __name__ == "__main__":
    df = pd.read_csv("data/raw/customer_journeys.csv",
                     parse_dates=["touchpoint_timestamp", "conversion_timestamp"])
    print("=" * 60)
    print("FRAUD DETECTION ANALYSIS")
    print("=" * 60)
    velocity   = detect_click_velocity_fraud(df)
    impossible = detect_impossible_paths(df)
    publisher  = detect_suspicious_publisher_patterns(df)
    impact_df  = calculate_fraud_impact(velocity, impossible, publisher, df)
    print(impact_df.to_string(index=False))
    recommend_blacklist(publisher)