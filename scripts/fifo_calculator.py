#!/usr/bin/env python3
"""
FIFO cost basis calculator for tax purposes.

Implements First-In-First-Out (FIFO) method for matching buy and sell transactions.
Generates capital gains/losses for tax reporting.
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import yaml

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


@dataclass
class AcquisitionLot:
    """Represents a single lot of shares acquired."""
    date: str
    quantity: float
    price: float
    fee_per_unit: float
    cost_basis: float
    reference: str

    def __str__(self):
        return f"{self.quantity} units @ ${self.price:.2f} on {self.date}"


@dataclass
class SaleRecord:
    """Represents a capital gain/loss from a sale."""
    date_acquired: str
    date_sold: str
    ticker: str
    quantity: float
    cost_per_unit: float
    cost_basis: float
    sale_price_per_unit: float
    sale_price: float
    capital_gain: float
    reference_acquired: str
    reference_sold: str
    held_over_12_months: bool = False
    discount_applicable: bool = False

    @property
    def is_gain(self) -> bool:
        return self.capital_gain > 0

    @property
    def is_loss(self) -> bool:
        return self.capital_gain < 0

    def __str__(self):
        """Format record for display."""
        return (
            f"{self.ticker}: {self.quantity:.0f} units | "
            f"Acquired {self.date_acquired} @ ${self.cost_per_unit:.2f} | "
            f"Sold {self.date_sold} @ ${self.sale_price_per_unit:.2f} | "
            f"Gain/Loss: ${self.capital_gain:.2f}"
        )


def parse_trade_file(filepath: str) -> Optional[Dict]:
    """Parse a trade markdown file and extract YAML frontmatter."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        yaml_content = match.group(1)
        data = yaml.safe_load(yaml_content)
        data['filepath'] = filepath
        return data
    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return None


def find_all_trades(base_path: str) -> List[Dict]:
    """
    Recursively find and parse all trade files.

    Dynamically discovers all year directories and supports any year.
    Examples: trades/1066/, trades/2025/, trades/2999/, etc.
    """
    trades = []

    # Dynamically discover all year directories (numeric names)
    try:
        all_items = os.listdir(base_path)
        year_dirs = sorted([
            d for d in all_items
            if os.path.isdir(os.path.join(base_path, d))
            and d.isdigit()  # Only numeric directory names
        ])
    except (OSError, IOError):
        return []

    # Process each year directory
    for year_dir in year_dirs:
        year_path = os.path.join(base_path, year_dir)

        for filename in sorted(os.listdir(year_path)):
            if filename.endswith('.md'):
                filepath = os.path.join(year_path, filename)
                trade = parse_trade_file(filepath)
                if trade:
                    trades.append(trade)

    return trades


def calculate_fifo_gains(trades: List[Dict], ticker: Optional[str] = None, tax_year: Optional[int] = None) -> Tuple[List[SaleRecord], Dict]:
    """
    Calculate capital gains/losses using FIFO method.

    Args:
        trades: List of all trade records
        ticker: Optional ticker to filter by
        tax_year: Optional tax year to filter sales (1 Jan - 31 Dec)

    Returns:
        (list of SaleRecords, dict of summary statistics)
    """
    # Filter trades
    if ticker:
        trades = [t for t in trades if t.get('ticker') and t['ticker'].upper() == ticker.upper()]

    # Sort by date
    def _normalize_date_key(date_val):
        if isinstance(date_val, str):
            return date_val
        else:
            return date_val.isoformat()

    trades = sorted(trades, key=lambda t: _normalize_date_key(t.get('date', '')))

    # Track purchases by ticker using FIFO queue
    purchases_queue = defaultdict(list)  # ticker -> [AcquisitionLot]
    sales_records = []
    summary = defaultdict(lambda: {'gains': 0, 'losses': 0, 'quantity': 0})

    for trade in trades:
        action = trade.get('action', '').lower()
        trade_ticker = trade.get('ticker')
        date = trade.get('date', '')
        quantity = float(trade.get('quantity', 0))
        price = float(trade.get('price', 0))
        fee = float(trade.get('fee', 0))
        reference = trade.get('reference', '')

        if not trade_ticker:
            continue

        trade_ticker = trade_ticker.upper()

        if action == 'buy':
            # Add to purchase queue
            lot = AcquisitionLot(
                date=date,
                quantity=quantity,
                price=price,
                fee_per_unit=fee / quantity if quantity > 0 else 0,
                cost_basis=quantity * price + fee,
                reference=reference
            )
            purchases_queue[trade_ticker].append(lot)

        elif action == 'sell':
            # Match against oldest purchases (FIFO)
            remaining_to_sell = quantity
            fee_per_unit = fee / quantity if quantity > 0 else 0

            while remaining_to_sell > 0 and purchases_queue[trade_ticker]:
                lot = purchases_queue[trade_ticker][0]

                # Determine how much of this lot to sell
                units_from_lot = min(remaining_to_sell, lot.quantity)

                # Calculate capital gain/loss including fees
                cost_basis = units_from_lot * lot.price
                buy_fee = units_from_lot * lot.fee_per_unit
                sale_proceeds = units_from_lot * price
                sell_fee = fee_per_unit * units_from_lot
                capital_gain = sale_proceeds - cost_basis - buy_fee - sell_fee

                # Calculate holding period (for CGT discount eligibility)
                # Handle both str and datetime.date objects
                if isinstance(lot.date, str):
                    date_acquired_dt = datetime.strptime(lot.date, '%Y-%m-%d')
                else:
                    date_acquired_dt = datetime.combine(lot.date, datetime.min.time())

                if isinstance(date, str):
                    date_sold_dt = datetime.strptime(date, '%Y-%m-%d')
                else:
                    date_sold_dt = datetime.combine(date, datetime.min.time())

                days_held = (date_sold_dt - date_acquired_dt).days
                held_over_12_months = days_held > 365
                discount_applicable = held_over_12_months  # For individuals

                record = SaleRecord(
                    date_acquired=lot.date,
                    date_sold=date,
                    ticker=trade_ticker,
                    quantity=units_from_lot,
                    cost_per_unit=lot.price,
                    cost_basis=cost_basis + buy_fee,  # Full ATO cost base includes buy fee
                    sale_price_per_unit=price,
                    sale_price=sale_proceeds,
                    capital_gain=capital_gain,
                    reference_acquired=lot.reference,
                    reference_sold=reference,
                    held_over_12_months=held_over_12_months,
                    discount_applicable=discount_applicable
                )
                sales_records.append(record)

                # Update queue and remaining
                lot.quantity -= units_from_lot
                if lot.quantity <= 0:
                    purchases_queue[trade_ticker].pop(0)

                remaining_to_sell -= units_from_lot

                # Update summary
                summary[trade_ticker]['quantity'] -= units_from_lot
                if capital_gain > 0:
                    summary[trade_ticker]['gains'] += capital_gain
                else:
                    summary[trade_ticker]['losses'] += capital_gain

    # Filter by tax year if specified
    if tax_year:
        sales_records = [
            r for r in sales_records
            if _is_in_tax_year(r.date_sold, tax_year)
        ]

    return sales_records, dict(summary)


def format_currency(value: float) -> str:
    """Format a float as currency."""
    return f"${value:,.2f}"


def _get_year(date_val) -> Optional[int]:
    """Extract year from date value (handles both str and datetime.date)."""
    if isinstance(date_val, str):
        return datetime.strptime(date_val, '%Y-%m-%d').year
    else:
        # datetime.date or datetime.datetime
        return date_val.year


def _get_tax_year(date_val) -> int:
    """
    Get the ATO tax year for a given date.
    ATO tax year runs from 1 July to 30 June.
    Returns the ending year of the tax year.

    Examples:
    - 2024-01-15 -> 2024 (within FY 2023-24)
    - 2024-07-15 -> 2025 (within FY 2024-25)
    """
    if isinstance(date_val, str):
        dt = datetime.strptime(date_val, '%Y-%m-%d')
    else:
        dt = date_val

    year = dt.year
    month = dt.month

    # If month is July or later, it's in the next tax year
    if month >= 7:
        return year + 1
    else:
        return year


def _is_in_tax_year(date_val, tax_year: int) -> bool:
    """Check if a date falls within a given ATO tax year."""
    return _get_tax_year(date_val) == tax_year


def calculate_holdings_at_date(trades: List[Dict], as_of_date: str) -> Dict[str, float]:
    """
    Calculate holdings (quantity) at a specific date using FIFO method.

    Args:
        trades: List of all trade records
        as_of_date: Date in YYYY-MM-DD format

    Returns:
        Dict mapping ticker -> quantity held
    """
    holdings = defaultdict(float)

    # Sort trades chronologically
    def _normalize_date_key(date_val):
        if isinstance(date_val, str):
            return date_val
        else:
            return date_val.isoformat()

    sorted_trades = sorted(trades, key=lambda t: _normalize_date_key(t.get('date', '')))

    for trade in sorted_trades:
        trade_date = trade.get('date', '')

        # Only process trades up to the specified date
        if trade_date > as_of_date:
            break

        action = trade.get('action', '').lower()
        ticker = trade.get('ticker', '').upper()
        quantity = float(trade.get('quantity', 0))

        if not ticker:
            continue

        if action == 'buy':
            holdings[ticker] += quantity
        elif action == 'sell':
            holdings[ticker] -= quantity

    return dict(holdings)


def get_price_at_date(ticker: str, date_str: str) -> Optional[float]:
    """
    Get the closing price for a ticker at a specific date.

    Args:
        ticker: Stock/ETF ticker symbol
        date_str: Date in YYYY-MM-DD format

    Returns:
        Closing price or None if not available
    """
    if not YFINANCE_AVAILABLE:
        return None

    try:
        # Format ticker for ASX (Australian stocks)
        if not ticker.endswith('.AX'):
            ticker_full = f"{ticker}.AX"
        else:
            ticker_full = ticker

        # Get price data with some buffer for weekends/holidays
        start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        data = yf.download(ticker_full, start=start_date, end=end_date, progress=False)

        if data.empty:
            return None

        # Get the closest date available
        data['Date'] = data.index.strftime('%Y-%m-%d')
        closest = data[data['Date'] <= date_str]

        if closest.empty:
            return None

        price = closest.iloc[-1]['Close']
        return float(price)
    except Exception:
        return None


def get_all_buys_and_sells(trades: List[Dict], tax_year: Optional[int] = None) -> List[Dict]:
    """
    Get all BUY and SELL transactions, optionally filtered by tax year.

    Returns a list of dicts with: date, action, ticker, quantity, price, fee
    """
    buy_sell_trades = []

    for trade in trades:
        action = trade.get('action', '').lower()
        if action not in ['buy', 'sell']:
            continue

        date = trade.get('date', '')

        # Filter by tax year if specified
        if tax_year and not _is_in_tax_year(date, tax_year):
            continue

        buy_sell_trades.append({
            'date': date,
            'action': action,
            'ticker': trade.get('ticker', '').upper(),
            'quantity': float(trade.get('quantity', 0)),
            'price': float(trade.get('price', 0)),
            'fee': float(trade.get('fee', 0))
        })

    return sorted(buy_sell_trades, key=lambda t: t['date'])


def generate_tax_report(sales_records: List[SaleRecord], summary: Dict, trades: Optional[List[Dict]] = None, ticker: Optional[str] = None, tax_year: Optional[int] = None) -> str:
    """Generate a markdown tax report."""
    if tax_year:
        # Tax year format: "2025" means FY 2024-25 (1 Jul 2024 - 30 Jun 2025)
        prev_year = tax_year - 1
        title = f"# Capital Gains Report - Tax Year {tax_year} (1 Jul {prev_year} - 30 Jun {tax_year})"
    elif ticker:
        title = f"# Capital Gains Report - {ticker}"
    else:
        title = "# Capital Gains Report (All Time)"

    output = title + "\n\n"

    # Always add buy/sell transactions section (even if no sales for CGT)
    if trades:
        buys_and_sells = get_all_buys_and_sells(trades, tax_year)
        if buys_and_sells:
            output += "<details>\n<summary>All Buy/Sell Transactions with Fees</summary>\n\n"
            output += "| Date | Action | Ticker | Quantity | Price | Fee |\n"
            output += "|------|--------|--------|----------|-------|-----|\n"

            for t in buys_and_sells:
                output += (
                    f"| {t['date']} | {t['action'].upper()} | {t['ticker']} | "
                    f"{t['quantity']:.0f} | ${t['price']:.2f} | {format_currency(t['fee'])} |\n"
                )

            output += "\n</details>\n\n"

    # If no sales, show that and return (but include transactions above)
    if not sales_records:
        output += "No capital gains/losses to report for this period.\n"
        return output

    # Summary statistics
    total_gain = sum(r.capital_gain for r in sales_records if r.is_gain)
    total_loss = sum(r.capital_gain for r in sales_records if r.is_loss)
    net_gain = total_gain + total_loss  # losses are negative

    # CGT discount calculation (ATO method)
    # Separate gains into discount-eligible and non-discount
    discount_gains = sum(r.capital_gain for r in sales_records if r.is_gain and r.discount_applicable)
    non_discount_gains = sum(r.capital_gain for r in sales_records if r.is_gain and not r.discount_applicable)

    # Apply losses against non-discount gains first, then discount gains
    remaining_loss = abs(total_loss)

    # Apply to non-discount gains first
    non_discount_after_loss = max(0, non_discount_gains - remaining_loss)
    remaining_loss = max(0, remaining_loss - non_discount_gains)

    # Apply remaining losses to discount-eligible gains
    discount_after_loss = max(0, discount_gains - remaining_loss)

    # Apply 50% CGT discount to remaining discount-eligible gains
    cgt_discount_amount = discount_after_loss * 0.5
    net_capital_gain_ato = non_discount_after_loss + (discount_after_loss - cgt_discount_amount)

    output += "## Summary\n\n"
    output += f"- **Total sales**: {len(sales_records)}\n"
    output += f"- **Total units sold**: {sum(r.quantity for r in sales_records):.0f}\n"
    output += f"- **Total capital gains**: {format_currency(total_gain)}\n"
    output += f"  - Discount-eligible (held >12 months): {format_currency(discount_gains)}\n"
    output += f"  - Non-discount (held \u226412 months): {format_currency(non_discount_gains)}\n"
    output += f"- **Total capital losses**: {format_currency(total_loss)}\n"
    output += f"- **Net capital gain/loss** (before discount): {format_currency(net_gain)}\n"
    output += f"- **CGT discount (50%)**: -{format_currency(cgt_discount_amount)}\n"
    output += f"- **Net capital gain (ATO label 18A)**: {format_currency(net_capital_gain_ato)}\n\n"

    # By ticker summary if not filtered
    if not ticker:
        output += "## Summary by Ticker\n\n"
        for t in sorted(set(r.ticker for r in sales_records)):
            ticker_sales = [r for r in sales_records if r.ticker == t]
            ticker_gains = sum(r.capital_gain for r in ticker_sales if r.is_gain)
            ticker_losses = sum(r.capital_gain for r in ticker_sales if r.is_loss)
            output += f"- **{t}**: {len(ticker_sales)} sales, Net: {format_currency(ticker_gains + ticker_losses)}\n"
        output += "\n"

    # Detailed records
    output += "## Detailed Records\n\n"
    output += "| Date Sold | Ticker | Quantity | Held | Cost per Unit | Sale Price | Cost Basis | Proceeds | Gain/Loss |\n"
    output += "|-----------|--------|----------|------|---------------|------------|-----------|----------|----------|\n"

    for record in sorted(sales_records, key=lambda r: r.date_sold):
        # Calculate holding period display
        # Handle both str and datetime.date objects
        if isinstance(record.date_acquired, str):
            date_acquired_dt = datetime.strptime(record.date_acquired, '%Y-%m-%d')
        else:
            date_acquired_dt = datetime.combine(record.date_acquired, datetime.min.time())

        if isinstance(record.date_sold, str):
            date_sold_dt = datetime.strptime(record.date_sold, '%Y-%m-%d')
        else:
            date_sold_dt = datetime.combine(record.date_sold, datetime.min.time())

        days_held = (date_sold_dt - date_acquired_dt).days
        years = days_held // 365
        remaining_days = days_held % 365
        months = remaining_days // 30

        if years > 0:
            held_str = f"{years}y {months}m"
        else:
            held_str = f"{months}m"

        if record.discount_applicable:
            held_str += " \u2713"  # checkmark for discount eligible

        output += (
            f"| {record.date_sold} | {record.ticker} | {record.quantity:.0f} | "
            f"{held_str} | ${record.cost_per_unit:.2f} | ${record.sale_price_per_unit:.2f} | "
            f"{format_currency(record.cost_basis)} | {format_currency(record.sale_price)} | "
            f"{format_currency(record.capital_gain)} |\n"
        )

    # Detailed breakdown by lot (useful for verification)
    output += "\n## Detailed Breakdown by Acquisition Lot\n\n"
    for record in sorted(sales_records, key=lambda r: (r.ticker, r.date_acquired)):
        output += (
            f"**{record.ticker}** - {record.quantity:.0f} units\n"
            f"- Acquired: {record.date_acquired} @ {format_currency(record.cost_per_unit)}\n"
            f"- Sold: {record.date_sold} @ {format_currency(record.sale_price_per_unit)}\n"
            f"- Cost basis: {format_currency(record.cost_basis)}\n"
            f"- Sale proceeds: {format_currency(record.sale_price)}\n"
            f"- Capital gain/loss: {format_currency(record.capital_gain)}\n\n"
        )

    return output


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Calculate capital gains using FIFO method')
    parser.add_argument('--year', type=int, help='Calculate gains for ATO tax year (1 Jul - 30 Jun). E.g., 2025 = FY 2024-25')
    parser.add_argument('--ticker', help='Show gains for a specific ticker')
    parser.add_argument('--base-path', default='input', help='Base path to trades directory')

    args = parser.parse_args()

    # Load all trades
    trades = find_all_trades(args.base_path)

    # Calculate FIFO gains
    sales_records, summary = calculate_fifo_gains(trades, ticker=args.ticker, tax_year=args.year)

    # Generate report
    report = generate_tax_report(sales_records, summary, trades=trades, ticker=args.ticker, tax_year=args.year)
    print(report)


if __name__ == '__main__':
    main()
