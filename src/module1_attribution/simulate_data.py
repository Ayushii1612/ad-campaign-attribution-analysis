"""
Module 1 — Step 1: Simulate 500K Customer Journeys
Generates synthetic ad touchpoint data across 6 channels over 90 days.
Injects anomalies: one channel with inflated clicks, one awareness-only channel.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.config import CONFIG

np.random.seed(CONFIG["RANDOM_SEED"])

CHANNELS = [
    "Google Search",
    "YouTube",
    "Meta Feed",
    "Instagram Stories",
    "Email",
    "Direct",
]

CHANNEL_WEIGHTS = {
    "Google Search":      0.30,
    "YouTube":            0.20,
    "Meta Feed":          0.20,
    "Instagram Stories":  0.10,
    "Email":              0.10,
    "Direct":             0.10,
}

CHANNEL_CONVERSION_PROB = {
    "Google Search":      0.12,
    "YouTube":            0.02,
    "Meta Feed":          0.09,
    "Instagram Stories":  0.07,
    "Email":              0.11,
    "Direct":             0.15,
}

AD_SPEND_PER_CHANNEL = {
    "Google Search":      500_000,
    "YouTube":            300_000,
    "Meta Feed":          400_000,
    "Instagram Stories":  200_000,
    "Email":              100_000,
    "Direct":              50_000,
}

CAMPAIGN_IDS = {
    "Google Search":      ["GS_001", "GS_002", "GS_003"],
    "YouTube":            ["YT_001", "YT_002"],
    "Meta Feed":          ["MF_001", "MF_002", "MF_003"],
    "Instagram Stories":  ["IG_001", "IG_002"],
    "Email":              ["EM_001", "EM_002"],
    "Direct":             ["DR_001"],
}

SIM_START = datetime(2024, 1, 1)
SIM_END   = SIM_START + timedelta(days=CONFIG["SIMULATION_DAYS"])


def simulate_customer_journey(customer_id: int) -> list[dict]:
    records = []
    n_touchpoints = np.random.randint(1, 8)

    channels_in_journey = np.random.choice(
        CHANNELS,
        size=n_touchpoints,
        p=list(CHANNEL_WEIGHTS.values()),
        replace=True,
    )

    days_offsets = sorted(np.random.randint(0, CONFIG["SIMULATION_DAYS"], size=n_touchpoints))
    converted = False
    conversion_timestamp = None
    revenue = 0.0

    for i, (channel, day_offset) in enumerate(zip(channels_in_journey, days_offsets)):
        ts = SIM_START + timedelta(days=int(day_offset), hours=np.random.randint(0, 24))

        if channel == "Meta Feed" and np.random.rand() < 0.30:
            for _ in range(np.random.randint(2, 6)):
                records.append(_make_record(customer_id, channel, ts, False, None, 0.0))
            continue

        records.append(_make_record(customer_id, channel, ts, False, None, 0.0))

        if i == n_touchpoints - 1:
            conv_prob = CHANNEL_CONVERSION_PROB[channel]
            if np.random.rand() < conv_prob:
                converted = True
                conversion_timestamp = ts + timedelta(hours=np.random.randint(1, 48))
                revenue = round(np.random.lognormal(mean=6.5, sigma=0.8), 2)

    for r in records:
        r["converted"] = converted
        r["conversion_timestamp"] = conversion_timestamp
        r["revenue"] = revenue if converted else 0.0

    return records


def _make_record(customer_id, channel, ts, converted, conv_ts, revenue) -> dict:
    return {
        "customer_id":           customer_id,
        "channel":               channel,
        "touchpoint_timestamp":  ts,
        "touchpoint_type":       "click",
        "converted":             converted,
        "conversion_timestamp":  conv_ts,
        "revenue":               revenue,
        "campaign_id":           np.random.choice(CAMPAIGN_IDS[channel]),
        "ad_spend":              AD_SPEND_PER_CHANNEL[channel] / CONFIG["TOTAL_CUSTOMERS"],
    }


def run_simulation() -> pd.DataFrame:
    print(f"Simulating {CONFIG['TOTAL_CUSTOMERS']:,} customer journeys...")
    all_records = []

    for cid in range(1, CONFIG["TOTAL_CUSTOMERS"] + 1):
        all_records.extend(simulate_customer_journey(cid))
        if cid % 50_000 == 0:
            print(f"  → {cid:,} customers done")

    df = pd.DataFrame(all_records)
    df["touchpoint_timestamp"]  = pd.to_datetime(df["touchpoint_timestamp"])
    df["conversion_timestamp"]  = pd.to_datetime(df["conversion_timestamp"])
    df = df.sort_values(["customer_id", "touchpoint_timestamp"]).reset_index(drop=True)

    out_path = "data/raw/customer_journeys.csv"
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\n✅ Saved {len(df):,} rows → {out_path}")
    return df


if __name__ == "__main__":
    run_simulation()