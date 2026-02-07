# Trade Tracking System

A simple, markdown-based investment trade tracking system inspired by Makesite's philosophy: one markdown file per trade, YAML frontmatter for metadata, Python scripts for processing.

## Philosophy

This system prioritizes simplicity, maintainability, and readability:

- **One file per trade**: Easy to find, understand, and modify individual transactions
- **Plain text/markdown**: Future-proof, version-control friendly, no proprietary formats
- **YAML metadata**: Structured data for scripting and queries
- **Python scripts**: Simple, focused utilities for analysis and reporting
- **FIFO cost basis**: Tax-compliant accounting method for capital gains calculations

## Directory Structure

```
trades/
├── README.md                    (trade system documentation)
├── template.md                  (copy and customize for new trades)
├── 2020/                        (trades by year)
├── 2021/
├── 2022/
├── 2023/
├── 2024/
├── 2025/
├── 2026/
└── scripts/
    ├── import_pearler.py       (import from Pearler CSV)
    ├── summarize.py            (generate reports)
    └── fifo_calculator.py      (capital gains calculations)
```

## Trade File Format

Each trade is a markdown file with YAML frontmatter followed by markdown content.

### File Naming

Use the format: `YYYY-MM-DD-ACTION-TICKER.md`

Examples:
- `2026-02-04-buy-iem.md`
- `2026-02-02-deposit.md`
- `2025-12-12-sell-vas.md`

If multiple trades occur on the same day for the same ticker, add time: `YYYY-MM-DD-ACTION-TICKER-HH-MM.md`

### File Content

```markdown
---
date: 2026-02-04
time: 08:05
action: buy
ticker: IEM
quantity: 10
price: 128.39
value: 1283.90
fee: 6.50
---

# IEM Purchase - 4 Feb 2026

**Action**: Buy IEM

**Details**:
- Quantity: 10 units
- Total value: $1,283.90 AUD
- Brokerage fee: $6.50
- Total cost: $1,290.40

**Notes**:
_Add any personal notes about this trade here_
```

### YAML Fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Trade date in YYYY-MM-DD format |
| `time` | string | Trade time in HH:MM format (24-hour) |
| `action` | string | buy, sell |
| `ticker` | string | Stock/ETF symbol |
| `quantity` | number | Number of units traded |
| `price` | number | Price per unit in trade currency |
| `value` | number | Total transaction value (absolute value) |
| `fee` | number | Brokerage/transaction fee |

## Adding a New Trade

1. Copy the template file:
   ```bash
   cp trades/template.md trades/YYYY/YYYY-MM-DD-ACTION-TICKER.md
   ```

2. Fill in the YAML frontmatter with trade details

3. Update the markdown content with any notes

4. The trade will be automatically included in future tax reports

## FIFO Method Explained

The First-In-First-Out (FIFO) method assumes that the first shares purchased are the first shares sold.

### Example

Say you bought VAS three times:
1. 2021-03-11: Buy 11 units @ $86.64
2. 2021-03-18: Buy 57 units @ $87.62
3. 2021-05-17: Buy 11 units @ $90.29

Then sold 40 units on 2023-06-13 @ $95.00:
- First 11 units matched from lot 1 (cost: 11 × $86.64 = $952.04)
- Next 29 units matched from lot 2 (cost: 29 × $87.62 = $2,540.98)
- Total cost basis: $3,493.02
- Sale proceeds: 40 × $95.00 = $3,800.00
- Capital gain: $306.98

This method is:
- **Tax-compliant**: Accepted by ATO for Australian tax reporting
- **Conservative**: Often results in lower gains than other methods (good for taxes)
- **Easy to track**: First purchase = first sale
