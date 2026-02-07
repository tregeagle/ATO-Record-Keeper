# YFinance Ignore Configuration

## What This Does

When you run `make all`, the build process tries to download current stock prices from Yahoo Finance for all your holdings. Some tickers may fail for various reasons:

- **Delisted**: ZFX (Zinifex), DES (Desc)
- **No historical data**: Some stocks from very early dates
- **Future dates**: 2026 holdings can't be priced yet since we're in February 2026
- **Data gaps**: Some ETFs may have missing data

Instead of crashing, the system now:
1. ✓ Silently skips ignored tickers
2. ✓ Logs which tickers failed to download
3. ✓ Completes the report generation successfully
4. ✓ Excludes ignored holdings from the index value calculation

## The Ignore File

**Location**: `.yfinance_ignore` (in the project root)

**Format**:
```
# Comments start with #
TICKER1    # Optional comment explaining why
TICKER2
TICKER3
```

## Current Configuration

```
ZFX       # Zinifex - delisted (2008)
DES       # Desc - delisted/unavailable
```

These 2 tickers are configured to be skipped during price downloads.

## How It Affects Your Reports

### Capital Gains Tax Reports ✓ UNAFFECTED
The FIFO calculator (`fifo_calculator.py`) does **NOT** use yfinance. It uses your actual trade data to calculate capital gains. Ignored tickers still appear in your tax reports because they're needed for cost basis matching.

Example: If you sold 100 ZFX shares, that sale will appear in your capital gains report even though ZFX is in the ignore list.

### Index/Holdings Values ✗ AFFECTED
The index page shows "Holdings Value" - the current value of shares you own. Ignored tickers won't contribute to this calculation, so the total will be lower.

**This is OK because:**
- You sold these shares years ago (ZFX, DES)
- Or they're future dates (2026) with no price data yet
- The tax reports (what matters) are completely accurate

## Adding More Tickers

If you see errors when running `make all`, edit `.yfinance_ignore` and add the problematic ticker:

```bash
# Edit the file
nano .yfinance_ignore

# Add the ticker (uppercase)
ZFX       # Delisted
DES       # Delisted
CBA       # If this keeps failing
```

Then run:
```bash
make all
```

## Common Issues

### "make all" still shows yfinance errors?
- The script will log warnings but still complete successfully
- This is expected for delisted stocks and future dates
- You can add those tickers to `.yfinance_ignore` to suppress the warnings

### CBA showing as failed in 2026?
- This is normal - we're in February 2026, so June 2026 prices don't exist yet
- Add `CBA` to the ignore file if you want to suppress the warning
- By June 2026, it will work automatically

### My tax reports look wrong?
- Check that you're NOT ignoring active tickers (VAS, VGS, GOLD, IEM, IAF)
- Tax reports use trade data, not yfinance - they're unaffected by the ignore list
- Run `python trades/scripts/fifo_calculator.py --year 2025` to verify

## Testing

Run the build and check for errors:
```bash
make clean
make all 2>&1 | grep "⚠"
```

This shows which tickers had price download issues. Add any delisted stocks to the ignore file.

## Technical Details

The ignore list is loaded in `trades/scripts/generate_index.py` and used to:

1. Skip calling yfinance for ignored tickers
2. Remove ignored holdings from the index page holdings calculations
3. Continue processing without crashing

The FIFO calculator is independent and unaffected.
