#!/usr/bin/env python3
"""
Calculate holdings value at end of each tax year.

This script calculates:
1. Holdings (quantity) as of 30 June of each tax year
2. Closing prices for each holding on that date
3. Market value of holdings at year-end
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


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
        return None


def find_all_trades(base_path: str) -> List[Dict]:
    """
    Recursively find and parse all trade files.

    Dynamically discovers all year directories (supports any year).
    """
    trades = []

    try:
        all_items = os.listdir(base_path)
        year_dirs = sorted([
            d for d in all_items
            if os.path.isdir(os.path.join(base_path, d))
            and d.isdigit()
        ])
    except (OSError, IOError):
        return []

    for year_dir in year_dirs:
        year_path = os.path.join(base_path, year_dir)

        for filename in sorted(os.listdir(year_path)):
            if filename.endswith('.md'):
                filepath = os.path.join(year_path, filename)
                trade = parse_trade_file(filepath)
                if trade:
                    trades.append(trade)

    return trades


def calculate_holdings_at_date(trades: List[Dict], as_of_date: str) -> Dict[str, float]:
    """Calculate holdings (quantity) at a specific date using FIFO method."""
    holdings = defaultdict(float)

    def _normalize_date_key(date_val):
        if isinstance(date_val, str):
            return date_val
        else:
            return date_val.isoformat()

    sorted_trades = sorted(trades, key=lambda t: _normalize_date_key(t.get('date', '')))

    for trade in sorted_trades:
        trade_date = trade.get('date', '')

        if trade_date > as_of_date:
            break

        action = trade.get('action', '').lower()
        ticker = trade.get('ticker', '').upper()
        quantity = float(trade.get('quantity', 0))

        if not ticker or action not in ['buy', 'sell']:
            continue

        if action == 'buy':
            holdings[ticker] += quantity
        elif action == 'sell':
            holdings[ticker] -= quantity

    return dict(holdings)


def get_price_at_date(ticker: str, date_str: str) -> Optional[float]:
    """Get the closing price for a ticker at a specific date."""
    if not YFINANCE_AVAILABLE:
        return None

    try:
        if not ticker.endswith('.AX'):
            ticker_full = f"{ticker}.AX"
        else:
            ticker_full = ticker

        from datetime import timedelta
        start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        data = yf.download(ticker_full, start=start_date, end=end_date, progress=False)

        if data.empty:
            return None

        data['Date'] = data.index.strftime('%Y-%m-%d')
        closest = data[data['Date'] <= date_str]

        if closest.empty:
            return None

        price = closest.iloc[-1]['Close']
        return float(price)
    except Exception:
        return None


def get_holdings_value_for_year(trades: List[Dict], tax_year: int) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Get holdings and their values at the end of a tax year.

    Args:
        trades: List of all trade records
        tax_year: ATO tax year (e.g., 2025 = 1 Jul 2024 - 30 Jun 2025)

    Returns:
        (holdings_dict, values_dict) where each maps ticker -> quantity/value
    """
    # End of tax year is 30 June
    year_end_date = f"{tax_year}-06-30"

    holdings = calculate_holdings_at_date(trades, year_end_date)

    values = {}
    for ticker, quantity in holdings.items():
        if quantity <= 0:
            continue

        price = get_price_at_date(ticker, year_end_date)
        if price:
            value = quantity * price
            values[ticker] = value

    return holdings, values


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Calculate holdings value at year-end')
    parser.add_argument('--year', type=int, help='Tax year to analyze')
    parser.add_argument('--base-path', default='input', help='Base path to trades directory')
    parser.add_argument('--all-years', action='store_true', help='Calculate for all years')

    args = parser.parse_args()

    trades = find_all_trades(args.base_path)

    if args.all_years:
        years = range(2007, 2027)
    elif args.year:
        years = [args.year]
    else:
        years = range(2021, 2027)  # Default to recent years

    # Get current date to skip incomplete tax years
    today = datetime.now().date()

    for year in years:
        # Skip years where tax year end (30 June) is in the future
        year_end = datetime.strptime(f"{year}-06-30", '%Y-%m-%d').date()
        if year_end > today:
            continue
        holdings, values = get_holdings_value_for_year(trades, year)

        print(f"Tax Year {year} (30 Jun {year}):")
        print("-" * 50)

        if not holdings or not any(q > 0 for q in holdings.values()):
            print("  No holdings\n")
            continue

        total_value = 0
        for ticker in sorted(holdings.keys()):
            qty = holdings[ticker]
            if qty <= 0:
                continue

            value = values.get(ticker, 0)
            total_value += value

            if value > 0:
                price = value / qty
                print(f"  {ticker}: {qty:.0f} units @ ${price:.2f} = ${value:,.2f}")
            else:
                print(f"  {ticker}: {qty:.0f} units @ [price not available]")

        print(f"\n  Total Holdings Value: ${total_value:,.2f}")
        print()


if __name__ == '__main__':
    main()
