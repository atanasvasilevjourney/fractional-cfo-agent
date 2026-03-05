# 💼 Fractional CFO Agent

AI-powered financial reporting — reads from Google Drive, runs OpenAI analysis, writes reports back to Drive automatically.

---

## 💰 Cost Estimate (Your $20 OpenAI Budget)

| Task | Cost per Run | Runs from $20 |
|------|-------------|---------------|
| Monthly Report | ~$0.01 | ~2,000 |
| Budget Variance | ~$0.01 | ~2,000 |
| Cash Flow Forecast | ~$0.01 | ~2,000 |
| Board Memo | ~$0.02 | ~1,000 |
| **Full Suite (all 4)** | **~$0.05** | **~400** |

**$20 = ~33 years of monthly full-suite runs.**

---

## 🏗 Architecture

```
Google Drive (CFO-Agent/Drop-Files-Here/)
        ↓  gws pulls files automatically
CFO Agent (Python + OpenAI GPT-4o-mini)
        ↓  gws pushes reports back
Google Drive (CFO-Agent/Reports/, /Board-Memos/, etc.)
        ↓  gws sends Gmail notification
Your inbox ✅
```

---

## 🚀 Setup (10 minutes total)

### Step 1 — Python dependencies
```bash
pip install openai pandas openpyxl python-dotenv flask
```

### Step 2 — Google Drive integration (gws)
```bash
npm install -g @googleworkspace/cli
gws auth setup    # one-time: walks you through Google OAuth
```

### Step 3 — Configure your .env
```bash
cp .env.example .env
# Edit .env and fill in:
#   OPENAI_API_KEY=sk-your-key-here
#   NOTIFY_EMAIL=you@yourcompany.com   (optional — get email when reports are ready)
```

### Step 4 — Create Drive folders (one-time)
```bash
python run.py --setup-drive
# Creates: CFO-Agent/Drop-Files-Here, /Reports, /Board-Memos, /Cash-Flow, /Budget-Variance
```

### Step 5 — Check everything is working
```bash
python run.py --check
# ✅ OpenAI API key:  Set
# ✅ gws CLI:         Installed
#    NOTIFY_EMAIL:    you@company.com
```

### Step 6 — Launch the dashboard
```bash
python dashboard.py
# Open: http://localhost:5000
```

---

## 📂 How to Use (Daily)

1. **Drop your financial files** into `CFO-Agent/Drop-Files-Here/` in Google Drive
2. **Click Run** in the dashboard (or run `python run.py --task full-suite`)
3. **Check your inbox** — notification arrives when reports are ready
4. **Reports appear automatically** in the correct Drive folders

---

## 📁 Drive Folder Structure (auto-created)

```
Google Drive/
└── 📂 CFO-Agent/
    ├── 📂 Drop-Files-Here/     ← You put files here
    ├── 📂 Reports/             ← Monthly financial reports
    ├── 📂 Budget-Variance/     ← Weekly variance reports
    ├── 📂 Cash-Flow/           ← 13-week forecasts
    └── 📂 Board-Memos/         ← Executive memo drafts
```

---

## 🖥 CLI Commands

```bash
# Run a single task (auto-detects Drive if gws installed)
python run.py --task monthly-report --period 2025-02

# Force Drive mode
python run.py --task full-suite --drive

# Force local folder mode (no Drive)
python run.py --task monthly-report --local

# One-time Drive folder setup
python run.py --setup-drive

# Check environment
python run.py --check

# Check OpenAI spend
python run.py --cost
```

---

## 📊 Report Types

| Command | What You Get |
|---------|-------------|
| `monthly-report` | Full P&L with commentary |
| `budget-variance` | Actuals vs budget, flagged variances |
| `cashflow-forecast` | 13-week rolling forecast, 3 scenarios |
| `board-memo` | Executive narrative memo draft |
| `full-suite` | All four at once |

---

## 🔒 Privacy

- Files stay in **your** Google Drive — never sent anywhere else
- Only **numbers and account labels** are sent to OpenAI — no names, no account numbers
- The gws CLI handles all Google auth locally on your machine

---

## 🆘 Troubleshooting

| Problem | Fix |
|---------|-----|
| `gws not found` | `npm install -g @googleworkspace/cli` |
| Drive auth error | `gws auth setup` (re-authenticate) |
| No files found | Check files are in `CFO-Agent/Drop-Files-Here/` in Drive |
| OpenAI error | Check `.env` has correct `OPENAI_API_KEY` |
| Reports not uploading | Run `python run.py --check` to diagnose |
