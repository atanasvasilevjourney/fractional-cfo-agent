"""
Generate sample financial data files for testing.
Run: python make_sample_data.py
"""

import csv
import os
from pathlib import Path

Path("drop-files-here").mkdir(exist_ok=True)

# ── Trial Balance ──
trial_balance = [
    ["Account Code", "Account Name", "Type", "Debit", "Credit"],
    ["4000", "Revenue - Product Sales",   "Revenue",   "",        "1,240,000"],
    ["4100", "Revenue - Services",         "Revenue",   "",          "180,000"],
    ["5000", "Cost of Goods Sold",         "COGS",    "620,000",         ""],
    ["5100", "Direct Labour",              "COGS",    "120,000",         ""],
    ["6000", "Salaries & Wages",           "OpEx",    "280,000",         ""],
    ["6100", "Rent & Occupancy",           "OpEx",     "45,000",         ""],
    ["6200", "Software & Subscriptions",   "OpEx",     "22,000",         ""],
    ["6300", "Marketing & Advertising",    "OpEx",     "38,000",         ""],
    ["6400", "Professional Services",      "OpEx",     "15,000",         ""],
    ["6500", "Travel & Entertainment",     "OpEx",      "8,500",         ""],
    ["6600", "Utilities",                  "OpEx",      "4,200",         ""],
    ["7000", "Depreciation",               "OpEx",     "12,000",         ""],
    ["7100", "Interest Expense",           "Finance",   "6,800",         ""],
    ["1000", "Cash & Cash Equivalents",    "Asset",   "310,000",         ""],
    ["1100", "Accounts Receivable",        "Asset",   "420,000",         ""],
    ["1200", "Inventory",                  "Asset",   "185,000",         ""],
    ["2000", "Accounts Payable",           "Liability",     "",    "198,000"],
    ["2100", "Accrued Liabilities",        "Liability",     "",     "45,000"],
    ["3000", "Retained Earnings",          "Equity",        "",    "256,500"],
]

with open("drop-files-here/trial_balance_2025_02.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(trial_balance)

# ── Budget ──
budget = [
    ["Account Name",           "Jan Budget", "Feb Budget", "Mar Budget", "Apr Budget", "Annual Budget"],
    ["Revenue - Product Sales", "1,100,000",  "1,150,000",  "1,200,000",  "1,250,000",  "14,400,000"],
    ["Revenue - Services",        "160,000",    "165,000",    "170,000",    "175,000",   "2,040,000"],
    ["Cost of Goods Sold",        "550,000",    "575,000",    "600,000",    "625,000",   "7,200,000"],
    ["Direct Labour",             "110,000",    "115,000",    "120,000",    "125,000",   "1,440,000"],
    ["Salaries & Wages",          "270,000",    "270,000",    "270,000",    "280,000",   "3,300,000"],
    ["Rent & Occupancy",           "45,000",     "45,000",     "45,000",     "45,000",     "540,000"],
    ["Software & Subscriptions",   "18,000",     "18,000",     "18,000",     "18,000",     "216,000"],
    ["Marketing & Advertising",    "30,000",     "30,000",     "35,000",     "35,000",     "400,000"],
    ["Professional Services",      "12,000",     "12,000",     "12,000",     "15,000",     "156,000"],
]

with open("drop-files-here/budget_fy2025.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(budget)

# ── AR Aging ──
ar_aging = [
    ["Invoice #", "Customer",    "Invoice Date", "Due Date",   "Amount",   "0-30 Days", "31-60 Days", "61-90 Days", "90+ Days"],
    ["INV-1041",  "Customer A",  "2025-02-01",   "2025-03-03", "45,000",   "45,000",    "",           "",           ""],
    ["INV-1039",  "Customer B",  "2025-01-15",   "2025-02-14", "82,000",   "",          "82,000",     "",           ""],
    ["INV-1035",  "Customer C",  "2025-01-05",   "2025-02-04", "28,500",   "",          "28,500",     "",           ""],
    ["INV-1029",  "Customer D",  "2024-12-20",   "2025-01-19", "61,200",   "",          "",           "61,200",     ""],
    ["INV-1021",  "Customer E",  "2024-12-01",   "2024-12-31", "38,000",   "",          "",           "",           "38,000"],
    ["INV-1018",  "Customer F",  "2024-11-15",   "2024-12-15", "22,000",   "",          "",           "",           "22,000"],
    ["INV-1042",  "Customer G",  "2025-02-10",   "2025-03-12", "93,000",   "93,000",    "",           "",           ""],
    ["INV-1040",  "Customer H",  "2025-02-05",   "2025-03-07", "56,300",   "56,300",    "",           "",           ""],
    ["TOTAL",     "",            "",             "",           "426,000",  "194,300",   "110,500",    "61,200",     "60,000"],
]

with open("drop-files-here/ar_aging_2025_02.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(ar_aging)

print("✅ Sample data files created in drop-files-here/")
print("   - trial_balance_2025_02.csv")
print("   - budget_fy2025.csv")
print("   - ar_aging_2025_02.csv")
print("\nNow run: python run.py --task full-suite --period 2025-02")
