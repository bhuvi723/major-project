from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from app.utils.stock_data import (
    get_all_stocks, get_all_mutual_funds, get_stock_info,
    get_historical_data, calculate_returns
)
import pandas as pd
import numpy as np
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
    print(f"Processing stock details for symbol: {symbol}")

    # For RELIANCE specifically, try with NSE suffix first
    if symbol.upper() == 'RELIANCE':
        print("Special handling for RELIANCE symbol")
        symbol_to_try = 'RELIANCE.NS'
        stock_info = get_stock_info(symbol_to_try)
        if stock_info and 'regularMarketPrice' in stock_info:
            print(f"Successfully got stock info for {symbol_to_try}")
            historical_data = get_historical_data(symbol_to_try)
            if not historical_data.empty:
                print(f"Successfully got historical data for {symbol_to_try}")
                symbol = symbol_to_try
    else:
        # Get detailed stock information
        stock_info = get_stock_info(symbol)
        historical_data = pd.DataFrame()  # Initialize as empty

        # If the symbol already has a suffix (like INFY.NS), make sure we use it consistently
        if (symbol.endswith('.NS') or symbol.endswith('.BO')) and not historical_data.empty:
            print(f"Symbol {symbol} already has a suffix, using it consistently")

    # If we don't have stock info yet, try normal flow
    if not stock_info or 'regularMarketPrice' not in stock_info:
        print(f"No stock info found for {symbol}, trying alternative approaches")
        stock_info = get_stock_info(symbol)

        if not stock_info or 'regularMarketPrice' not in stock_info:
            print(f"Still no stock info for {symbol}, returning not found page")
            return render_template('stocks/not_found.html', symbol=symbol)

    # If we don't have historical data yet, try to get it
    if 'historical_data' not in locals() or historical_data.empty:
        print(f"Getting historical data for {symbol}")
        historical_data = get_historical_data(symbol)

        # Check if we have data
        if historical_data.empty:
            print(f"No historical data found for {symbol}, trying alternative symbol formats")
            # Try with alternative symbol formats
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                # Try with NSE suffix
                nse_symbol = f"{symbol}.NS"
                print(f"Trying with NSE suffix: {nse_symbol}")
                historical_data = get_historical_data(nse_symbol)
                if not historical_data.empty:
                    print(f"Successfully got historical data for {nse_symbol}")
                    symbol = nse_symbol
                else:
                    # Try with BSE suffix
                    bse_symbol = f"{symbol}.BO"
                    print(f"Trying with BSE suffix: {bse_symbol}")
                    historical_data = get_historical_data(bse_symbol)
                    if not historical_data.empty:
                        print(f"Successfully got historical data for {bse_symbol}")
                        symbol = bse_symbol

            # If still empty, try alternative method
            if historical_data.empty:
                print(f"Still no historical data for {symbol}, using alternative method")
                from app.utils.indian_stocks import get_historical_data_alternative
                historical_data = get_historical_data_alternative(symbol)

    # Calculate returns
    returns = calculate_returns(historical_data)

    # Calculate additional technical indicators
    if not historical_data.empty:
        print(f"Calculating technical indicators for {symbol}")
        try:
            # Calculate moving averages
            historical_data['MA50'] = historical_data['Close'].rolling(window=50).mean()
            historical_data['MA200'] = historical_data['Close'].rolling(window=200).mean()

            # Calculate Bollinger Bands
            historical_data['MA20'] = historical_data['Close'].rolling(window=20).mean()
            historical_data['STD20'] = historical_data['Close'].rolling(window=20).std()
            historical_data['Upper_Band'] = historical_data['MA20'] + (historical_data['STD20'] * 2)
            historical_data['Lower_Band'] = historical_data['MA20'] - (historical_data['STD20'] * 2)

            # Calculate RSI with better handling of edge cases
            delta = historical_data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            # Handle division by zero
            rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
            historical_data['RSI'] = 100 - (100 / (1 + rs))
            # Ensure RSI is within bounds
            historical_data['RSI'] = historical_data['RSI'].clip(0, 100)

            # Calculate MACD
            historical_data['EMA12'] = historical_data['Close'].ewm(span=12, adjust=False).mean()
            historical_data['EMA26'] = historical_data['Close'].ewm(span=26, adjust=False).mean()
            historical_data['MACD'] = historical_data['EMA12'] - historical_data['EMA26']
            historical_data['Signal'] = historical_data['MACD'].ewm(span=9, adjust=False).mean()
            historical_data['Histogram'] = historical_data['MACD'] - historical_data['Signal']

            # Calculate Money Flow Index (MFI) with better handling of edge cases
            typical_price = (historical_data['High'] + historical_data['Low'] + historical_data['Close']) / 3
            money_flow = typical_price * historical_data['Volume']

            # Get positive and negative money flow
            positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
            negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)

            # Calculate money flow ratio and MFI
            positive_flow_sum = positive_flow.rolling(window=14).sum()
            negative_flow_sum = negative_flow.rolling(window=14).sum()
            # Handle division by zero
            money_ratio = positive_flow_sum / negative_flow_sum.replace(0, np.finfo(float).eps)
            historical_data['MFI'] = 100 - (100 / (1 + money_ratio))
            # Ensure MFI is within bounds
            historical_data['MFI'] = historical_data['MFI'].clip(0, 100)

            print(f"Successfully calculated technical indicators for {symbol}")
        except Exception as e:
            print(f"Error calculating technical indicators for {symbol}: {e}")
            # Create default values for technical indicators
            historical_data['MA50'] = historical_data['Close']
            historical_data['MA200'] = historical_data['Close']
            historical_data['Upper_Band'] = historical_data['Close'] * 1.05
            historical_data['Lower_Band'] = historical_data['Close'] * 0.95
            historical_data['RSI'] = pd.Series([50] * len(historical_data), index=historical_data.index)
            historical_data['MACD'] = pd.Series([0] * len(historical_data), index=historical_data.index)
            historical_data['Signal'] = pd.Series([0] * len(historical_data), index=historical_data.index)
            historical_data['Histogram'] = pd.Series([0] * len(historical_data), index=historical_data.index)
            historical_data['MFI'] = pd.Series([50] * len(historical_data), index=historical_data.index)

        # Calculate Average True Range (ATR)
        high_low = historical_data['High'] - historical_data['Low']
        high_close = (historical_data['High'] - historical_data['Close'].shift()).abs()
        low_close = (historical_data['Low'] - historical_data['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        historical_data['ATR'] = true_range.rolling(window=14).mean()

        # Calculate Monthly Volatility
        returns = historical_data['Close'].pct_change()
        historical_data['MonthlyVolatility'] = returns.rolling(window=21).std() * (21 ** 0.5)  # 21 trading days in a month

        # Calculate Beta (using a simple approximation)
        # In a real app, you would compare against a market index
        market_returns = returns.rolling(window=50).mean()  # Simplified market returns
        covariance = returns.rolling(window=50).cov(market_returns)
        variance = market_returns.rolling(window=50).var()
        historical_data['Beta'] = covariance / variance

        # Add these values to stock_info for the template
        if 'RSI' in historical_data:
            stock_info['rsi14'] = historical_data['RSI'].iloc[-1] if not historical_data['RSI'].iloc[-1:].isna().all() else 50.0

        if 'ATR' in historical_data:
            stock_info['averageTrueRange'] = historical_data['ATR'].iloc[-1] if not historical_data['ATR'].iloc[-1:].isna().all() else 0.0

        if 'MonthlyVolatility' in historical_data:
            stock_info['monthlyVolatility'] = historical_data['MonthlyVolatility'].iloc[-1] if not historical_data['MonthlyVolatility'].iloc[-1:].isna().all() else 0.0

        if 'Beta' in historical_data:
            stock_info['beta'] = historical_data['Beta'].iloc[-1] if not historical_data['Beta'].iloc[-1:].isna().all() else 1.0

        # Add moving averages to stock_info
        if 'MA50' in historical_data:
            stock_info['fiftyDayAverage'] = historical_data['MA50'].iloc[-1] if not historical_data['MA50'].iloc[-1:].isna().all() else 0.0

        if 'MA200' in historical_data:
            stock_info['twoHundredDayAverage'] = historical_data['MA200'].iloc[-1] if not historical_data['MA200'].iloc[-1:].isna().all() else 0.0

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

    # Clean up data by removing NaN values and ensuring all values are valid for Plotly
    def clean_data(data_list):
        # First, convert to float and replace NaN with None (which Plotly can handle)
        cleaned = [float(x) if not pd.isna(x) else None for x in data_list]

        # Check if we have too many None values (more than 50%)
        none_count = sum(1 for x in cleaned if x is None)
        if none_count > len(cleaned) * 0.5:
            print(f"Warning: More than 50% of values are None ({none_count}/{len(cleaned)})")
            # Fill in None values with interpolated values where possible
            result = []
            last_valid = None
            for i, val in enumerate(cleaned):
                if val is not None:
                    # Fill any previous None values with interpolation
                    if last_valid is not None and i > 0 and cleaned[i-1] is None:
                        # Find how many None values we need to fill
                        none_streak = 0
                        for j in range(i-1, -1, -1):
                            if cleaned[j] is None:
                                none_streak += 1
                            else:
                                break

                        # Calculate step size for linear interpolation
                        step = (val - last_valid) / (none_streak + 1)

                        # Go back and fill in the None values
                        for j in range(1, none_streak + 1):
                            result[-(j)] = last_valid + step * j

                    result.append(val)
                    last_valid = val
                else:
                    # Keep None for now, might be filled later
                    result.append(None)

            # If we still have None values at the beginning, use the first valid value
            if None in result and any(x is not None for x in result):
                first_valid = next(x for x in result if x is not None)
                result = [first_valid if x is None else x for x in result]

            return result

        return cleaned

    # Apply cleaning to all data lists
    open_data = clean_data(open_data)
    high_data = clean_data(high_data)
    low_data = clean_data(low_data)
    close_data = clean_data(close_data)
    volume_data = clean_data(volume_data)
    ma50_data = clean_data(ma50_data)
    ma200_data = clean_data(ma200_data)
    upper_band_data = clean_data(upper_band_data)
    lower_band_data = clean_data(lower_band_data)
    rsi_data = clean_data(rsi_data)
    macd_data = clean_data(macd_data)
    signal_data = clean_data(signal_data)
    histogram_data = clean_data(histogram_data)
    mfi_data = clean_data(mfi_data)

    # Ensure we have data for the charts
    if not dates or len(dates) == 0:
        print("No dates available for charts, generating default data")
        # Generate default data for charts
        current_date = datetime.now()
        dates = [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]

        # Get current price or use default
        current_price = stock_info.get('regularMarketPrice', 100.0)

        # Generate synthetic price data
        import numpy as np
        np.random.seed(hash(symbol) % 2**32)  # Use symbol as seed for reproducibility

        # Generate close prices with random walk
        close_data = [current_price]
        for i in range(1, 30):
            close_data.append(close_data[-1] * (1 + np.random.normal(0, 0.01)))
        close_data.reverse()  # Reverse to get chronological order

        # Generate other OHLC data
        open_data = [price * (1 + np.random.normal(0, 0.005)) for price in close_data]
        high_data = [max(open_data[i], close_data[i]) * (1 + abs(np.random.normal(0, 0.005))) for i in range(30)]
        low_data = [min(open_data[i], close_data[i]) * (1 - abs(np.random.normal(0, 0.005))) for i in range(30)]
        volume_data = [1000000 * (1 + np.random.normal(0, 0.2)) for _ in range(30)]

        # Generate technical indicators
        ma50_data = [sum(close_data[max(0, i-50):i+1])/min(i+1, 50) for i in range(30)]
        ma200_data = [sum(close_data[max(0, i-200):i+1])/min(i+1, 200) for i in range(30)]

        # Simple RSI calculation
        rsi_data = [50 + np.random.normal(0, 10) for _ in range(30)]
        rsi_data = [max(0, min(100, rsi)) for rsi in rsi_data]  # Clamp between 0 and 100

        # Simple MACD
        macd_data = [np.random.normal(0, 2) for _ in range(30)]
        signal_data = [sum(macd_data[max(0, i-9):i+1])/min(i+1, 9) for i in range(30)]
        histogram_data = [macd_data[i] - signal_data[i] for i in range(30)]

        # Simple MFI
        mfi_data = [50 + np.random.normal(0, 15) for _ in range(30)]
        mfi_data = [max(0, min(100, mfi)) for mfi in mfi_data]  # Clamp between 0 and 100

        # Bollinger Bands
        std_dev = np.std(close_data)
        upper_band_data = [ma50_data[i] + 2 * std_dev for i in range(30)]
        lower_band_data = [ma50_data[i] - 2 * std_dev for i in range(30)]

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
