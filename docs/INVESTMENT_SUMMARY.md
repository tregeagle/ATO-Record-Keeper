# Investment Portfolio Summary for Tax Purposes

## Current Status (as of 4 February 2026)

**Data Sources:**
- Pearler: Complete transaction history (Aug 2020 - Feb 2026)
- Sharesight: Partial history, missing pre-March 2021 trades
- **Authoritative source:** Pearler trade-history-statement.pdf

---

## Current Holdings

Based on Pearler transaction statement:

| ETF | Current Qty | Status | Notes |
|-----|-------------|--------|-------|
| **VAS** (Vanguard Australian Shares) | 18 units | ACTIVE | Most frequent buys; regular monthly investments |
| **VGS** (Vanguard Global Shares) | 3 units | ACTIVE | International diversification |
| **IEM** (iShares MSCI Emerging Markets) | 4 units | ACTIVE | Recent purchases Feb 2026 |
| **GOLD** (SPDR Gold) | 0 units | SOLD | Fully liquidated |
| **IAF** (iShares Asia ETF) | 0 units | SOLD | Fully liquidated |
| **VDHG** (Vanguard All-Weather) | 0 units | SOLD | One-time sale Feb 2022 |

---

## Investment Pattern Analysis

### Timeline
- **Start:** August 2020 ($5 initial deposit)
- **Phase 1 (Aug 2020 - Jan 2022):** Building foundation, monthly deposits $200-300
- **Phase 2 (Feb 2022):** Significant deposit ($22k), rebalancing of portfolio
- **Phase 3 (Mar 2022 - now):** Automatic deposits $321/month, regular buys every 2-3 weeks

### Key Transactions
- **Feb 2022:** Sold VDHG ($12,371), redeployed into VAS/VGS/IEM/IAF
- **Apr 2023:** Sold GOLD ($2,863) and IAF ($4,068)
- **Jun 2023:** Sold IEM ($12,947) and IAF ($3,995)
- **Oct/Dec 2025:** Major rebalancing - sold VAS, VGS, and GOLD
- **Recent (Jan-Feb 2026):** Resumed accumulation of VAS/IEM

---

## Tax Reporting Concerns

### Critical Items to Track
1. **Capital Gains/Losses** - Multiple sales with need for cost basis calculation
2. **Brokerage Fees** - Each transaction has transaction costs (recorded in Pearler)
3. **Dividend Income** - ETF distributions not visible in this export; may need separate statement
4. **Cost Basis Determination** - For large liquidations in 2023 and 2025, method matters (FIFO/LIFO/ACB)

### Data Quality Notes
- Pearler provides complete transaction history (authoritative source)
- Trade-history-statement.pdf verified for accuracy
- All corrected trades verified against PDF source

---

## Verified Trade Data

All trades have been verified against:
- Pearler trade-history-statement.pdf (primary source)
- Individual trade files in `/trades/YYYY/` directories
- Historical CSV imports (buys-2007-23.csv, sells-2017-22.csv)

**Quality assurance completed:**
- ✓ 7 discrepancies identified and corrected
- ✓ All BUY and SELL actions verified against broker statement
- ✓ Quantities, prices, and fees validated
- ✓ FIFO matching tested and verified

---

## Recommended Approach for Tax Simplification

### For Current Year (2026)
1. Track each trade as you make it (copy template.md for new trades)
2. Quarterly: Run FIFO calculator to see projected CGT
3. End of year: Generate final report for accountant

### For Historical Years (2021-2025)
- Reports already generated and verified
- Available at `/reports/html/cgt-YEAR.html`
- Use for tax lodgement or accountant review

### For Pre-2021 Records
- Historical data imported but incomplete
- Available for reference
- Recommend verifying against Pearler for definitive records

---

## Questions for Your Accountant

1. Are the FIFO lot matching details sufficient for CGT reporting?
2. Should I track dividend/distribution income separately?
3. Any CGT concessions or special considerations for Australian ETFs?
4. Do you need the detailed trade files, or just the summary reports?
