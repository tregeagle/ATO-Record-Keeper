# Holdings Checkpoints and Historical Data Gaps

## Overview

This document explains how the trade tracking system handles portfolio snapshots and periods where we lack detailed transaction records.

## What is a Holdings Checkpoint?

A **holdings checkpoint** is a point-in-time snapshot of portfolio holdings, typically from broker/investment account statements. Unlike BUY/SELL transactions, a checkpoint documents:
- Specific date and holdings quantities
- Cost basis for each holding (from the broker)
- Market values and unrealised gains/losses

## Why We Use Checkpoints

1. **ATO Documentation**: Proof of ownership at a specific date with official cost basis
2. **Cost Basis Reference**: When holdings are later sold, the checkpoint provides the acquisition cost
3. **Data Verification**: Checkpoints help verify transaction records are accurate
4. **Gap Documentation**: Transparent record of what we know vs. what's missing

## Current Checkpoints

### Stockspot Holdings Checkpoint - 29 August 2017

**File**: `/home/ruben/Projects/risk/trades/2017/2017-08-29-holdings-checkpoint-stockspot.md`

**Holdings Documented**:
- GOLD: 27 units @ $152.95 cost basis
- IAF: 55 units @ $106.41 cost basis
- IEM: 78 units @ $50.41 cost basis
- IOO: 39 units @ $102.51 cost basis *(Note: Stock split to 76 units by 2018 sale)*
- VAS: 253 units @ $71.90 cost basis

**Account Period**: 1 July 2016 - 1 September 2017

**Data Gap**: No transaction records for initial purchase of these holdings - they must have been acquired before 1 July 2016 or transferred in during the early Stockspot period.

## How Holdings Checkpoints Integrate with Tax Reporting

When a holding from a checkpoint is later sold:

1. **Initial Acquisition**: Use the cost basis from the checkpoint (verified by broker)
2. **Sale Price & Date**: Use the BUY/SELL transaction record for the sale
3. **Capital Gain Calculation**: Proceeds (from sale) - Cost basis (from checkpoint)

**Example - IOO**:
- Acquired before 1 July 2016
- Cost basis: $102.51 per unit (from Stockspot checkpoint)
- 39 units held → stock split to 76 units
- Sold 28 May 2018: 76 units @ $62.19 = $4,726.44 proceeds - $18.14 fee
- Capital loss: ($4,726.44 - $18.14) - ($102.51 × 39 × 2) = loss calculated using checkpoint basis

## Data Quality Notes

### Pre-2016 Holdings

The Stockspot checkpoint is the earliest documented holdings we have. For these holdings:
- ✓ We have official cost basis (from Stockspot report)
- ✓ We have sale records when they were eventually sold
- ✗ We don't have original purchase records
- ~ Acquisition dates are unknown (before 1 July 2016)

### From 2021 Onwards

AllTradesReport.csv provides complete transaction records with:
- ✓ Original purchase records (date, quantity, price, fees)
- ✓ Sale records (date, quantity, price, fees)
- ✓ No gaps or missing data
- ✓ Full FIFO matching capability

### 2016-2020 Period

Partial data:
- ✓ Checkpoints like Stockspot (29 Aug 2017)
- ✓ Some transaction records (WOW, ANZ, GOLD sales)
- ~ Limited purchase records
- ~ Some corporate actions (stock splits) may not be documented

## Using Checkpoints for Tax Purposes

If you need to:

1. **Claim a capital loss on IOO**: Use the cost basis from the 29 Aug 2017 checkpoint ($102.51/unit × 76 units after split)

2. **Verify holdings accumulation**: Compare the 2017 checkpoint holdings to current holdings and trace the transactions that resulted in the current state

3. **Reconstruct cost basis**: When selling very old holdings, a checkpoint may be your only proof of cost basis if the original purchase record is missing

## Future Checkpoints

If you obtain investment statements from other brokers (e.g., Pearler, Sharesight), follow the same format:
- Create a checkpoint file with date and action: `holdings-checkpoint`
- Document all holdings with quantities, cost basis, and market values
- Reference the source document
- Note any known gaps or discrepancies

**File naming pattern**:
```
YYYY-MM-DD-holdings-checkpoint-[SOURCE].md
```

Example:
```
2025-06-30-holdings-checkpoint-pearler.md
2024-06-30-holdings-checkpoint-sharesight.md
```

## ATO Compliance

Holdings checkpoints are ATO-acceptable documentation because:
- Official broker statements
- Timestamped with specific date
- Include cost basis and market values
- Provide audit trail for capital gains calculations
- Serve as proof of ownership

## Limitations

Checkpoints do NOT replace transaction records because:
- They don't show when or at what price acquisitions occurred
- They don't provide fee details
- They can't be used for FIFO matching without corresponding buy records
- They show unrealised gains, not realised gains (which are tax-relevant)

## Best Practice

When you have both a checkpoint and transaction records:

1. **Use checkpoint** for cost basis reference when transaction records are missing
2. **Use transactions** for accurate dates and quantities when available
3. **Document the gap** if you're relying on checkpoint data instead of full transaction history
4. **Cross-check** checkpoint holdings against transaction records (buy minus sells should equal checkpoint quantities)

## Related Documents

- `IMPLEMENTATION_PLAN.md` - How data was sourced and imported
- `TAX_REPORTING.md` - How to generate capital gains reports
- `FIFO_CALCULATOR_ATO_AUDITING.md` - How cost basis is calculated when full records exist
