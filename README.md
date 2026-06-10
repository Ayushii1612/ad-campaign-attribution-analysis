# Ad-campaign-attribution-analysis
This project addresses one of the most critical challenges in digital 
marketing — understanding which advertising channels genuinely drive 
purchases and which ones simply take credit for conversions that would 
have happened anyway. Using Python, the system simulates 500,000 customer 
journeys with realistic touchpoint patterns, injecting known anomalies such 
as click inflation on Meta Feed and awareness-only behavior on YouTube. Five 
attribution models are implemented from scratch and compared side by side, 
with a disagreement score highlighting channels where no single model should 
be trusted. The Data-Driven model using scikit-learn logistic regression 
serves as the most reliable signal, revealing that Direct channel is 
significantly under-credited by traditional Last Click analysis.

The incrementality testing framework is the analytical core of the project. 
By randomly splitting each channel's audience into a 70% test group that 
sees ads and a 30% holdout group that sees nothing, the system measures true 
causal lift using a two-proportion z-test. YouTube emerges as the only 
channel with a statistically significant result — but in the wrong direction, 
with a p-value of 0.033 and an incremental ROAS of -1.33x. The budget 
optimizer then uses PuLP linear programming to reallocate spend away from 
negative-ROAS channels toward high-performers, with constraints ensuring 
diversification and projecting ₹16 lakh in additional revenue.

The project covers the complete data-to-decision pipeline. SQL queries 
reconstruct customer journeys using window functions and cohort analysis. 
Fraud detection identifies 73 impossible conversion paths worth ₹4.27 lakh 
in misattributed revenue. A four-sheet Excel workbook delivers CMO-facing 
budget recommendations with live formulas and color-coded action items. A 
Power BI dashboard provides four pages of interactive visualizations covering 
attribution comparison, incrementality results, budget reallocation, and 
fraud impact — making every insight accessible to both technical and 
non-technical stakeholders.

# Features
- Simulates 500,000 customer journeys across 6 channels over 90 days
- Implements 5 attribution models: Last Click, First Click, Linear, Time Decay, Data-Driven
- Compares attribution credit distribution with model disagreement scoring
- Splits audience 70/30 for incrementality testing with statistical significance testing
- Calculates incremental ROAS per channel using two-proportion z-test at 95% confidence
- Identifies channels with negative incremental ROAS draining marketing budget
- Optimises budget allocation using PuLP linear programming
- Projects revenue impact of recommended budget reallocation in rupees
- Detects click velocity fraud, impossible conversion paths, and suspicious publisher traffic
- Quantifies financial impact of detected fraud per channel
- Generates 4-sheet Excel workbook with live formulas for CMO-level decisions
- Builds 4-page Power BI dashboard for interactive exploration
- Produces automated plain-English summary report without any API dependency
- Includes 6 production-ready SQL queries for journey reconstruction and cohort analysis
- Fully modular pipeline — each module runs independently or end-to-end

# Tech Stack
- Python 3.13 — core analysis and modeling
- pandas — data simulation, manipulation, aggregation
- NumPy — statistical computations and random simulation
- scikit-learn — logistic regression for data-driven attribution model
- scipy — z-test, p-values, statistical significance testing
- PuLP — linear programming budget optimization
- Matplotlib & Seaborn — attribution heatmap and budget charts
- openpyxl — Excel workbook generation with formatting and formulas
- Power BI Desktop — interactive 4-page dashboard
- SQL (SQLite) — customer journey reconstruction, window functions, cohort queries
- python-dotenv — environment configuration management

# Project Structure
```
ad-campaign-attribution-analysis/
│
├── run_pipeline.py                          # Master runner — executes all 5 modules
├── requirements.txt                         # All dependencies
├── .env.example                             # Environment variables template
├── README.md                                # Project documentation
│
├── src/
│   ├── module1_attribution/
│   │   ├── simulate_data.py                 # Generates 500K customer journeys
│   │   └── attribution_models.py            # 5 attribution models + heatmap
│   │
│   ├── module2_incrementality/
│   │   └── ab_test.py                       # 70/30 holdout test + z-test + ROAS
│   │
│   ├── module3_budget/
│   │   ├── optimizer.py                     # PuLP linear programming optimizer
│   │   └── excel_report.py                  # CMO-facing Excel workbook generator
│   │
│   ├── module4_fraud/
│   │   └── fraud_detector.py                # Velocity, paths, publisher fraud detection
│   │
│   └── module5_presentation/
│       └── llm_summaries.py                 # Rule-based automated report generator
│
├── sql/
│   └── attribution_queries.sql              # 6 SQL queries for journey analysis
│
├── dashboard/
│   ├── prepare_powerbi_data.py              # Prepares Power BI ready CSV tables
│   ├── POWERBI_SETUP_GUIDE.md               # Step-by-step Power BI guide
│   └── powerbi_data/                        # 6 CSV tables for Power BI
│       ├── attribution_models.csv
│       ├── incrementality_results.csv
│       ├── budget_optimisation.csv
│       ├── fraud_impact.csv
│       ├── channel_master.csv
│       └── summary_kpis.csv
│
├── data/
│   ├── raw/
│   │   └── customer_journeys.csv            # 2.3M rows simulated data
│   ├── processed/
│   └── outputs/
│       ├── attribution_comparison.csv
│       ├── attribution_heatmap.png
│       ├── incrementality_results.csv
│       ├── budget_optimisation.csv
│       ├── budget_optimisation.png
│       └── fraud_impact.csv
│
├── reports/
│   ├── budget_recommendation.xlsx           # 4-sheet CMO Excel report
│   └── campaign_summary_report.md           # Auto-generated text summary
│
└── utils/
    └── config.py                            # Shared configuration
```
