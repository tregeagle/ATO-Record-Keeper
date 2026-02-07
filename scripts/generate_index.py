#!/usr/bin/env python3
"""
Generate index pages (HTML and Markdown) with CGT indicators and holdings values.

This script:
1. Checks each tax year report for sales
2. Calculates holdings at end of each tax year
3. Attempts to fetch current prices for holdings
4. Generates index.html and INDEX.md with complete information
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

try:
    import yfinance as yf
    import pandas as pd
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    pd = None


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
        return data
    except Exception:
        return None


def find_all_trades(base_path: str) -> List[Dict]:
    """
    Recursively find and parse all trade files.

    Dynamically discovers all year directories (supports any year: 1066, 2025, 2999, etc).
    """
    trades = []

    try:
        all_items = os.listdir(base_path)
        year_dirs = sorted([
            d for d in all_items
            if os.path.isdir(os.path.join(base_path, d))
            and d.isdigit()  # Only numeric directory names
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


def has_cgt_events(report_path: str) -> bool:
    """Check if a report has any capital gains/losses (CGT events)."""
    try:
        with open(report_path, 'r') as f:
            content = f.read()
        # Check for the message that appears when there are no sales
        return "No capital gains/losses to report for this period" not in content
    except FileNotFoundError:
        return False


def calculate_yearly_transactions(trades: List[Dict], tax_year: int) -> Tuple[float, float]:
    """
    Calculate total value of buys and sells for a tax year.

    Tax year is 1 July to 30 June (e.g., 2025 = 1 Jul 2024 to 30 Jun 2025)

    Returns:
        (total_buys_value, total_sells_value)
    """
    from datetime import date as date_type

    year_start = f"{tax_year - 1}-07-01"
    year_end = f"{tax_year}-06-30"

    total_buys = 0.0
    total_sells = 0.0

    for trade in trades:
        trade_date = trade.get('date')
        action = trade.get('action', '').lower()

        if not trade_date:
            continue

        # Convert date objects to strings
        if isinstance(trade_date, date_type):
            trade_date = trade_date.isoformat()
        trade_date = str(trade_date)

        if trade_date < year_start or trade_date > year_end:
            continue

        value = float(trade.get('value', 0))

        if action == 'buy':
            total_buys += value
        elif action == 'sell':
            total_sells += value

    return total_buys, total_sells


def calculate_holdings_at_date(trades: List[Dict], as_of_date: str) -> Dict[str, float]:
    """Calculate holdings (quantity) at a specific date."""
    holdings = defaultdict(float)

    def _normalize_date_key(date_val):
        if isinstance(date_val, str):
            return date_val
        else:
            return date_val.isoformat()

    def _normalize_date_str(date_val):
        if isinstance(date_val, str):
            return date_val
        else:
            return date_val.isoformat()

    sorted_trades = sorted(trades, key=lambda t: _normalize_date_key(t.get('date', '')))

    for trade in sorted_trades:
        trade_date = _normalize_date_str(trade.get('date', ''))

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


def get_price_at_date(ticker: str, date_str: str, verbose: bool = False) -> Optional[float]:
    """Get the closing price for a ticker at a specific date."""
    if not YFINANCE_AVAILABLE:
        return None

    try:
        if not ticker.endswith('.AX'):
            ticker_full = f"{ticker}.AX"
        else:
            ticker_full = ticker

        start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        data = yf.download(ticker_full, start=start_date, end=end_date, progress=False)

        if data.empty or data.shape[0] == 0:
            if verbose:
                print(f"  ⚠ {ticker}: No data found", file=sys.stderr)
            return None

        # Handle both single ticker and multi-ticker data
        if isinstance(data.columns, pd.MultiIndex):
            # Multi-ticker data
            close_col = ('Close', ticker_full)
            if close_col not in data.columns:
                if verbose:
                    print(f"  ⚠ {ticker}: Close price not found", file=sys.stderr)
                return None
        else:
            # Single ticker data
            close_col = 'Close'

        close_prices = data[close_col]

        # Find the closest date on or before the target date
        data_dates = close_prices.index.strftime('%Y-%m-%d')
        valid_dates = [d for d in data_dates if d <= date_str]

        if not valid_dates:
            if verbose:
                print(f"  ⚠ {ticker}: No data before {date_str}", file=sys.stderr)
            return None

        # Get the most recent valid date
        last_date_idx = data_dates.tolist().index(valid_dates[-1])
        price = float(close_prices.iloc[last_date_idx])
        return price
    except Exception as e:
        if verbose:
            print(f"  ⚠ {ticker}: Error downloading - {str(e)[:50]}", file=sys.stderr)
        return None


def get_holdings_value_for_year(trades: List[Dict], tax_year: int, verbose: bool = False) -> Tuple[Dict[str, float], Dict[str, float], float]:
    """
    Get holdings and their values at the end of a tax year.

    Only includes holdings with positive quantities (actual holdings).

    Returns:
        (holdings_dict, values_dict, total_value)
    """
    year_end_date = f"{tax_year}-06-30"

    all_holdings = calculate_holdings_at_date(trades, year_end_date)

    # Filter to only positive holdings
    holdings = {k: v for k, v in all_holdings.items() if v > 0}

    values = {}
    total_value = 0
    failed_tickers = []

    for ticker in sorted(holdings.keys()):
        quantity = holdings[ticker]

        price = get_price_at_date(ticker, year_end_date, verbose=verbose)
        if price:
            value = quantity * price
            values[ticker] = value
            total_value += value
        else:
            failed_tickers.append(ticker)

    if failed_tickers and verbose:
        print(f"  Holdings with no price data: {', '.join(failed_tickers)}", file=sys.stderr)

    return holdings, values, total_value


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate index pages with CGT and holdings info')
    parser.add_argument('--trades-path', default='input', help='Path to trades directory')
    parser.add_argument('--reports-path', default='output', help='Path to reports directory')
    parser.add_argument('--markdown-dir', default='output/markdown', help='Markdown reports directory')
    parser.add_argument('--html-dir', default='output/html', help='HTML reports directory')

    args = parser.parse_args()

    # Load all trades
    print("Loading trades...", file=sys.stderr)
    trades = find_all_trades(args.trades_path)

    # Get list of tax years from report files
    report_files = list(Path(args.markdown_dir).glob('cgt-*.md'))
    years = sorted(set(
        int(f.stem.split('-')[-1])
        for f in report_files
    ))

    if not years:
        # Fallback: scan trades directory
        years = sorted(set(
            int(d.name) for d in Path(args.trades_path).glob('[0-9]*')
            if d.is_dir()
        ))

    print(f"Found {len(years)} tax years: {years}", file=sys.stderr)

    # Get current date to skip incomplete tax years
    today = datetime.now().date()

    # Generate year data
    year_data = {}
    for year in years:
        # Mark as in-progress if tax year end (30 June) is in the future
        year_end = datetime.strptime(f"{year}-06-30", '%Y-%m-%d').date()
        is_in_progress = year_end > today

        has_cgt = has_cgt_events(os.path.join(args.markdown_dir, f'cgt-{year}.md'))
        holdings, values, total_value = get_holdings_value_for_year(trades, year, verbose=True)
        total_buys, total_sells = calculate_yearly_transactions(trades, year)

        year_data[year] = {
            'has_cgt': has_cgt,
            'holdings': holdings,
            'values': values,
            'total_value': total_value,
            'total_buys': total_buys,
            'total_sells': total_sells,
            'is_in_progress': is_in_progress
        }

        if total_value > 0:
            print(f"Year {year}: Buys ${total_buys:,.2f} | Sells ${total_sells:,.2f} | Holdings ${total_value:,.2f}", file=sys.stderr)
        else:
            print(f"Year {year}: Buys ${total_buys:,.2f} | Sells ${total_sells:,.2f} | [no holdings]", file=sys.stderr)

    # Generate HTML index
    print(f"\nGenerating HTML index...", file=sys.stderr)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ATO Capital Gains Reports</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<main>
<h1>ATO Capital Gains Tax Reports</h1>
<p>Complete tax reports for all trade years with FIFO cost basis calculations.</p>

<h2>Tax Year Reports</h2>
<table>
<thead>
<tr>
<th>Tax Year</th>
<th>Value Sold</th>
<th>Value Bought</th>
<th>Holdings Value (30 Jun)</th>
<th>Report</th>
</tr>
</thead>
<tbody>
"""

    for year in sorted(year_data.keys(), reverse=True):
        data = year_data[year]
        total_sells = data['total_sells']
        total_buys = data['total_buys']
        total_value = data['total_value']
        is_in_progress = data['is_in_progress']

        # Format year label with "in progress" indicator
        year_label = f"Tax Year {year}"
        if is_in_progress:
            year_label += ' <span style="font-size: 0.85em; color: #888;">(in progress)</span>'

        # Format sell value with checkmark if no sales
        if total_sells > 0:
            sells_str = f"${total_sells:,.2f}"
        else:
            sells_str = '<span style="color: green; font-size: 1.3em;">✓</span>'

        # Format buy value
        if total_buys > 0:
            buys_str = f"${total_buys:,.2f}"
        else:
            buys_str = "—"

        # Format holdings value
        if total_value > 0:
            value_str = f"${total_value:,.2f}"
        else:
            value_str = "—"

        html_content += f"""<tr>
<td><strong>{year_label}</strong></td>
<td style="text-align: right;">{sells_str}</td>
<td style="text-align: right;">{buys_str}</td>
<td style="text-align: right;">{value_str}</td>
<td><a href="cgt-{year}.html">View Report</a></td>
</tr>
"""

    html_content += """</tbody>
</table>

<h2>Legend</h2>
<ul>
<li><strong>Value Sold</strong> = Total value of all shares sold in the tax year (green ✓ = no sales)</li>
<li><strong>Value Bought</strong> = Total value of all shares purchased in the tax year</li>
<li><strong>Holdings Value</strong> = Market value of remaining holdings at 30 June (end of tax year)</li>
</ul>

<h2>About These Reports</h2>
<p>These reports are generated using the FIFO (First-In-First-Out) cost basis method, which is ATO-compliant for Australian capital gains tax reporting.</p>
<p><strong>Each report includes:</strong></p>
<ul>
<li>Total capital gains and losses for the year</li>
<li>Breakdown by ticker (VAS, VGS, GOLD, IEM, IAF)</li>
<li>Detailed sale records with cost basis</li>
<li>FIFO lot matching details (acquisition dates & prices)</li>
<li>Complete transaction list with fees</li>
</ul>
<p><em>Generated: """ + datetime.now().strftime("%a %d %b %Y %H:%M:%S %Z") + """</em></p>
</main>
</body>
</html>"""

    with open(os.path.join(args.html_dir, 'index.html'), 'w') as f:
        f.write(html_content)

    print(f"✓ Created {os.path.join(args.html_dir, 'index.html')}", file=sys.stderr)

    # Generate Markdown index
    print(f"Generating Markdown index...", file=sys.stderr)
    md_content = """# ATO Capital Gains Tax Reports

Complete tax reports for all trade years with FIFO cost basis calculations.

## Tax Year Reports

| Tax Year | Value Sold | Value Bought | Holdings Value (30 Jun) | Report |
|----------|-----------|---------|------------------------|--------|
"""

    for year in sorted(year_data.keys(), reverse=True):
        data = year_data[year]
        total_sells = data['total_sells']
        total_buys = data['total_buys']
        total_value = data['total_value']
        is_in_progress = data['is_in_progress']

        # Format year label with "in progress" indicator
        year_label = f"Tax Year {year}"
        if is_in_progress:
            year_label += ' (in progress)'

        # Format sell value with checkmark if no sales
        if total_sells > 0:
            sells_str = f"${total_sells:,.2f}"
        else:
            sells_str = "✓"

        # Format buy value
        if total_buys > 0:
            buys_str = f"${total_buys:,.2f}"
        else:
            buys_str = "—"

        # Format holdings value
        if total_value > 0:
            value_str = f"${total_value:,.2f}"
        else:
            value_str = "—"

        md_content += f"| **{year_label}** | {sells_str} | {buys_str} | {value_str} | [View Report](cgt-{year}.md) |\n"

    md_content += """
## Legend

- **Value Sold** = Total value of all shares sold in the tax year (✓ = no sales)
- **Value Bought** = Total value of all shares purchased in the tax year
- **Holdings Value** = Market value of remaining holdings at 30 June (end of tax year)

## About These Reports

These reports are generated using the FIFO (First-In-First-Out) cost basis method, which is ATO-compliant for Australian capital gains tax reporting.

**Each report includes:**

- Total capital gains and losses for the year
- Breakdown by ticker (VAS, VGS, GOLD, IEM, IAF)
- Detailed sale records with cost basis
- FIFO lot matching details (acquisition dates & prices)
- Complete transaction list with fees

_Generated: """ + datetime.now().strftime("%a %d %b %Y %H:%M:%S %Z") + """_
"""

    with open(os.path.join(args.markdown_dir, 'INDEX.md'), 'w') as f:
        f.write(md_content)

    print(f"✓ Created {os.path.join(args.markdown_dir, 'INDEX.md')}", file=sys.stderr)


if __name__ == '__main__':
    main()
