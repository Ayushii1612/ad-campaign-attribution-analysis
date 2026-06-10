# Power BI Dashboard Setup Guide
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
