#!/usr/bin/env python3
"""
Optional data fetcher for the file-itr Schedule FA engine.

Downloads the two machine-fetchable inputs used by schedule_fa.py, writing them
in exactly the CSV shape the loaders expect (no personal data involved):

  * sbi_usd.csv   SBI TT-buying reference rates (USD->INR) from the public
                  `sahilgupta/sbi-fx-ratekeeper` GitHub repo (columns DATE, TT BUY, ...).
  * <ticker>.csv  Daily close prices from Stooq (free, no API key), written with
                  columns Date, Price, Open, High, Low  (Price = daily Close).

Notes / limits:
  - investing.com has no clean API; Stooq is used instead as a free equivalent.
    The SBI TT rate stays authoritative for filing; treat prices as the peak input.
  - rbi_ref.csv (manual overrides / pre-dataset dates) stays user-maintained.
  - Network access is required; in restricted environments these downloads may
    fail — fall back to the manual steps in SKILL.md section 7.

Examples:
  python fetch_data.py                      # SBI rates + MSFT, QCOM, INTC
  python fetch_data.py --tickers msft aapl  # SBI rates + chosen tickers
  python fetch_data.py --no-sbi --tickers qcom
"""

import argparse
import csv
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_BASE = Path(__file__).resolve().parent
_UA = {"User-Agent": "Mozilla/5.0 (file-itr fetch_data.py)"}

# Candidate raw URLs for the SBI ratekeeper USD reference-rate CSV (repo layout
# has moved before; the first that resolves is used).
SBI_URLS = (
    "https://raw.githubusercontent.com/sahilgupta/sbi-fx-ratekeeper/main/csv_files/SBI_REFERENCE_RATES_USD.csv",
    "https://raw.githubusercontent.com/sahilgupta/sbi-fx-ratekeeper/master/csv_files/SBI_REFERENCE_RATES_USD.csv",
    "https://raw.githubusercontent.com/sahilgupta/sbi-fx-ratekeeper/main/SBI_REFERENCE_RATES_USD.csv",
)

# Stooq daily-history CSV endpoint. US tickers need a ".us" suffix.
STOOQ_URL = "https://stooq.com/q/d/l/?s={sym}&i=d"

# Yahoo Finance chart endpoint (JSON, no API key/crumb) used as a fallback.
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=10y&interval=1d"


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_sbi(out_dir: Path) -> bool:
    """Download the SBI TT-buying reference-rate CSV -> sbi_usd.csv (raw)."""
    for url in SBI_URLS:
        try:
            data = _get(url)
        except Exception as e:  # noqa: BLE001 - report and try next candidate
            print(f"  SBI: {url} failed ({e})")
            continue
        text = data.decode("utf-8-sig", errors="replace")
        header = text.splitlines()[0] if text else ""
        if "TT BUY" not in header or "DATE" not in header.upper():
            print(f"  SBI: unexpected header from {url!r}: {header[:80]!r}")
            continue
        out = out_dir / "sbi_usd.csv"
        out.write_text(text, encoding="utf-8")
        rows = max(0, len(text.splitlines()) - 1)
        print(f"  SBI: wrote {out.name} ({rows} rows) from {url}")
        return True
    print("  SBI: all sources failed - use SKILL.md 7a manual steps.")
    return False


def _stooq_symbol(ticker: str) -> str:
    t = ticker.strip().lower()
    return t if "." in t else f"{t}.us"


def _rows_from_stooq(ticker: str):
    """Yield (Date, Close, Open, High, Low) rows from Stooq, or None on failure."""
    sym = _stooq_symbol(ticker)
    try:
        text = _get(STOOQ_URL.format(sym=sym)).decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        print(f"  {ticker}: Stooq download failed ({e})")
        return None
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "Close" not in reader.fieldnames:
        # Stooq returns HTML / "N/A" for unknown symbols, rate limits, or proxies.
        print(f"  {ticker}: Stooq gave no data for {sym!r}")
        return None
    rows = [(r.get("Date", ""), (r.get("Close") or "").strip(),
             r.get("Open", ""), r.get("High", ""), r.get("Low", ""))
            for r in reader if (r.get("Close") or "").strip()]
    return rows or None


def _rows_from_yahoo(ticker: str):
    """Yield (Date, Close, Open, High, Low) rows from Yahoo chart JSON, or None."""
    sym = ticker.strip().upper()
    try:
        payload = json.loads(_get(YAHOO_URL.format(sym=sym)).decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"  {ticker}: Yahoo download failed ({e})")
        return None
    try:
        res = payload["chart"]["result"][0]
        ts = res["timestamp"]
        q = res["indicators"]["quote"][0]
    except (KeyError, IndexError, TypeError):
        print(f"  {ticker}: Yahoo returned no series for {sym!r}")
        return None
    rows = []
    for i, epoch in enumerate(ts):
        close = q.get("close", [None] * len(ts))[i]
        if close is None:
            continue
        d = datetime.fromtimestamp(epoch, tz=timezone.utc).date().isoformat()
        rows.append((d, f"{close:.4f}",
                     _fmt(q, "open", i), _fmt(q, "high", i), _fmt(q, "low", i)))
    return rows or None


def _fmt(q: dict, key: str, i: int) -> str:
    v = q.get(key, [None])[i] if i < len(q.get(key, [])) else None
    return f"{v:.4f}" if isinstance(v, (int, float)) else ""


def fetch_ticker(ticker: str, out_dir: Path) -> bool:
    """Download daily prices -> <ticker>.csv (Date, Price, Open, High, Low).
    Tries Stooq first, then falls back to the Yahoo Finance chart API."""
    rows = _rows_from_stooq(ticker)
    source = "Stooq"
    if not rows:
        rows = _rows_from_yahoo(ticker)
        source = "Yahoo"
    if not rows:
        print(f"  {ticker}: no price data from any source - use SKILL.md 7b manual steps.")
        return False
    out = out_dir / f"{ticker.strip().lower()}.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Price", "Open", "High", "Low"])
        w.writerows(rows)
    print(f"  {ticker}: wrote {out.name} ({len(rows)} rows) from {source}")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fetch SBI TT rates + ticker prices for schedule_fa.py")
    ap.add_argument("--tickers", nargs="*", default=["msft", "qcom", "intc"],
                    help="ticker symbols (default: msft qcom intc)")
    ap.add_argument("--out-dir", type=Path, default=_BASE,
                    help="destination directory (default: this script's folder)")
    ap.add_argument("--no-sbi", action="store_true", help="skip the SBI rate download")
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ok = True

    if not args.no_sbi:
        print("SBI TT buying rates:")
        ok &= fetch_sbi(args.out_dir)

    if args.tickers:
        print("Ticker prices:")
        for t in args.tickers:
            ok &= fetch_ticker(t, args.out_dir)

    print("Done." if ok else "Done (with some failures - see messages above).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
