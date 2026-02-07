# ATO Trade Tracking & Tax Reporting Documentation

Complete documentation for the investment trade tracking system and capital gains tax reporting.

## Quick Navigation

### Getting Started
- **[TRADE_SYSTEM_OVERVIEW.md](TRADE_SYSTEM_OVERVIEW.md)** - Overview of the markdown-based trade system
  - Philosophy and design
  - Directory structure
  - How to add new trades
  - FIFO method explanation

### Tax Reporting
- **[TAX_REPORTING.md](TAX_REPORTING.md)** - Quick guide to generating tax reports
  - How to run the FIFO calculator
  - Report format and what it contains
  - Data quality notes
  - How to share with accountant

- **[FIFO_CALCULATOR_ATO_AUDITING.md](FIFO_CALCULATOR_ATO_AUDITING.md)** - Comprehensive technical documentation
  - How the FIFO calculator works (technical details)
  - ATO compliance requirements and how they're met
  - Detailed calculation examples
  - Code structure and functions
  - How to use for auditing purposes
  - Testing and verification
  - What to submit to ATO

### Investment Context
- **[INVESTMENT_SUMMARY.md](INVESTMENT_SUMMARY.md)** - Overview of current holdings and history
  - Current portfolio status
  - Investment patterns
  - Tax considerations
  - Verified trade data

---

## System Architecture

```
/home/ruben/Projects/risk/
├── docs/                          (this folder - documentation)
│   ├── README.md                  (you are here)
│   ├── TRADE_SYSTEM_OVERVIEW.md
│   ├── TAX_REPORTING.md
│   ├── FIFO_CALCULATOR_ATO_AUDITING.md
│   └── INVESTMENT_SUMMARY.md
│
├── trades/                        (trade records & scripts)
│   ├── 2020/ through 2026/        (84 trade files)
│   ├── template.md                (template for new trades)
│   ├── scripts/
│   │   ├── fifo_calculator.py     (main tax calculator)
│   │   ├── summarize.py
│   │   └── import_pearler.py
│   └── README.md                  (detailed trade system guide)
│
├── reports/                       (generated tax reports)
│   ├── html/                      (HTML reports for browser viewing)
│   │   ├── index.html             (report index with CGT indicators)
│   │   ├── cgt-2023.html through cgt-2026.html
│   │   └── style.css
│   └── markdown/                  (markdown source reports)
│       ├── INDEX.md               (markdown index)
│       └── cgt-2023.md through cgt-2026.md
│
├── imports/                       (original source data)
│   ├── trade-history-statement.pdf (Pearler broker statement)
│   ├── trade-history-statement.txt (PDF converted to text)
│   ├── AllTradesReport.csv        (authoritative trade data)
│   ├── buys-2007-23.csv           (historical buy data)
│   └── sells-2017-22.csv          (historical sell data)
│
└── Makefile                       (build system for reports)
```

---

## Key Files by Purpose

### For Tax Lodgement
1. **Run calculator**: `python trades/scripts/fifo_calculator.py --year 2025`
2. **View HTML report**: `open reports/html/cgt-2025.html`
3. **Share with accountant**: Export from `reports/markdown/cgt-2025.md`

### For Adding New Trades
1. **Copy template**: `cp trades/template.md trades/2026/2026-MM-DD-action-ticker.md`
2. **Fill in YAML**: Edit date, ticker, quantity, price, fee
3. **Regenerate reports**: `make all` (in project root)

### For Auditing / Verification
1. **View individual trades**: Browse `trades/YYYY/*.md` files
2. **Review PDF statement**: `imports/processed/trade-history-statement.txt`
3. **Check calculations**: See FIFO_CALCULATOR_ATO_AUDITING.md for examples

### For Understanding FIFO
1. **Quick intro**: TRADE_SYSTEM_OVERVIEW.md section "FIFO Method Explained"
2. **Technical details**: FIFO_CALCULATOR_ATO_AUDITING.md sections "How It Works" and "Calculation Example"
3. **Code walkthrough**: See `fifo_calculator.py` docstrings and comments

---

## Data Status

### Complete & Verified ✓
- **BUY/SELL transactions**: 2021-2026 (52 trades)
- **Quantities and prices**: All recorded with brokerage fees
- **Tax year filtering**: Implemented per ATO specification (1 Jul - 30 Jun)
- **FIFO algorithm**: Fully implemented and tested
- **Reports generated**: Available for all years 2021-2026

### Historical Data ⚠
- **2007-2020**: Limited data (acquisition details incomplete)
- **2026 (YTD)**: Early in year, may be incomplete

### Verified Against Source
- ✓ Pearler trade-history-statement.pdf (primary broker)
- ✓ 7 discrepancies identified and corrected
- ✓ All action labels (BUY/SELL) verified
- ✓ Fees reconciled and included in cost basis

---

## Common Tasks

### Generate Tax Report for Accountant

```bash
cd /home/ruben/Projects/risk
python trades/scripts/fifo_calculator.py --year 2025 > cgt-2025.txt
# Share cgt-2025.txt with accountant
```

### Check Current Holdings

```bash
python trades/scripts/summarize.py --current-holdings
```

### Audit a Specific Sale

```bash
python trades/scripts/fifo_calculator.py --ticker VAS | grep -A 5 "Detailed Records"
```

### Regenerate All Reports

```bash
cd /home/ruben/Projects/risk
make all
```

### Add a New Trade

```bash
# 1. Copy template
cp trades/template.md trades/2026/2026-02-15-buy-vas.md

# 2. Edit the file with your trade details

# 3. Regenerate reports
make all

# 4. Verify it appears in the report
python trades/scripts/fifo_calculator.py --year 2026
```

---

## Technology Stack

- **Trade records**: Markdown with YAML frontmatter
- **Calculation engine**: Python 3 (fifo_calculator.py)
- **Report generation**: Markdown to HTML via Pandoc
- **Build system**: GNU Make
- **Source control**: Git (all trades versioned)

---

## Security & Auditability

✓ **Plain text storage**: No proprietary formats (future-proof)
✓ **Version controlled**: Complete history in Git
✓ **Transparent calculations**: Every number is traceable to source
✓ **Broker reconciliation**: Cross-checked against Pearler
✓ **ATO compliant**: FIFO method accepted for tax reporting
✓ **Auditable**: Complete lot matching details preserved

---

## Support & Troubleshooting

### Issue: "No sales found" for a year
**Cause**: No SELL transactions recorded for that year
**Check**: Is it a year when you made sales? If yes, verify trades were imported
**Reference**: See FIFO_CALCULATOR_ATO_AUDITING.md

### Issue: FIFO calculator shows wrong gains
**Cause**: Usually missing purchase data or quantity mismatches
**Check**: Verify all purchases have quantity and price recorded
**Reference**: See TRADE_SYSTEM_OVERVIEW.md section "FIFO Method Explained"

### Issue: Report shows blank values
**Cause**: Missing YAML fields in trade file
**Check**: Compare to template.md to ensure all fields are populated
**Reference**: See TRADE_SYSTEM_OVERVIEW.md section "YAML Fields"

---

## For More Information

- **How trades are tracked**: See `trades/README.md`
- **How to use the FIFO calculator**: See `TAX_REPORTING.md`
- **Deep technical details**: See `FIFO_CALCULATOR_ATO_AUDITING.md`
- **Implementation history**: See `trades/TRADES_IMPLEMENTATION_SUMMARY.md`

---

## Contact & Questions

For questions about:
- **How to use the system**: Review the relevant documentation above
- **Python scripts**: Check docstrings in `trades/scripts/*.py`
- **Tax implications**: Consult your accountant
- **ATO requirements**: See FIFO_CALCULATOR_ATO_AUDITING.md or consult ATO directly

---

**Last updated**: February 6, 2026
**Status**: ✓ Production ready
**Data coverage**: 84 trades (2007-2026), verified through Pearler
