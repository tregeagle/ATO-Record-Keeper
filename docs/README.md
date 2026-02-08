
# Intro

Reporting on capital gains when selling shares can be a nightmare. All those boring little DRP and Buy transactions add up over a few decades. 

I tried recording stuff in paper notebooks, spreadsheets and eventually using Sharesight to shortcut the work. I really distrust subscription businesses. I would rather control my own data. Last Friday I used Claude (a subscription. Oh, the irony) to bolt together this thing.

# ATO Record Keeper

Create ATO-compliant capital gains reports with a general record of your progress over time.

 - Imports: Save your contract notes and other evidence
 - Input/YYYY: Create a simple reference for each transaction
 - Output: A lifetime overview along with annual reports in markdown and html

## Quick Start

Copy your contract notes, and other evidence to the /import directory.
use /input/template.md to create simple trade records in YYYY directories.

```bash
make setup                                  # install requirements
make all                                    # generate all reports
```
Reports are generated in /output

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
