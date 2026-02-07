		# Trade Tracking & ATO Tax Reporting

One markdown file per trade, FIFO cost basis calculation, ATO-compliant capital gains reports.

## Quick Start

```bash
make all                                    # generate all reports
python scripts/fifo_calculator.py --year 2025   # single year report
```

Reports are output to `output/html/` and `output/markdown/`.

## Adding a Trade

```bash
cp input/template.md input/2026/2026-02-15-buy-vas.md
# Edit the YAML fields, then:
make all
```

### Trade File Format

```yaml
---
date: 2026-02-15
time: 10:30
action: buy
ticker: VAS
quantity: 10
price: 94.50
value: 945.00
fee: 6.50
contract_note: 2026-02-15-buy-vas.pdf
---
```

File naming: `YYYY-MM-DD-ACTION-TICKER.md`

## Project Layout

```
input/                  Trade data (one .md per trade, by year)
input/template.md       Template for new trades
imports/contract-notes/ Broker contract note PDFs
scripts/                fifo_calculator.py, generate_index.py, holdings_value.py
output/html/            Generated HTML reports + index
output/markdown/        Generated markdown reports
```

## Tax Reports

Reports include:
- Capital gains/losses with FIFO lot matching
- 50% CGT discount for assets held >12 months
- Net capital gain for ATO label 18A
- Complete buy/sell transaction list with fees

ATO tax year = 1 Jul to 30 Jun (e.g. `--year 2025` = FY 2024-25).

## Notes

- Buy and sell brokerage fees are included in cost base
- Dividend income is not tracked (report separately)
- Pre-2021 trade data is incomplete
