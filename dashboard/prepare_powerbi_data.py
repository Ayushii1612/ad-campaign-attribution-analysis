"""
Power BI Data Preparation Script
Structures all outputs into Power BI-ready CSVs with proper relationships.
Also generates a setup guide for connecting Power BI to the data.
"""

import pandas as pd
import os
from datetime import datetime


def prepare_powerbi_data():
    """
    Reshape and enrich all output CSVs into Power BI-ready format.
    Creates a /dashboard/powerbi_data/ folder with all tables.
    """
    os.makedirs("dashboard/powerbi_data", exist_ok=True)
    print("Preparing Power BI data tables...\n")

    # ── TABLE 1: Attribution Model Comparison (unpivoted for Power BI) ──
    if os.path.exists("data/outputs/attribution_comparison.csv"):
        attr_df = pd.read_csv("data/outputs/attribution_comparison.csv", index_col=0)

        # Melt wide → long format (Power BI loves long format for visuals)
        attr_long = attr_df.drop(columns=["Disagreement"]).reset_index()
        attr_long = attr_long.rename(columns={"index": "Channel"})
        attr_long = attr_long.melt(
            id_vars="Channel",
            var_name="Model",
            value_name="Attribution_Share"
        )
        attr_long["Attribution_Pct"] = (attr_long["Attribution_Share"] * 100).round(2)

        # Add disagreement back
        disagreement = attr_df["Disagreement"].reset_index()
        disagreement.columns = ["Channel", "Disagreement_Score"]
        attr_long = attr_long.merge(disagreement, on="Channel", how="left")

        attr_long.to_csv("dashboard/powerbi_data/attribution_models.csv", index=False)
        print("✅ attribution_models.csv — use for: Bar chart comparing 5 models per channel")

    # ── TABLE 2: Incrementality Results ──
    if os.path.exists("data/outputs/incrementality_results.csv"):
        inc_df = pd.read_csv("data/outputs/incrementality_results.csv")

        # Add budget decision column for slicers
        def budget_action(roas, sig):
            if not sig:
                return "Inconclusive"
            if roas < 0:
                return "STOP — Negative ROAS"
            if roas < 1:
                return "REDUCE — Sub-1x ROAS"
            if roas < 3:
                return "MAINTAIN"
            return "INCREASE — Strong ROAS"

        inc_df["Budget_Action"] = inc_df.apply(
            lambda r: budget_action(r["incremental_roas"], r["significant_95"]), axis=1
        )
        inc_df["Wasted_Spend_INR"] = inc_df.apply(
            lambda r: r["ad_spend"] if r["incremental_roas"] < 1 else 0, axis=1
        )
        inc_df.to_csv("dashboard/powerbi_data/incrementality_results.csv", index=False)
        print("✅ incrementality_results.csv — use for: KPI cards, waterfall chart, gauge visuals")

    # ── TABLE 3: Budget Optimisation ──
    if os.path.exists("data/outputs/budget_optimisation.csv"):
        budget_df = pd.read_csv("data/outputs/budget_optimisation.csv")
        budget_df.to_csv("dashboard/powerbi_data/budget_optimisation.csv", index=False)
        print("✅ budget_optimisation.csv — use for: Before/After budget bar chart")

    # ── TABLE 4: Fraud Impact ──
    if os.path.exists("data/outputs/fraud_impact.csv"):
        fraud_df = pd.read_csv("data/outputs/fraud_impact.csv")
        fraud_df.to_csv("dashboard/powerbi_data/fraud_impact.csv", index=False)
        print("✅ fraud_impact.csv — use for: Fraud impact donut / table visual")

    # ── TABLE 5: Channel Master (dimension table for relationships) ──
    channels = [
        "Google Search", "YouTube", "Meta Feed",
        "Instagram Stories", "Email", "Direct"
    ]
    channel_master = pd.DataFrame({
        "Channel":       channels,
        "Channel_Type":  ["Paid Search", "Video", "Social", "Social", "Owned", "Direct"],
        "Channel_Cost":  ["High", "High", "Medium", "Medium", "Low", "None"],
        "Funnel_Stage":  ["Bottom", "Top", "Mid", "Mid", "Bottom", "Bottom"],
        "Total_Budget_INR": [500000, 300000, 400000, 200000, 100000, 50000],
    })
    channel_master.to_csv("dashboard/powerbi_data/channel_master.csv", index=False)
    print("✅ channel_master.csv — dimension table for relationships in Power BI model")

    # ── TABLE 6: Summary KPIs ──
    if os.path.exists("data/outputs/incrementality_results.csv") and \
       os.path.exists("data/outputs/budget_optimisation.csv"):
        inc_df    = pd.read_csv("data/outputs/incrementality_results.csv")
        budget_df = pd.read_csv("data/outputs/budget_optimisation.csv")

        kpis = pd.DataFrame([
            {"Metric": "Total Ad Spend (₹)",        "Value": inc_df["ad_spend"].sum()},
            {"Metric": "Estimated Wasted Spend (₹)", "Value": inc_df[inc_df["incremental_roas"]<1]["ad_spend"].sum()},
            {"Metric": "Channels with Positive ROAS","Value": len(inc_df[inc_df["incremental_roas"]>0])},
            {"Metric": "Channels with Negative ROAS","Value": len(inc_df[inc_df["incremental_roas"]<0])},
            {"Metric": "Projected Revenue Gain (₹)", "Value": budget_df["Projected Rev Delta"].sum()},
            {"Metric": "Best Channel by ROAS",        "Value": inc_df.loc[inc_df["incremental_roas"].idxmax(), "channel"]},
            {"Metric": "Worst Channel by ROAS",       "Value": inc_df.loc[inc_df["incremental_roas"].idxmin(), "channel"]},
            {"Metric": "Report Generated",            "Value": datetime.now().strftime("%Y-%m-%d %H:%M")},
        ])
        kpis.to_csv("dashboard/powerbi_data/summary_kpis.csv", index=False)
        print("✅ summary_kpis.csv — use for: KPI card visuals on dashboard home page")

    print(f"\n📁 All Power BI tables saved → dashboard/powerbi_data/")
    generate_powerbi_guide()


def generate_powerbi_guide():
    """Write step-by-step Power BI connection guide."""
    guide = """# Power BI Dashboard Setup Guide
## Ad Campaign Attribution & Incrementality Analysis

---

## Step 1 — Open Power BI Desktop
Download free from: https://powerbi.microsoft.com/desktop

---

## Step 2 — Load Data Tables

1. Click **Home → Get Data → Text/CSV**
2. Load ALL 6 files from `dashboard/powerbi_data/`:
   - `attribution_models.csv`
   - `incrementality_results.csv`
   - `budget_optimisation.csv`
   - `fraud_impact.csv`
   - `channel_master.csv`
   - `summary_kpis.csv`

---

## Step 3 — Build Relationships (Model View)

Go to **Model View** (left sidebar icon) and connect:

| From Table | From Column | To Table | To Column |
|------------|-------------|----------|-----------|
| attribution_models | Channel | channel_master | Channel |
| incrementality_results | channel | channel_master | Channel |
| budget_optimisation | Channel | channel_master | Channel |

---

## Step 4 — Recommended Dashboard Pages

### Page 1: Executive Overview
- **KPI Cards** from `summary_kpis.csv`:
  - Total Ad Spend | Wasted Spend | Projected Gain | Best Channel
- **Donut Chart**: Budget_Action count from `incrementality_results`
- **Bar Chart**: incremental_roas per channel (color by Budget_Action)

### Page 2: Attribution Analysis
- **Clustered Bar Chart**:
  - X-axis: Channel
  - Y-axis: Attribution_Pct
  - Legend: Model
  - (From `attribution_models.csv`)
- **Heatmap Matrix**:
  - Rows: Channel | Columns: Model | Values: Attribution_Pct
- **Bar Chart**: Disagreement_Score per Channel (highlights unreliable channels)

### Page 3: Incrementality Testing
- **Waterfall Chart**:
  - Category: channel
  - Y-axis: incremental_roas
- **Scatter Plot**:
  - X: ad_spend | Y: incremental_roas | Size: total_incremental_rev
- **Table**: Full results with conditional formatting

### Page 4: Budget Optimisation
- **Clustered Bar Chart**: Current vs Recommended spend
- **Bar Chart**: Projected Revenue Delta per Channel
- **KPI**: Total projected revenue gain

### Page 5: Fraud Detection
- **Table**: fraud_impact with total row
- **Donut Chart**: Fraud type breakdown

---

## Step 5 — Add Conditional Formatting

For the incrementality table, add data bars or color scales:
1. Click the visual → Format → Cell elements
2. Set color scale: Red (negative) → Yellow (0) → Green (positive)

---

## Step 6 — Publish (Optional)

**Home → Publish → My Workspace** to share with stakeholders via browser.

---

## Tips
- Use **Slicer** on `Channel_Type` or `Funnel_Stage` from channel_master for filtering
- Use **Bookmarks** to create a guided presentation flow
- Save the .pbix file in the `dashboard/` folder
"""

    with open("dashboard/POWERBI_SETUP_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide)
    print("📖 Power BI setup guide saved → dashboard/POWERBI_SETUP_GUIDE.md")


if __name__ == "__main__":
    prepare_powerbi_data()