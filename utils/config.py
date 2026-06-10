"""
Shared configuration. Loaded by all modules.
Override values via .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "TOTAL_CUSTOMERS":   int(os.getenv("TOTAL_CUSTOMERS",   500_000)),
    "SIMULATION_DAYS":   int(os.getenv("SIMULATION_DAYS",   90)),
    "RANDOM_SEED":       int(os.getenv("RANDOM_SEED",       42)),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY",     ""),
}