"""
Module 2 — Incrementality Testing Framework
Split: 70% test (sees ad) vs 30% holdout (sees nothing).
Measures true causal lift using difference-in-proportions test.
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

np.random.seed(42)


def run_incrementality_test(df: pd.DataFrame) -> pd.DataFrame:
    channels = df["channel"].unique()
    results = []

    for channel in channels:
        channel_customers = df[df["channel"] == channel]["customer_id"].unique()
        n = len(channel_customers)
        n_test = int(n * 0.70)
        test_ids    = set(channel_customers[:n_test])
        holdout_ids = set(channel_customers[n_test:])

        channel_df = df[df["channel"] == channel].copy()
        channel_df["group"] = channel_df["customer_id"].apply(
            lambda x: "test" if x in test_ids else "holdout"
        )

        per_customer = channel_df.groupby(["customer_id", "group"]).agg(
            converted=("converted", "max"),
            revenue=("revenue", "max"),
        ).reset_index()

        test_group    = per_customer[per_customer["group"] == "test"]
        holdout_group = per_customer[per_customer["group"] == "holdout"]

        test_rate    = test_group["converted"].mean()
        holdout_rate = holdout_group["converted"].mean()
        incremental_rate = test_rate - holdout_rate

        n1, n2 = len(test_group), len(holdout_group)
        p1, p2 = test_rate, holdout_rate
        p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
        se     = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        z_stat = (p1 - p2) / se if se > 0 else 0
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        test_rev_per_user    = test_group["revenue"].mean()
        holdout_rev_per_user = holdout_group["revenue"].mean()
        incremental_rev_per_user = test_rev_per_user - holdout_rev_per_user

        test_basket    = test_group[test_group["converted"] == 1]["revenue"].mean()
        holdout_basket = holdout_group[holdout_group["converted"] == 1]["revenue"].mean()

        total_incremental_rev = incremental_rev_per_user * n_test
        ad_spend = df[df["channel"] == channel]["ad_spend"].sum()
        incremental_roas = total_incremental_rev / ad_spend if ad_spend > 0 else 0

        results.append({
            "channel":                  channel,
            "test_n":                   n_test,
            "holdout_n":                n - n_test,
            "test_purchase_rate":       round(test_rate, 4),
            "holdout_purchase_rate":    round(holdout_rate, 4),
            "incremental_rate":         round(incremental_rate, 4),
            "z_stat":                   round(z_stat, 3),
            "p_value":                  round(p_value, 4),
            "significant_95":           p_value < 0.05,
            "test_rev_per_user":        round(test_rev_per_user, 2),
            "holdout_rev_per_user":     round(holdout_rev_per_user, 2),
            "incremental_rev_per_user": round(incremental_rev_per_user, 2),
            "test_basket_size":         round(test_basket, 2) if not np.isnan(test_basket) else 0,
            "holdout_basket_size":      round(holdout_basket, 2) if not np.isnan(holdout_basket) else 0,
            "total_incremental_rev":    round(total_incremental_rev, 2),
            "ad_spend":                 round(ad_spend, 2),
            "incremental_roas":         round(incremental_roas, 3),
            "verdict":                  _verdict(incremental_roas, p_value),
        })

    result_df = pd.DataFrame(results).sort_values("incremental_roas", ascending=False)
    os.makedirs("data/outputs", exist_ok=True)
    result_df.to_csv("data/outputs/incrementality_results.csv", index=False)
    print("✅ Saved → data/outputs/incrementality_results.csv")
    return result_df


def _verdict(roas: float, p_value: float) -> str:
    if p_value >= 0.05:
        return "⚠️  Inconclusive — not statistically significant"
    if roas < 0:
        return "🔴 NEGATIVE — channel is hurting conversions"
    if roas < 1:
        return "🟡 Sub-1x ROAS — spending more than earning"
    if roas < 3:
        return "🟢 Positive — marginal ROI"
    return "✅ Strong — high incremental value"


def print_summary(result_df: pd.DataFrame):
    print("\n" + "="*80)
    print("INCREMENTALITY TEST RESULTS (14-Day Window, 70/30 Split)")
    print("="*80)
    cols = ["channel", "test_purchase_rate", "holdout_purchase_rate",
            "incremental_rate", "p_value", "significant_95", "incremental_roas", "verdict"]
    print(result_df[cols].to_string(index=False))
    wasted = result_df[result_df["incremental_roas"] < 1]["ad_spend"].sum()
    print(f"\n💸 Estimated wasted spend (ROAS < 1): ₹{wasted:,.0f}")


if __name__ == "__main__":
    df = pd.read_csv("data/raw/customer_journeys.csv",
                     parse_dates=["touchpoint_timestamp", "conversion_timestamp"])
    results = run_incrementality_test(df)
    print_summary(results)