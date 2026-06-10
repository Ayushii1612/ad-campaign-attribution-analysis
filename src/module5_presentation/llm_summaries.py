"""
Module 5 — Automated Campaign Summary Report
Generates plain-English summaries from CSV outputs using rule-based logic.
No API key required.
"""

import pandas as pd
import os
from datetime import datetime


def summarise_attribution(attribution_csv: str) -> str:
    df = pd.read_csv(attribution_csv, index_col=0)

    lines = []
    lines.append("ATTRIBUTION MODEL INSIGHTS")
    lines.append("-" * 40)

    # Find channel with highest disagreement
    top_disagreement = df["Disagreement"].idxmax()
    lines.append(f"⚠️  '{top_disagreement}' has the highest model disagreement score "
                 f"({df.loc[top_disagreement, 'Disagreement']:.4f}). "
                 f"This means different models give it very different credit — "
                 f"do not trust Last Click alone for this channel.")

    # Last click vs data-driven gap
    for channel in df.index:
        lc  = df.loc[channel, "Last Click"]
        dd  = df.loc[channel, "Data-Driven"]
        gap = lc - dd
        if gap > 0.05:
            lines.append(f"📉 '{channel}' is OVER-credited by Last Click "
                         f"({lc:.1%} vs Data-Driven {dd:.1%}). "
                         f"It may be stealing credit from earlier touchpoints.")
        elif gap < -0.05:
            lines.append(f"📈 '{channel}' is UNDER-credited by Last Click "
                         f"({lc:.1%} vs Data-Driven {dd:.1%}). "
                         f"It likely drives awareness that other channels harvest.")

    # Top channel by data-driven
    top_dd = df["Data-Driven"].idxmax()
    lines.append(f"\n✅ Top channel by Data-Driven model: '{top_dd}' "
                 f"({df.loc[top_dd, 'Data-Driven']:.1%} of attributed revenue)")

    return "\n".join(lines)


def summarise_incrementality(incrementality_csv: str) -> str:
    df = pd.read_csv(incrementality_csv)

    lines = []
    lines.append("INCREMENTALITY TEST INSIGHTS")
    lines.append("-" * 40)

    # Negative ROAS channels
    negative = df[df["incremental_roas"] < 0]
    if len(negative) > 0:
        for _, row in negative.iterrows():
            lines.append(f"🔴 STOP SPENDING on '{row['channel']}' — "
                         f"Incremental ROAS is {row['incremental_roas']:.2f}x. "
                         f"This channel is HURTING conversions (p={row['p_value']:.4f}).")

    # Sub-1x ROAS channels
    sub1 = df[(df["incremental_roas"] >= 0) & (df["incremental_roas"] < 1)]
    for _, row in sub1.iterrows():
        lines.append(f"🟡 REDUCE budget on '{row['channel']}' — "
                     f"ROAS {row['incremental_roas']:.2f}x means you spend ₹1 to earn ₹{row['incremental_roas']:.2f}. "
                     f"Statistically significant: {row['significant_95']}.")

    # Best channels
    strong = df[df["incremental_roas"] >= 3].sort_values("incremental_roas", ascending=False)
    for _, row in strong.iterrows():
        lines.append(f"✅ INCREASE budget on '{row['channel']}' — "
                     f"Strong ROAS of {row['incremental_roas']:.2f}x. "
                     f"Incremental revenue: ₹{row['total_incremental_rev']:,.0f}.")

    # Total wasted spend
    wasted = df[df["incremental_roas"] < 1]["ad_spend"].sum()
    lines.append(f"\n💸 Total estimated wasted spend: ₹{wasted:,.0f}")

    return "\n".join(lines)


def explain_fraud_anomaly(fraud_csv: str) -> str:
    df = pd.read_csv(fraud_csv)

    lines = []
    lines.append("FRAUD DETECTION INSIGHTS")
    lines.append("-" * 40)

    for _, row in df.iterrows():
        if row["fraud_type"] == "TOTAL":
            lines.append(f"\n💰 TOTAL estimated fraud loss: ₹{row['estimated_loss_inr']:,.0f}")
            continue
        if row["fraud_type"] == "Click Velocity":
            lines.append(f"🚨 Click Velocity Fraud detected — estimated loss ₹{row['estimated_loss_inr']:,.0f}. "
                         f"One or more campaigns show 10x normal click rates. "
                         f"Action: Pause these campaigns and investigate publisher traffic.")
        elif row["fraud_type"] == "Impossible Paths":
            lines.append(f"🚨 Impossible Conversion Paths found — estimated misattribution ₹{row['estimated_loss_inr']:,.0f}. "
                         f"Conversions are timestamped BEFORE the ad was seen. "
                         f"Action: Audit your tracking pixel implementation.")
        elif row["fraud_type"] == "Suspicious Publisher":
            lines.append(f"🚨 Suspicious Publisher Traffic detected — estimated wasted spend ₹{row['estimated_loss_inr']:,.0f}. "
                         f"Conversion rate is less than 30% of average. "
                         f"Action: Blacklist these publishers immediately.")

    return "\n".join(lines)


def generate_full_report():
    print("Generating automated summary report...\n")

    summaries = {}

    if os.path.exists("data/outputs/attribution_comparison.csv"):
        summaries["Attribution"] = summarise_attribution("data/outputs/attribution_comparison.csv")
        print("✅ Attribution summary generated")
    else:
        print("⚠️  Skipping attribution — run Module 1 first")

    if os.path.exists("data/outputs/incrementality_results.csv"):
        summaries["Incrementality"] = summarise_incrementality("data/outputs/incrementality_results.csv")
        print("✅ Incrementality summary generated")
    else:
        print("⚠️  Skipping incrementality — run Module 2 first")

    if os.path.exists("data/outputs/fraud_impact.csv"):
        summaries["Fraud Detection"] = explain_fraud_anomaly("data/outputs/fraud_impact.csv")
        print("✅ Fraud summary generated")
    else:
        print("⚠️  Skipping fraud — run Module 4 first")

    # Write markdown report
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/campaign_summary_report.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Ad Campaign Attribution — Summary Report\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        f.write("---\n\n")
        for section, text in summaries.items():
            f.write(f"## {section}\n\n```\n{text}\n```\n\n---\n\n")

    print(f"\n📄 Report saved → {report_path}")
    return summaries


if __name__ == "__main__":
    generate_full_report()