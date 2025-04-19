from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.utils.stock_data import (
    get_all_stocks, get_all_mutual_funds, get_stock_info,
    get_historical_data, calculate_returns
)
import pandas as pd
import json

stocks_bp = Blueprint('stocks', __name__, url_prefix='/stocks')

@stocks_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all stocks and mutual funds
    stocks = get_all_stocks()
    mutual_funds = get_all_mutual_funds()

    # Group stocks by sector for visualization
    sectors = {}
    for stock in stocks:
        sector = stock.get('sector', 'Other')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)

    # Group stocks by market cap
    market_caps = {
        'Large Cap': [s for s in stocks if s.get('cap') == 'Large Cap'],
        'Mid Cap': [s for s in stocks if s.get('cap') == 'Mid Cap'],
        'Small Cap': [s for s in stocks if s.get('cap') == 'Small Cap']
    }

    return render_template('stocks/dashboard.html',
                          stocks=stocks,
                          mutual_funds=mutual_funds,
                          sectors=sectors,
                          market_caps=market_caps)

@stocks_bp.route('/details/<symbol>')
@login_required
def stock_details(symbol):
    # Get detailed stock information
    stock_info = get_stock_info(symbol)

    if not stock_info:
        return render_template('stocks/not_found.html', symbol=symbol)

    # Get historical data
    historical_data = get_historical_data(symbol)

    # Check if we have data
    if historical_data.empty:
        # Try with alternative symbol formats
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            # Try with NSE suffix
            historical_data = get_historical_data(f"{symbol}.NS")
            if not historical_data.empty:
                symbol = f"{symbol}.NS"
            else:
                # Try with BSE suffix
                historical_data = get_historical_data(f"{symbol}.BO")
                if not historical_data.empty:
                    symbol = f"{symbol}.BO"

        # If still empty, try alternative method
        if historical_data.empty:
            from app.utils.indian_stocks import get_historical_data_alternative
            historical_data = get_historical_data_alternative(symbol)

    # Calculate returns
    returns = calculate_returns(historical_data)

    # Calculate additional technical indicators
    if not historical_data.empty:
        # Calculate moving averages
        historical_data['MA50'] = historical_data['Close'].rolling(window=50).mean()
        historical_data['MA200'] = historical_data['Close'].rolling(window=200).mean()

        # Calculate Bollinger Bands
        historical_data['MA20'] = historical_data['Close'].rolling(window=20).mean()
        historical_data['STD20'] = historical_data['Close'].rolling(window=20).std()
        historical_data['Upper_Band'] = historical_data['MA20'] + (historical_data['STD20'] * 2)
        historical_data['Lower_Band'] = historical_data['MA20'] - (historical_data['STD20'] * 2)

        # Calculate RSI
        delta = historical_data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        historical_data['RSI'] = 100 - (100 / (1 + rs))

        # Calculate MACD
        historical_data['EMA12'] = historical_data['Close'].ewm(span=12, adjust=False).mean()
        historical_data['EMA26'] = historical_data['Close'].ewm(span=26, adjust=False).mean()
        historical_data['MACD'] = historical_data['EMA12'] - historical_data['EMA26']
        historical_data['Signal'] = historical_data['MACD'].ewm(span=9, adjust=False).mean()
        historical_data['Histogram'] = historical_data['MACD'] - historical_data['Signal']

        # Calculate Money Flow Index (MFI)
        typical_price = (historical_data['High'] + historical_data['Low'] + historical_data['Close']) / 3
        money_flow = typical_price * historical_data['Volume']

        # Get positive and negative money flow
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)

        # Calculate money flow ratio and MFI
        positive_flow_sum = positive_flow.rolling(window=14).sum()
        negative_flow_sum = negative_flow.rolling(window=14).sum()
        money_ratio = positive_flow_sum / negative_flow_sum
        historical_data['MFI'] = 100 - (100 / (1 + money_ratio))

    # Prepare data for charts
    dates = historical_data.index.strftime('%Y-%m-%d').tolist() if not historical_data.empty else []

    # OHLC data for candlestick chart
    open_data = historical_data['Open'].tolist() if not historical_data.empty else []
    high_data = historical_data['High'].tolist() if not historical_data.empty else []
    low_data = historical_data['Low'].tolist() if not historical_data.empty else []
    close_data = historical_data['Close'].tolist() if not historical_data.empty else []
    volume_data = historical_data['Volume'].tolist() if not historical_data.empty else []

    # Prepare technical indicator data
    ma50_data = historical_data['MA50'].tolist() if not historical_data.empty and 'MA50' in historical_data else []
    ma200_data = historical_data['MA200'].tolist() if not historical_data.empty and 'MA200' in historical_data else []
    upper_band_data = historical_data['Upper_Band'].tolist() if not historical_data.empty and 'Upper_Band' in historical_data else []
    lower_band_data = historical_data['Lower_Band'].tolist() if not historical_data.empty and 'Lower_Band' in historical_data else []
    rsi_data = historical_data['RSI'].tolist() if not historical_data.empty and 'RSI' in historical_data else []

    # MACD data
    macd_data = historical_data['MACD'].tolist() if not historical_data.empty and 'MACD' in historical_data else []
    signal_data = historical_data['Signal'].tolist() if not historical_data.empty and 'Signal' in historical_data else []
    histogram_data = historical_data['Histogram'].tolist() if not historical_data.empty and 'Histogram' in historical_data else []

    # MFI data
    mfi_data = historical_data['MFI'].tolist() if not historical_data.empty and 'MFI' in historical_data else []

    # Find similar stocks (same sector)
    all_stocks = get_all_stocks()
    sector = None
    for s in all_stocks:
        if s['symbol'] == symbol or s['symbol'] == f"{symbol}.NS" or s['symbol'] == f"{symbol}.BO":
            sector = s.get('sector')
            break

    similar_stocks = [s for s in all_stocks if s.get('sector') == sector and
                     s['symbol'] != symbol and
                     s['symbol'] != f"{symbol}.NS" and
                     s['symbol'] != f"{symbol}.BO"][:5]

    return render_template('stocks/details.html',
                          symbol=symbol,
                          stock_info=stock_info,
                          open_data=json.dumps(open_data),
                          high_data=json.dumps(high_data),
                          low_data=json.dumps(low_data),
                          close_data=json.dumps(close_data),
                          volume_data=json.dumps(volume_data),
                          dates=json.dumps(dates),
                          ma50_data=json.dumps(ma50_data),
                          ma200_data=json.dumps(ma200_data),
                          upper_band_data=json.dumps(upper_band_data),
                          lower_band_data=json.dumps(lower_band_data),
                          rsi_data=json.dumps(rsi_data),
                          macd_data=json.dumps(macd_data),
                          signal_data=json.dumps(signal_data),
                          histogram_data=json.dumps(histogram_data),
                          mfi_data=json.dumps(mfi_data),
                          similar_stocks=similar_stocks)

@stocks_bp.route('/mutual-funds')
@login_required
def mutual_funds():
    # Get all mutual funds
    mutual_funds = get_all_mutual_funds()

    # Group by category
    categories = {}
    for fund in mutual_funds:
        category = fund.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(fund)

    return render_template('stocks/mutual_funds.html',
                          mutual_funds=mutual_funds,
                          categories=categories)

@stocks_bp.route('/mutual-fund/<symbol>')
@login_required
def mutual_fund_details(symbol):
    # Find the mutual fund
    mutual_funds = get_all_mutual_funds()
    fund = None
    for mf in mutual_funds:
        if mf['symbol'] == symbol:
            fund = mf
            break

    if not fund:
        return render_template('stocks/not_found.html', symbol=symbol)

    # Get historical data
    historical_data = get_historical_data(symbol)

    # Prepare data for charts
    price_data = historical_data['Close'].tolist() if not historical_data.empty else []
    dates = historical_data.index.strftime('%Y-%m-%d').tolist() if not historical_data.empty else []

    # Find similar funds (same category)
    similar_funds = [mf for mf in mutual_funds if mf.get('category') == fund.get('category') and mf['symbol'] != symbol]

    return render_template('stocks/mutual_fund_details.html',
                          fund=fund,
                          price_data=json.dumps(price_data),
                          dates=json.dumps(dates),
                          similar_funds=similar_funds)

@stocks_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').upper()

    if not query:
        return jsonify([])

    # Search in stocks and mutual funds
    stocks = get_all_stocks()
    mutual_funds = get_all_mutual_funds()

    # Filter stocks and mutual funds by query
    filtered_stocks = [s for s in stocks if query in s['symbol'] or query in s['name'].upper()]
    filtered_funds = [f for f in mutual_funds if query in f['symbol'] or query in f['name'].upper()]

    # Combine results
    results = []
    for stock in filtered_stocks:
        results.append({
            'symbol': stock['symbol'],
            'name': stock['name'],
            'type': 'Stock',
            'cap': stock.get('cap', ''),
            'sector': stock.get('sector', '')
        })

    for fund in filtered_funds:
        results.append({
            'symbol': fund['symbol'],
            'name': fund['name'],
            'type': 'Mutual Fund',
            'category': fund.get('category', ''),
            'aum': fund.get('aum', '')
        })

    return jsonify(results[:10])  # Limit to 10 results
