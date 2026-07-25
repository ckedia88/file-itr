#!/usr/bin/env python3
"""
Reusable FX-rate + price-peak engine for India Schedule FA / foreign capital gains.

This is a SCRUBBED, DATA-FREE engine intended for distribution. It contains NO
personal financial data — only generic loaders and conversion helpers. Supply
your own data files (all optional; missing files degrade gracefully):

  - usd_inr.csv     Consolidated USD->INR SBI TT rates (columns: date, tt_buy,
                    tt_sell, source). Preferred single source when present; merges
                    authoritative SBI TT BUY with pre-2020 / outage estimates.
  - sbi_usd.csv     SBI TT-buying reference rates (USD->INR). Export
                    SBI_REFERENCE_RATES_USD.csv from the public
                    `sahilgupta/sbi-fx-ratekeeper` repo. Columns: DATE, TT BUY, ...
                    Used as a fallback when usd_inr.csv is absent.
  - rbi_ref.csv     Optional manual overrides, simple `date,rate` CSV (# comments ok).
                    Takes precedence over sbi_usd.csv (use for pre-dataset dates).
  - <ticker>.csv    Daily close price (USD) for a ticker, investing.com / Yahoo
                    "Historical Data" export. Columns: Date, Price, Open, High, ...

Reporting window for Schedule FA is the CALENDAR year (01-Jan .. 31-Dec).
See the skill's section 7 for the full sourcing steps.
"""

import csv
from datetime import date, datetime
from pathlib import Path

RATE_SOURCE_LABEL = "SBI TT buying rate"
WH_RATE = 0.25                        # US non-resident-alien dividend withholding

# Default calendar-year reporting window (override per assessment year as needed).
PERIOD_START = date(2025, 1, 1)
PERIOD_END = date(2025, 12, 31)

_BASE = Path(__file__).resolve().parent

_DATE_FORMATS = ("%Y-%m-%d", "%d %B %Y", "%d-%b-%Y", "%d/%m/%Y",
                 "%d-%b-%y", "%d %b %Y", "%d-%m-%Y", "%m/%d/%Y")


def _to_iso(s: str):
    """Best-effort parse of a date string to an ISO 'YYYY-MM-DD' string."""
    if not s or not s.strip():
        return None
    s = s.strip().split()[0]          # drop any trailing time component
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def load_simple_rates(path: Path) -> dict:
    """Parse a simple 'date,rate' CSV (comment lines starting with '#' allowed)."""
    rates = {}
    if not path.exists():
        return rates
    with path.open(newline="") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip() or row[0].lstrip().startswith("#"):
                continue
            if row[0].strip().lower() == "date":
                continue
            iso = _to_iso(row[0])
            val = row[1].strip() if len(row) > 1 else ""
            if iso and val:
                rates[iso] = float(val.replace(",", ""))
    return rates


def load_sbi_ttbr(path: Path) -> dict:
    """Parse SBI_REFERENCE_RATES_USD.csv; use the 'TT BUY' column.
    Rows where TT BUY is 0.00 (non-publish days) are skipped."""
    rates = {}
    if not path.exists():
        return rates
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            iso = _to_iso(row.get("DATE", ""))
            raw = (row.get("TT BUY") or "").strip()
            if not iso or not raw:
                continue
            try:
                val = float(raw.replace(",", ""))
            except ValueError:
                continue
            if val > 0:                # last row for a date wins
                rates[iso] = val
    return rates


def load_usd_inr(path: Path) -> dict:
    """Parse the consolidated usd_inr.csv (columns: date, tt_buy, tt_sell, source);
    use the 'tt_buy' column. Comment lines starting with '#' are skipped."""
    rates = {}
    if not path.exists():
        return rates
    with path.open(newline="") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if not row or not row[0].strip() or row[0].lstrip().startswith("#"):
                continue
            if header is None:
                header = [c.strip().lower() for c in row]
                continue
            rec = dict(zip(header, row))
            iso = _to_iso(rec.get("date", ""))
            raw = (rec.get("tt_buy") or "").strip().replace(",", "")
            if not iso or not raw:
                continue
            try:
                val = float(raw)
            except ValueError:
                continue
            if val > 0:
                rates[iso] = val
    return rates


def load_price_series(path: Path) -> dict:
    """Daily close price (USD) by ISO date from an investing.com-style CSV
    (columns: Date, Price, Open, High, Low, ...)."""
    series = {}
    if not path.exists():
        return series
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            iso = _to_iso(row.get("Date", ""))
            raw = (row.get("Price") or "").strip().replace(",", "")
            if not iso or not raw:
                continue
            try:
                series[iso] = float(raw)
            except ValueError:
                pass
    return series


# Primary source: the consolidated usd_inr.csv (SBI TT BUY + pre-2020/outage estimates).
# If it is absent, fall back to the two-file setup (rbi_ref.csv overrides sbi_usd.csv).
FX_RATES = load_usd_inr(_BASE / "usd_inr.csv") or {
    **load_simple_rates(_BASE / "rbi_ref.csv"),
    **load_sbi_ttbr(_BASE / "sbi_usd.csv"),
}

# Fallback used (and should be flagged) only when no rate at/before a date exists.
FALLBACK_RATE = FX_RATES.get(PERIOD_END.isoformat(), 89.47)


def _rate_on_or_before(iso: str):
    """Nearest published reference rate on/before a date (working-day rule)."""
    candidates = [d for d in FX_RATES if d <= iso]
    return FX_RATES[max(candidates)] if candidates else None


def _rate_for(iso: str) -> float:
    """SBI TT rate for an ISO date: exact -> nearest-prior -> fallback."""
    return FX_RATES.get(iso) or _rate_on_or_before(iso) or FALLBACK_RATE


def peak_inr_for_lot(qty: float, acq: date, series: dict,
                     start: date = PERIOD_START, end: date = PERIOD_END):
    """Highest daily holding value in INR while the lot is held in the window.
    For each trading day in [max(acq, start) .. end] value = qty * close_USD[day]
    * SBI_TT[day]; returns (best_value_inr, best_iso_date) or (None, None)."""
    lo = max(acq, start)
    best_val, best_iso = None, None
    for iso, price in series.items():
        y, m, d = (int(x) for x in iso.split("-"))
        day = date(y, m, d)
        if lo <= day <= end:
            val = qty * price * _rate_for(iso)
            if best_val is None or val > best_val:
                best_val, best_iso = val, iso
    return best_val, best_iso


_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}


def parse_date(s: str) -> date:
    """Parse a 'Mon-DD-YYYY' style date (e.g. broker lot dates)."""
    mon, day, year = s.split("-")
    return date(int(year), _MONTHS[mon[:3].title()], int(day))
