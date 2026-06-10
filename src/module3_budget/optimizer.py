"""
Module 3 — Budget Allocation Optimizer
Uses Linear Programming (PuLP) to reallocate budget based on true incremental ROAS.
"""

import pandas as pd
import numpy as np
import pulp
import matplotlib.pyplot as plt
import os

TOTAL_BUDGET = 1_550_000


def load_incrementality(path: str = "data/outputs/incrementality_results.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def optimise_budget(inc_df: pd.DataFrame) -> dict:
    positive_channels = inc_df[inc_df["incremental_roas"] > 0].copy()
    channels = positive_channels["channel"].tolist()
    roas_vals = dict(zip(positive_channels["channel"], positive_channels["incremental_roas"]))
    current_spend = dict(zip(inc_df["channel"], inc_df["ad_spend"]))

    prob = pulp.LpProblem("BudgetOptimizer", pulp.LpMaximize)
    x = {c: pulp.LpVariable(f"spend_{c.replace(' ', '_')}", lowBound=0) for c in channels}

    prob += pulp.lpSum(roas_vals[c] * x[c] for c in channels)
    prob += pulp.lpSum(x[c] for c in channels) == TOTAL_BUDGET
    for c in channels:
        prob += x[c] <= TOTAL_BUDGET * 0.50
    for c in channels:
        prob += x[c] >= TOTAL_BUDGET * 0.02

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    recommended = {c: x[c].varValue for c in channels}
    return current_spend, recommended


def show_before_after(current: dict, recommended: dict, inc_df: pd.DataFrame):
    roas = dict(zip(inc_df["channel"], inc_df["incremental_roas"]))
    comparison = []
    for channel in current:
        curr_spend = current.get(channel, 0)
        rec_spend  = recommended.get(channel, 0)
        curr_rev   = curr_spend * roas.get(channel, 0)
        rec_rev    = rec_spend  * roas.get(channel, 0)
        comparison.append({
            "Channel":             channel,
            "Current Spend (₹)":   round(curr_spend, 0),
            "Recommended (₹)":     round(rec_spend, 0),
            "Delta Spend (₹)":     round(rec_spend - curr_spend, 0),
            "Projected Rev Delta": round(rec_rev - curr_rev, 0),
        })

    comp_df = pd.DataFrame(comparison).sort_values("Projected Rev Delta", ascending=False)
    print("\n── Budget Reallocation Recommendations ──")
    print(comp_df.to_string(index=False))
    total_rev_gain = comp_df["Projected Rev Delta"].sum()
    print(f"\n💰 Projected incremental revenue gain: ₹{total_rev_gain:,.0f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    labels    = comp_df["Channel"].tolist()
    curr_vals = comp_df["Current Spend (₹)"].tolist()
    rec_vals  = comp_df["Recommended (₹)"].tolist()
    x_pos = range(len(labels))
    axes[0].bar(x_pos, curr_vals, color="#E57373", label="Current")
    axes[0].bar(x_pos, rec_vals,  color="#66BB6A", alpha=0.7, label="Recommended")
    axes[0].set_xticks(list(x_pos))
    axes[0].set_xticklabels(labels, rotation=30, ha="right")
    axes[0].set_title("Budget: Current vs Recommended")
    axes[0].set_ylabel("₹ Spend")
    axes[0].legend()

    delta_vals = comp_df["Projected Rev Delta"].tolist()
    colors = ["#66BB6A" if v >= 0 else "#E57373" for v in delta_vals]
    axes[1].barh(labels, delta_vals, color=colors)
    axes[1].axvline(0, color="black", linewidth=0.8)
    axes[1].set_title("Projected Revenue Change per Channel")
    axes[1].set_xlabel("₹ Revenue Delta")

    plt.tight_layout()
    os.makedirs("data/outputs", exist_ok=True)
    plt.savefig("data/outputs/budget_optimisation.png", dpi=150)
    plt.show()
    comp_df.to_csv("data/outputs/budget_optimisation.csv", index=False)
    print("✅ Saved → data/outputs/budget_optimisation.png")
    return comp_df


if __name__ == "__main__":
    inc_df = load_incrementality()
    current_spend, recommended_spend = optimise_budget(inc_df)
    show_before_after(current_spend, recommended_spend, inc_df)