---
name: file-itr
description: >-
  Prepare, reconcile, and verify an Indian individual income-tax return — both
  ITR-1 (Sahaj: resident, income ≤ ₹50L, salary/pension + one house property +
  other sources, optional §112A LTCG ≤ ₹1.25L) and ITR-2 (salaried resident with
  foreign RSU/ESPP via broker custodians such as Fidelity / E*TRADE; example
  tickers MSFT / QCOM / INTC; foreign dividends + Foreign Tax Credit; Indian +
  foreign capital gains; mutual funds; LRS remittances; Schedule AL). Includes an
  ITR-1-vs-ITR-2 eligibility gate. USE WHEN the user says "file my ITR", "which
  ITR form", "ITR-1 / ITR-2", "check my ITR", "reconcile AIS/26AS/TIS", "review my
  tax return", "help with Form 67 / Schedule FA / Schedule CG / Schedule AL /
  capital gains / FTC / 54F / 87A rebate", or shares tax documents (Form 16, AIS,
  TIS, 26AS, 1042-S, broker P&L, MF capital-gains statements). Covers AY 2026-27
  (FY 2025-26) onward. NOT for US tax filing, and NOT for business/professional
  income (ITR-3/ITR-4).
---

# File ITR-1 / ITR-2 (Indian individual returns)

Advisory workflow only — always remind the user to get a CA sign-off before filing,
especially for foreign income / Schedule FA / FTC. Never store PAN, Aadhaar, or bank
account numbers in this repo. **First pick the correct form (section 0.5), then follow
the intake and reconciliation.**

## 0. Intake — ask for prerequisites FIRST

Before computing or editing anything, **run an intake**: ask the user which documents
they already have vs. still need to fetch, using the **section 1 checklist**. Do NOT
assume the data is available.

1. Confirm the **year**: AY (e.g. 2026-27) and the FY it covers (2025-26).
2. Ask for / confirm each source in **section 1** (Form 16, AIS, TIS, 26AS, 1042-S x2,
   broker P&L + holdings, KFintech + CAMS CG, bank interest, property/26QB, home loan).
3. Ask the **scope questions** that change the return:
   - Any **foreign shares/RSU/ESPP** sold or held this year? (Schedule FA + foreign CG)
   - Any **property** bought/sold ≥ ₹50L? (194IA/26QB, or 54F reinvestment)
   - Total income likely **> ₹50L**? (Schedule AL becomes mandatory)
   - **LRS remittances** > ₹7L / any TCS? (Schedule TCS)
   - New vs old **regime** preference (or compute both).
4. Note what's **missing** and list it back to the user before proceeding; only start
   reconciliation (section 2) once the required inputs are in hand.
5. Reuse prior-year working files and the session store before
   re-deriving anything (see section 6).

## 0.5 Choose the right form (ITR-1 vs ITR-2) FIRST

Decide the form before intake — it changes which schedules exist. Default to the
**simplest form the taxpayer is eligible for**.

**ITR-1 (Sahaj) — allowed ONLY if ALL hold (AY 2026-27):**
- **Resident and ordinarily resident** (not NR / RNOR).
- **Total income ≤ ₹50 lakh.**
- Income only from: **salary/pension**, **ONE house property** (no brought-forward loss),
  **other sources** (interest, dividend, family pension), and **agricultural income ≤ ₹5,000**.
- **New for AY 2026-27:** **LTCG u/s §112A up to ₹1.25 lakh** is allowed in ITR-1,
  **provided there is no brought-forward / carry-forward capital loss.**

**Must use ITR-2 instead if ANY apply:** capital gains beyond the ₹1.25L §112A allowance
(any STCG, any §112, debt/§50AA, foreign-share CG); **more than one house property**;
**any foreign asset/income** (Schedule FA) or foreign dividends/FTC; **RSU/ESPP / unlisted
shares / director** in a company; agricultural income > ₹5,000; income taxable at special
rates (other than the small 112A allowance); **brought-forward or carry-forward losses**;
total income **> ₹50L** (Schedule AL); NR/RNOR residency; TDS u/s 194N; deferred ESOP tax.
(Business/professional income → ITR-3/ITR-4 — out of scope for this skill.)

**Worked example:** a senior citizen with income < ₹50L, only interest + dividend +
a small §112A LTCG well under ₹1.25L (no b/f loss) → **ITR-1 is permissible**; ITR-2 is
also valid. When both are allowed, either is fine — ITR-2 is the safe superset.

For an **ITR-1** return, follow intake/reconciliation but use only: salary/pension, one
house property, Schedule OS, the §112A LTCG field (if any), Chapter VI-A, and §87A rebate
(section 3a). **Skip** Schedule CG (full), FA, FTC/Form 67, and AL entirely.

## 1. Collect documents (checklist)

| Source | Document | Feeds into |
|---|---|---|
| Employer | **Form 16 Part B** | Salary, TDS, 80CCD(2), regime used |
| Income Tax portal | **AIS** + **TIS** (PDF, password = PAN lowercase + DOB ddmmyyyy) | Cross-check all income |
| TRACES / portal | **Form 26AS** | TDS/TCS credits, property TDS (Part VIII) |
| Broker custodians (e.g. Fidelity / E*TRADE) | **Form 1042-S** (per ticker) | Foreign dividend + FTC (25% withholding) |
| Broker custodians (e.g. Fidelity / E*TRADE) | Year-end holdings / lots (cost + peak + closing) | Schedule FA + foreign capital gains |
| Indian broker (e.g. Zerodha) | Tax P&L + **Holdings** (invested value) | Indian equity/MF CG + Schedule AL |
| Indian broker (e.g. Paytm Money) | Tax P&L (Equity + MF-Equity + MF-Debt) + Holdings | Indian equity/MF CG + Schedule AL |
| KFintech + CAMS | **Capital Gains statement — ALL folios, FY 01-Apr to 31-Mar** | MF capital gains (see gotcha #6) |
| Banks | Interest certificates (SB + FD) | Schedule OS |
| Property/builder | Sale deed, payment schedule, 26QB | Schedule AL + 194IA TDS |
| Home loan | Interest certificate (lender) | Old-regime §24(b) comparison only |

## 2. Reconciliation workflow

1. **Salary / TDS / TCS** → tie to **Form 16 + 26AS** exactly. Gross salary = 17(1) + perquisites (RSU). 80CCD(2) employer NPS carries to new regime.
2. **Interest, dividend, sale of securities, LRS** → tie to **AIS/TIS** processed totals (rupee-exact expected).
3. **Foreign dividends + FTC** → tie to **1042-S**. Check: `FTC ÷ foreign dividend = withholding rate` (25% for India-USA). Convert both income and tax at the same USD→INR rate.
4. **Capital gains** → build Schedule CG from broker + RTA statements. Verify total sale consideration = AIS "Sale of securities & MF".
5. **Schedule FA** → foreign custodial (Fidelity, E*TRADE) + per-lot foreign equity (MSFT, QCOM): cost, peak, closing, dividend.
6. **Form 67** → file BEFORE submitting the ITR (mandatory to keep FTC). Attach both 1042-S PDFs (Rule 128(8)(ii)).
7. **Schedule AL** → mandatory if total income > ₹50L.
8. **Regime** → compute new vs old; pick lower tax (see gotcha #1).

> **ITR-1 shortcut:** for an ITR-1 filer do only steps 1 (salary/TDS to Form 16+26AS)
> and 2 (interest/dividend to AIS/TIS), plus one house property and the §112A LTCG
> field if present. Steps 3–7 (foreign dividend/FTC, full Schedule CG, Schedule FA,
> Form 67, Schedule AL) do **not** exist in ITR-1 — skip them. Then apply the §87A
> rebate logic in section 3a.

## 3a. ITR-1 specifics (rebate, heads, regime)

- **§87A rebate (AY 2026-27):**
  - **New regime:** full rebate if **total income ≤ ₹12 lakh** — rebate up to **₹60,000**
    wipes out normal-slab tax. **Not available against §112A/§111A special-rate tax**, so
    a §112A LTCG above ₹1.25L is still taxed at 12.5% even if total income ≤ ₹12L.
  - **Old regime:** rebate if total income ≤ ₹5 lakh (up to ₹12,500).
- **Regime:** new regime is the default; opt out on the return itself. **No Form 10-IEA**
  is needed for ITR-1/ITR-2 (that form is only for taxpayers with business/professional
  income). Old regime unlocks 80C/80D/80TTA/80TTB/§24(b); new regime allows essentially
  only 80CCD(2)/80CCH/80JJAA.
- **Heads:** salary/pension (→ Form 16), **one** house property (§24(b) interest only in
  old regime; self-occupied loss capped at ₹2L), and Schedule OS (interest — split SB vs
  deposit; dividend with the quarterly break-up for 234C; family pension gets a 1/3
  deduction capped at ₹15,000).
- **80TTB** (senior citizen) up to ₹50,000 on interest, or **80TTA** up to ₹10,000 on
  savings interest — old regime only.
- **Verification:** salary/TDS = Form 16 + 26AS; interest/dividend = AIS/TIS. No CG-total,
  FA, FTC, or AL checks apply.
- **Offline JSON:** a **data-free** ITR-1 skeleton ships as `itr1_skeleton.json` (placeholders
  only). Fill it, set `NewTaxRegime`, populate the §112A field if the schema exposes it,
  remove the `_template_note`/`_note_112A` keys, and **validate against the official ITR-1
  schema / offline utility** before upload — field names can change year to year.

## 3. Key rules & gotchas (learned)

1. **Regime choice is yours, not the employer's.** Form 16 may use OLD regime for TDS; you can file NEW. At high income (e.g. > ₹1cr) the NEW regime usually wins (lower graduated slabs beat old-regime deductions) even with 80C/80CCD(1B)/80D/home-loan interest. Always compute both.
2. **§111A vs §50AA.** Equity-oriented MF (≥65% Indian equity, STT paid) + listed equity short-term → **§111A @ 20%**. Money-market / debt funds (e.g. JioBlackRock) → **§50AA slab rate**, always short-term, go in CG "other assets", NOT §111A. "Mutual fund" alone doesn't mean §111A.
3. **Foreign shares** (MSFT/QCOM): short-term → CG "other assets" (item 5, applicable/slab); long-term → CG "assets where B1-B7 not applicable" (item 8, 12.5%, no indexation for transfers on/after 23-Jul-2024). Long-term threshold for foreign shares = 24 months.
4. **FTC / Form 67**: file before the return; FSI income = TR relief = Sec 90 = ₹ claimed; ratio = 25%.
5. **Table F (accrual of CG) must equal BFLA item 3vii** for the LTCG 12.5% line, split by quarter of sale (most equity sold Jan-Mar → Q4 "16/12-15/3").
6. **AIS "Sale of MF (RTA)" includes ALL folios**, including DIRECT folios not routed through your broker. Pull the KFintech AND CAMS capital-gains statements for **all** folios (each folio number separately) — a direct folio can be missing from the broker P&L and cause an AIS mismatch. Report ACTUAL gains, not the (sometimes inflated) AIS figure, but reconcile the difference.
7. **Schedule AL** = **cost** as on 31-Mar. Shares/securities = foreign shares at cost (sum of InitialValOfInvstmnt from Schedule FA) + Indian holdings invested value (from your Indian brokers). **Health/term insurance are NOT assets** (no surrender value). Company-leased car is NOT your asset. Co-owned property → your % share only. Under-construction property → full cost as asset, unpaid balance as liability. **Timing: report only what you OWN/paid on or before 31-Mar.** A house purchased or paid *after* FY-end (e.g. a 54F house bought in Jun after a Mar year-end) is NOT in this year's AL — it belongs to next year's; only installments actually paid on/before 31-Mar count.
8. **Property purchase ≥ ₹50L → you (buyer) must deduct 1% TDS u/s 194IA**, file **Form 26QB within 30 days** of end of payment month, issue **Form 16B**. Late = ₹200/day (234E) + interest (201(1A)). **If seller is NRI → Section 195 instead (TAN, 27Q, ~20%+)** — very different. TDS you deduct as buyer is NOT claimed in your own ITR.
9. **54F** exempts LTCG (from asset other than a residential house — shares qualify, incl. foreign shares) if the **net sale consideration** is reinvested in **ONE residential house in India** within 1yr before / 2yr after (or construct in 3yr), owning ≤1 other residential house on the sale date. **Commercial property does NOT qualify.** Cap ₹10cr.
10. **Dividend quarterly break-up** in Schedule OS must sum to total dividend, or validation fails.
11. **Schedule FA is CALENDAR-year (1-Jan–31-Dec), NOT financial-year** — unlike Schedule CG (FY). So a lot sold 21-Mar-2025 is disclosed in *this* year's FA but its capital gain belongs to *last* year's (AY 2025-26) Schedule CG. FA and CG proceeds are NOT expected to tie.
12. **FA Table A2 (custodial) has NO gross-proceeds field** — only peak/closing/dividend. **Table A3 (foreign equity) HAS "Total gross proceeds from sale/redemption".** Report each SOLD lot as its own A3 row with `ClosingBalance=0` + gross proceeds filled; keep the dividend/peak rows for still-held lots separate.
13. **Broker year-end holdings snapshots exclude already-sold lots** (they're a point-in-time-after-31-Dec view). Add sold lots to A3 manually from the G&L / realized-gains statement — don't assume the holdings export is complete.
14. **54F with multiple sale dates:** a single representative `DateofTransfer` (with total AmtDeducted covering the whole exempt gain) is accepted, provided the house purchase falls within the 1yr-before / 2yr-after window for each transfer.

## 4. Common validation errors → fixes

| Error | Fix |
|---|---|
| Flat/Door/Block No > 50 chars | Shorten `ResidenceNo` (put rest in ResidenceName/RoadOrStreet) |
| Secondary address option | Set `SecondaryAdd=Y` + fill AlternateAddress |
| "Table F Sl.5 quarters ≠ BFLA 3vii" | Enter LTCG 12.5% amount in the sale quarter of Table F |
| "Select option in Schedule AL" | Fill Schedule AL (mandatory when income > ₹50L) |

## 5. Verification (before filing)

- Salary, TDS, TCS = Form 16 + 26AS (exact)
- Interest, dividend, securities, LRS = AIS/TIS (exact; foreign dividends NOT in AIS)
- Foreign dividend/FTC = 1042-S (ratio 25%)
- CG total consideration = AIS securities line (± small load/rounding)
- Table F = BFLA 3vii; FSI = TR = Sec 90
- Schedule AL complete; Form 67 filed (save ack no.)
- Then: Preview → Validation (0 errors) → Submit → **e-Verify** (Aadhaar OTP/EVC)

**Offline JSON:** data-free skeletons ship as `itr1_skeleton.json` and `itr2_skeleton.json`
(placeholders + 0 amounts). Fill values, set the regime flag (`OptOutNewTaxRegime` for ITR-2),
add Schedule112A rows for CG, remove the `_template_note`/`_note_*` keys, and **validate
against the official schema / offline utility** before upload — field names change year to year.

## 6. Reusable helpers

Read broker xlsx with `openpyxl` (`data_only=True`). A scrubbed, reusable FX/price
engine ships with this skill as `schedule_fa.py` (rate loaders, `_rate_for`,
`peak_inr_for_lot`) — **no personal data**. The per-ticker sale/dividend tables and
data CSVs (`sbi_usd.csv`, `<ticker>.csv`) are **user-supplied** (see section 7).

`fetch_data.py` (stdlib-only, optional) auto-downloads the two machine-fetchable
inputs: SBI TT rates from the `sahilgupta/sbi-fx-ratekeeper` GitHub repo -> `sbi_usd.csv`,
and daily prices (Stooq, falling back to the Yahoo Finance chart API) -> `<ticker>.csv`,
written in the exact loader format. Run `python fetch_data.py --tickers msft qcom intc`.
If network access is blocked, fall back to the manual steps in section 7. `rbi_ref.csv`
stays user-maintained.

## 7. FX rate & price-history sourcing (SBI TT + MSFT peak)

**Why:** Schedule FA / foreign CG must convert USD→INR at the **SBI TT buying rate**
on each relevant date (Explanation to Rule 26; SBI TTBR is the Schedule FA reference).
The "peak balance during the period" needs a **daily price series** to find the true
intra-year high, not just the closing price.

### 7a. SBI TT buying rate history → `sbi_usd.csv` (or consolidated `usd_inr.csv`)

> **Preferred single source:** a consolidated **`usd_inr.csv`** (columns
> `date, tt_buy, tt_sell, source`) can replace the two-file setup. `schedule_fa.py`
> loads it first via `load_usd_inr` (reads `tt_buy`); if it is absent it falls back to
> `rbi_ref.csv` (overrides) + `sbi_usd.csv`. The `source` column marks each row as
> authoritative (`SBI_TTBUY`) or an estimate (`xls_mid-0.425`, `ECB-0.39`).
1. Source: **`sahilgupta/sbi-fx-ratekeeper`** on GitHub — download **`SBI_REFERENCE_RATES_USD.csv`**
   (it aggregates SBI's daily reference-rate PDFs). Save it as `schedule_fa/sbi_usd.csv`.
2. Columns used: **`DATE`** and **`TT BUY`** (ignore TT SELL / bill rates). Loader
   (`load_sbi_ttbr` in `schedule_fa.py`) reads `TT BUY`, strips commas, and **skips
   rows where the value is `0.00`** (SBI leaves 0 on non-publish days).
3. **Working-day rule:** for a date SBI didn't publish (Sun / bank holiday), use the
   **nearest prior published rate** — `_rate_on_or_before(iso)` picks `max(date ≤ iso)`.
4. **Manual overrides / pre-dataset dates:** `rbi_ref.csv` (simple `date,rate` CSV,
   `#` comments allowed) is merged in and takes precedence. For dates *before* the
   ratekeeper dataset begins (e.g. a 2019 vest), the ratekeeper has no row — supply a
   **user-confirmed rate** via an override dict (e.g. `QCOM_RATE_OVERRIDE["2019-08-19"]=71.765`)
   or an `rbi_ref.csv` line. Any row that fell back to `FALLBACK_RATE` must be flagged
   and fixed before filing.
5. Access in code: `schedule_fa._rate_for(iso_date)` returns the rate for any ISO date
   (exact → nearest-prior → fallback).
6. **Pre-2020 / SBI-outage backfill (estimates):** the SBI ratekeeper dataset only starts
   **2020-01-06**, and has multi-day non-publish gaps (e.g. COVID Apr–Jun 2020, Aug 2021).
   To fill those in `rbi_ref.csv` / `usd_inr.csv`, both methods below are **calibrated to
   actual SBI TT BUY** and give an estimated TT BUY (flag as estimates, prefer the exact
   SBI PDF for a filed date):
   - **From an SBI TT *mid* export** (e.g. a bank's INR/USD sheet): `TT BUY ≈ mid − 0.425`
     (SBI applies a fixed ~₹0.85 TT buy/sell spread; half = 0.425).
   - **From the ECB reference rate** (free, no key, daily back to 1999) via
     `https://api.frankfurter.app/<start>..<end>?base=USD&symbols=INR`:
     `TT BUY ≈ ECB − 0.39` (median `SBI_TTBUY − ECB = −0.393` over 185 overlapping 2020 days).
     Fill only genuine **multi-day outages**; leave 1–2 day holidays to the working-day rule.
   `tt_sell` for an estimated row = `tt_buy + 0.85`.
7. **10-year range:** also pull **USD/INR daily history for the last 10 years** from
   investing.com (Currencies → USD/INR → Historical Data → set range ~10y, export CSV).
   Use it as a **cross-check / fallback** for acquisition dates that predate the SBI
   ratekeeper dataset (older vests). Note: the **SBI TT buying rate stays authoritative**
   for filing — investing.com's interbank USD/INR is only a sanity check / last-resort fill
   when no SBI rate exists, and any such row must be flagged.

### 7b. MSFT (and any ticker) daily price history → `msft.csv`
1. Source: an **investing.com "Historical Data" export** for MSFT (or Yahoo Finance) —
   columns `Date, Price, Open, High, Low, ...`. Save as `schedule_fa/msft.csv`.
   Cover the whole reporting window (**CY 1-Jan → 31-Dec** for Schedule FA).
2. Loader `load_msft_series` reads `Date` + **`Price`** (daily close), comma-stripped.
3. **Peak computation** (`peak_inr_for_lot`): for each trading day the lot is held in
   `[max(acq, 01-Jan) .. end]` (end = sale date for sold lots, else 31-Dec), value =
   `qty × close_USD[day] × SBI_TT[day]`; the **maximum** value and its date are the peak.
   This gives the correct INR peak (price-high and FX-high can fall on different days).
4. Closing value = `qty × close_USD[31-Dec] × SBI_TT[31-Dec]`; initial value =
   `qty × price_at_acq × SBI_TT[acq]`.
5. Same pattern works for QCOM/CDNS — just swap the price CSV; keep one `sbi_usd.csv`
   shared across all tickers.
6. **10-year range:** on investing.com set the Historical Data range to the **last 10
   years** (Equities → MSFT → Historical Data → ~10y → export CSV) so every past vest /
   acquisition date has a price. Downloading the full 10y once avoids re-pulling each year.

### 7c. QCOM daily price history → `qcom.csv`
1. Ticker **`QCOM`** (QUALCOMM Incorporated), custodian **E*TRADE from Morgan Stanley**.
2. Source: **investing.com "Historical Data"** for QCOM (or Yahoo Finance) — same
   `Date, Price, Open, High, Low, ...` layout. Save as `schedule_fa/qcom.csv`,
   covering the full **CY 1-Jan → 31-Dec** window.
3. Reuse the identical loader/peak logic (`load_msft_series`-style + `peak_inr_for_lot`):
   value = `qty × QCOM_close_USD[day] × SBI_TT[day]`; max over held days = peak.
4. **Pre-dataset acquisitions:** QCOM has old RSU/ESPP vests (e.g. 2019) that predate the
   SBI ratekeeper coverage — supply the SBI TT rate via `QCOM_RATE_OVERRIDE`
   (e.g. `"2019-08-19": 71.765`) or an `rbi_ref.csv` line. Cross-check E*TRADE 1042-S for
   dividends and the G&L / realized-gains export for sold lots (holdings snapshot omits them).
5. **10-year range:** on investing.com set the QCOM Historical Data range to the **last 10
   years** and export once, so all old vest dates are covered without re-pulling.

### 7d. Intel daily price history → `intel.csv`
1. Ticker **`INTC`** (Intel Corporation). Custodian depends on the plan (E*TRADE / Fidelity /
   Computershare) — confirm from the broker statement.
2. Source: **investing.com "Historical Data"** for INTC (or Yahoo Finance) — same
   `Date, Price, Open, High, Low, ...` layout. Save as `schedule_fa/intel.csv`,
   covering the full **CY 1-Jan → 31-Dec** window.
3. Reuse the identical loader/peak logic: value = `qty × INTC_close_USD[day] × SBI_TT[day]`;
   max over held days = peak; closing = `qty × close[31-Dec] × SBI_TT[31-Dec]`.
4. Same `sbi_usd.csv` and `_rate_for()` as all other tickers; add rate overrides only for
   acquisition dates that predate the ratekeeper dataset.
5. **10-year range:** on investing.com set the INTC Historical Data range to the **last 10
   years** and export once, so all past vest / acquisition dates have a price.
