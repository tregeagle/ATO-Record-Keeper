# ATO Capital Gains Tax Reporting

Simple guide for generating capital gains reports for Australian tax purposes.

## Overview

This system tracks your investment trades and calculates capital gains/losses using the **FIFO (First-In-First-Out) method**, which is ATO-compliant.

## Generate Your Tax Report

### For a Specific Tax Year

```bash
cd /home/ruben/Projects/risk
python trades/scripts/fifo_calculator.py --year 2025
```

Output shows:
- Total capital gains
- Total capital losses
- Net capital gain/loss
- Detailed breakdown by sale with lot matching

### For a Specific Ticker

```bash
python trades/scripts/fifo_calculator.py --ticker VAS
```

### All-Time Gains

```bash
python trades/scripts/fifo_calculator.py
```

## Report Format

The output is markdown formatted with:

1. **Summary** - Total gains, losses, net position
2. **By Ticker** - Summary for each holding
3. **Detailed Records** - Table of each sale with:
   - Date sold
   - Quantity
   - Cost per unit
   - Sale price
   - Cost basis
   - Proceeds
   - Capital gain/loss

4. **Detailed Breakdown** - By acquisition lot with:
   - Date acquired
   - Purchase price
   - Date sold
   - Sale price
   - Capital gain/loss

## FIFO Method

The calculator uses First-In-First-Out cost basis matching:

- Oldest purchases matched first against sales
- Each sale shows which purchase lots were sold
- Generates per-lot capital gains/losses
- ATO-compliant methodology

## Data Quality

**Complete data:**
- 2021-2025 buy/sell transactions with quantity and price
- Accurate cost basis matching for FIFO

**Partial data:**
- Pre-2021 trades: Limited quantity data
- 2026 trades: May not have quantity/price yet

## Using the Report for Your Accountant

1. Run: `python trades/scripts/fifo_calculator.py --year [TAX_YEAR]`
2. Copy the markdown output or redirect to file:
   ```bash
   python trades/scripts/fifo_calculator.py --year 2025 > cgt_report_2025.md
   ```
3. Share the report with your accountant for lodgement

The report shows:
- Each sale transaction
- Cost basis calculated via FIFO matching
- Capital gain or loss per sale
- Total net position for the year

## Trade File Format

Each trade is stored as a simple markdown file with YAML metadata:

```yaml
---
date: 2026-02-04
time: 08:05
action: buy
ticker: IEM
quantity: 0
price: 0.00
value: 1283.85
fee: 0.00
---
```

Fields:
- `date`: Transaction date (YYYY-MM-DD)
- `time`: Transaction time (HH:MM)
- `action`: buy, sell
- `ticker`: Security symbol
- `quantity`: Units traded
- `price`: Price per unit
- `value`: Total transaction value
- `fee`: Brokerage fee

## Adding New Trades

Copy the template and edit:

```bash
cp trades/template.md trades/2026/2026-02-15-buy-vas.md
```

Edit the YAML and the trade will be included in future tax reports.

## Notes

- Only **capital gains/losses from sales** are reported
- **Deposits and withdrawals** are not taxable events
- **Brokerage fees** are included in cost basis
- **Dividend income** would need to be added separately (not tracked here)
- Reports generated in markdown format (easily convertible to PDF if needed)

---

For questions about how to apply these gains to your tax return, consult your accountant.
