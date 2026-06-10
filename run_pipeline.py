"""
run_pipeline.py — Run all 5 modules end-to-end. No API key required.
Usage: python run_pipeline.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.module1_attribution.simulate_data       import run_simulation
from src.module1_attribution.attribution_models   import compare_all_models, plot_comparison
from src.module2_incrementality.ab_test           import run_incrementality_test, print_summary
from src.module3_budget.optimizer                 import load_incrementality, optimise_budget, show_before_after
from src.module3_budget.excel_report              import generate_excel_report
from src.module4_fraud.fraud_detector             import (
    detect_click_velocity_fraud,
    detect_impossible_paths,
    detect_suspicious_publisher_patterns,
    calculate_fraud_impact,
    recommend_blacklist,
)
from src.module5_presentation.llm_summaries       import generate_full_report
from dashboard.prepare_powerbi_data               import prepare_powerbi_data


def main():
    print("\n" + "="*60)
    print("  AD CAMPAIGN ATTRIBUTION & INCREMENTALITY PIPELINE")
    print("="*60 + "\n")

    # ── MODULE 1: Simulate + Attribution ──
    print("► MODULE 1: Simulating customer journeys...")
    df = run_simulation()

    print("\n► MODULE 1: Running attribution models...")
    attribution_results = compare_all_models(df)
    plot_comparison(attribution_results)

    # ── MODULE 2: Incrementality ──
    print("\n► MODULE 2: Running incrementality test...")
    inc_results = run_incrementality_test(df)
    print_summary(inc_results)

    # ── MODULE 3: Budget Optimiser + Excel Report ──
    print("\n► MODULE 3: Optimising budget allocation...")
    inc_df = load_incrementality()
    current, recommended = optimise_budget(inc_df)
    show_before_after(current, recommended, inc_df)

    print("\n► MODULE 3: Generating Excel report (CMO-facing)...")
    generate_excel_report()

    # ── MODULE 4: Fraud Detection ──
    print("\n► MODULE 4: Running fraud detection...")
    velocity   = detect_click_velocity_fraud(df)
    impossible = detect_impossible_paths(df)
    publisher  = detect_suspicious_publisher_patterns(df)
    calculate_fraud_impact(velocity, impossible, publisher, df)
    recommend_blacklist(publisher)

    # ── MODULE 5: Automated Summary Report ──
    print("\n► MODULE 5: Generating summary report...")
    generate_full_report()

    # ── POWER BI: Prepare dashboard data ──
    print("\n► POWER BI: Preparing dashboard data tables...")
    prepare_powerbi_data()

    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE!")
    print("="*60)
    print("\n📁 data/outputs/")
    print("   ├── attribution_comparison.csv")
    print("   ├── attribution_heatmap.png")
    print("   ├── incrementality_results.csv")
    print("   ├── budget_optimisation.csv")
    print("   ├── budget_optimisation.png")
    print("   └── fraud_impact.csv")
    print("\n📁 reports/")
    print("   ├── budget_recommendation.xlsx  ← Open in Excel")
    print("   └── campaign_summary_report.md")
    print("\n📁 dashboard/powerbi_data/        ← Connect in Power BI")
    print("   ├── attribution_models.csv")
    print("   ├── incrementality_results.csv")
    print("   ├── budget_optimisation.csv")
    print("   ├── fraud_impact.csv")
    print("   ├── channel_master.csv")
    print("   └── summary_kpis.csv")
    print("\n📖 dashboard/POWERBI_SETUP_GUIDE.md ← Step-by-step Power BI guide\n")


if __name__ == "__main__":
    main()