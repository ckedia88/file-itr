# file-itr — India ITR-1 / ITR-2 skill

A VS Code Copilot **skill** to prepare, reconcile, and verify an Indian individual
return — **ITR-1 (Sahaj)** (resident, income ≤ ₹50L, salary/pension + one house
property + other sources, optional §112A LTCG ≤ ₹1.25L) and **ITR-2** (salaried
resident with foreign RSU/ESPP, foreign dividends + Foreign Tax Credit, Indian +
foreign capital gains, mutual funds, LRS, and Schedule AL). Includes an
ITR-1-vs-ITR-2 eligibility gate (SKILL.md §0.5).

> **Advisory only.** This is not tax advice. Always get a CA sign-off before
> filing, especially for foreign income / Schedule FA / FTC.

## Contents

| File | Purpose |
|---|---|
| `SKILL.md` | The skill instructions (intake, reconciliation, gotchas, verification, FX/price sourcing). Auto-invoked by Copilot from its `description`. |
| `schedule_fa.py` | Scrubbed, **data-free** FX-rate + price-peak engine (SBI TT loader, `_rate_for`, `peak_inr_for_lot`). Reusable across tickers. |
| `fetch_data.py` | Optional, stdlib-only downloader for `sbi_usd.csv` (SBI ratekeeper) and `<ticker>.csv` (Stooq → Yahoo fallback), in the loader's CSV format. |
| `itr1_skeleton.json` | **Data-free** ITR-1 (Sahaj) JSON template (AY 2026-27) with placeholders. Validate against the official schema before upload. |
| `itr2_skeleton.json` | **Data-free** ITR-2 JSON template (AY 2026-27) with placeholders — salary, OS, Schedule CG/112A, SI, CYLA/BFLA, Part B-TI/TTI. Validate before upload. |

## Data files you supply (not included)

None of these are shipped — they are user-specific and must be added locally:

- `sbi_usd.csv` — `SBI_REFERENCE_RATES_USD.csv` from the public
  [`sahilgupta/sbi-fx-ratekeeper`](https://github.com/sahilgupta/sbi-fx-ratekeeper)
  repo (columns `DATE, TT BUY, ...`).
- `rbi_ref.csv` — optional manual `date,rate` overrides (for pre-dataset dates).
- `<ticker>.csv` — daily close price export (investing.com / Yahoo "Historical
  Data"), e.g. `msft.csv`, `qcom.csv`, `intel.csv`.

See **section 7** of `SKILL.md` for step-by-step sourcing (including the 10-year
history export).

## Privacy

Do **not** commit personal identifiers or financial documents (PAN, Aadhaar,
bank/account numbers, Form 16, AIS/TIS, 1042-S, broker statements, generated ITR
JSON). Keep those outside the distributed skill folder.

## Quick check

```python
import schedule_fa as sf
sf._rate_for("2025-12-22")          # SBI TT USD->INR for a date
sf.peak_inr_for_lot(10, __import__("datetime").date(2024, 3, 28),
                    sf.load_price_series(__import__("pathlib").Path("msft.csv")))
```
