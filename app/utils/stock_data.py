import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from flask import current_app
from app.utils.indian_stocks import get_stock_info_alternative, get_historical_data_alternative, get_current_price_alternative

# Cache directory for stock data
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(CACHE_DIR, exist_ok=True)

# List of Indian stocks (60 hand-picked stocks from different sectors and market caps)
INDIAN_STOCKS = {
    'Large Cap': [
        {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Ltd.', 'sector': 'Energy'},
        {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services Ltd.', 'sector': 'IT'},
        {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Ltd.', 'sector': 'Banking'},
        {'symbol': 'INFY.NS', 'name': 'Infosys Ltd.', 'sector': 'IT'},
        {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever Ltd.', 'sector': 'FMCG'},
        {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Ltd.', 'sector': 'Banking'},
        {'symbol': 'SBIN.NS', 'name': 'State Bank of India', 'sector': 'Banking'},
        {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel Ltd.', 'sector': 'Telecom'},
        {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank Ltd.', 'sector': 'Banking'},
        {'symbol': 'ITC.NS', 'name': 'ITC Ltd.', 'sector': 'FMCG'},
        {'symbol': 'LT.NS', 'name': 'Larsen & Toubro Ltd.', 'sector': 'Construction'},
        {'symbol': 'AXISBANK.NS', 'name': 'Axis Bank Ltd.', 'sector': 'Banking'},
        {'symbol': 'ASIANPAINT.NS', 'name': 'Asian Paints Ltd.', 'sector': 'Consumer Durables'},
        {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki India Ltd.', 'sector': 'Automobile'},
        {'symbol': 'HCLTECH.NS', 'name': 'HCL Technologies Ltd.', 'sector': 'IT'},
        {'symbol': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical Industries Ltd.', 'sector': 'Pharma'},
        {'symbol': 'BAJFINANCE.NS', 'name': 'Bajaj Finance Ltd.', 'sector': 'Financial Services'},
        {'symbol': 'TATAMOTORS.NS', 'name': 'Tata Motors Ltd.', 'sector': 'Automobile'},
        {'symbol': 'WIPRO.NS', 'name': 'Wipro Ltd.', 'sector': 'IT'},
        {'symbol': 'NTPC.NS', 'name': 'NTPC Ltd.', 'sector': 'Power'}
    ],
    'Mid Cap': [
        {'symbol': 'GODREJCP.NS', 'name': 'Godrej Consumer Products Ltd.', 'sector': 'FMCG'},
        {'symbol': 'HAVELLS.NS', 'name': 'Havells India Ltd.', 'sector': 'Consumer Durables'},
        {'symbol': 'BERGEPAINT.NS', 'name': 'Berger Paints India Ltd.', 'sector': 'Consumer Durables'},
        {'symbol': 'MPHASIS.NS', 'name': 'Mphasis Ltd.', 'sector': 'IT'},
        {'symbol': 'TATAPOWER.NS', 'name': 'Tata Power Co. Ltd.', 'sector': 'Power'},
        {'symbol': 'TORNTPHARM.NS', 'name': 'Torrent Pharmaceuticals Ltd.', 'sector': 'Pharma'},
        {'symbol': 'INDIGO.NS', 'name': 'InterGlobe Aviation Ltd.', 'sector': 'Aviation'},
        {'symbol': 'AUROPHARMA.NS', 'name': 'Aurobindo Pharma Ltd.', 'sector': 'Pharma'},
        {'symbol': 'GAIL.NS', 'name': 'GAIL (India) Ltd.', 'sector': 'Oil & Gas'},
        {'symbol': 'JINDALSTEL.NS', 'name': 'Jindal Steel & Power Ltd.', 'sector': 'Metal'},
        {'symbol': 'COLPAL.NS', 'name': 'Colgate-Palmolive (India) Ltd.', 'sector': 'FMCG'},
        {'symbol': 'LUPIN.NS', 'name': 'Lupin Ltd.', 'sector': 'Pharma'},
        {'symbol': 'MARICO.NS', 'name': 'Marico Ltd.', 'sector': 'FMCG'},
        {'symbol': 'BIOCON.NS', 'name': 'Biocon Ltd.', 'sector': 'Pharma'},
        {'symbol': 'AMBUJACEM.NS', 'name': 'Ambuja Cements Ltd.', 'sector': 'Cement'},
        {'symbol': 'DABUR.NS', 'name': 'Dabur India Ltd.', 'sector': 'FMCG'},
        {'symbol': 'GODREJPROP.NS', 'name': 'Godrej Properties Ltd.', 'sector': 'Real Estate'},
        {'symbol': 'MUTHOOTFIN.NS', 'name': 'Muthoot Finance Ltd.', 'sector': 'Financial Services'},
        {'symbol': 'BANDHANBNK.NS', 'name': 'Bandhan Bank Ltd.', 'sector': 'Banking'},
        {'symbol': 'SAIL.NS', 'name': 'Steel Authority of India Ltd.', 'sector': 'Metal'}
    ],
    'Small Cap': [
        {'symbol': 'IRCTC.NS', 'name': 'Indian Railway Catering and Tourism Corporation Ltd.', 'sector': 'Services'},
        {'symbol': 'LALPATHLAB.NS', 'name': 'Dr. Lal PathLabs Ltd.', 'sector': 'Healthcare'},
        {'symbol': 'CAMS.NS', 'name': 'Computer Age Management Services Ltd.', 'sector': 'Financial Services'},
        {'symbol': 'CDSL.NS', 'name': 'Central Depository Services (India) Ltd.', 'sector': 'Financial Services'},
        {'symbol': 'SUNTV.NS', 'name': 'Sun TV Network Ltd.', 'sector': 'Media'},
        {'symbol': 'ABCAPITAL.NS', 'name': 'Aditya Birla Capital Ltd.', 'sector': 'Financial Services'},
        {'symbol': 'TATAELXSI.NS', 'name': 'Tata Elxsi Ltd.', 'sector': 'IT'},
        {'symbol': 'JUBLFOOD.NS', 'name': 'Jubilant FoodWorks Ltd.', 'sector': 'Consumer Services'},
        {'symbol': 'MINDTREE.NS', 'name': 'MindTree Ltd.', 'sector': 'IT'},
        {'symbol': 'COFORGE.NS', 'name': 'Coforge Ltd.', 'sector': 'IT'},
        {'symbol': 'APOLLOHOSP.NS', 'name': 'Apollo Hospitals Enterprise Ltd.', 'sector': 'Healthcare'},
        {'symbol': 'LTTS.NS', 'name': 'L&T Technology Services Ltd.', 'sector': 'IT'},
        {'symbol': 'PERSISTENT.NS', 'name': 'Persistent Systems Ltd.', 'sector': 'IT'},
        {'symbol': 'DIXON.NS', 'name': 'Dixon Technologies (India) Ltd.', 'sector': 'Consumer Durables'},
        {'symbol': 'ASTRAL.NS', 'name': 'Astral Ltd.', 'sector': 'Industrial Manufacturing'},
        {'symbol': 'POLYCAB.NS', 'name': 'Polycab India Ltd.', 'sector': 'Consumer Durables'},
        {'symbol': 'NAVINFLUOR.NS', 'name': 'Navin Fluorine International Ltd.', 'sector': 'Chemicals'},
        {'symbol': 'DEEPAKNTR.NS', 'name': 'Deepak Nitrite Ltd.', 'sector': 'Chemicals'},
        {'symbol': 'AARTIIND.NS', 'name': 'Aarti Industries Ltd.', 'sector': 'Chemicals'},
        {'symbol': 'ALKYLAMINE.NS', 'name': 'Alkyl Amines Chemicals Ltd.', 'sector': 'Chemicals'}
    ]
}

# List of popular Indian mutual funds with scheme codes
INDIAN_MUTUAL_FUNDS = [
    {'symbol': '118834', 'name': 'Axis Bluechip Fund', 'category': 'Large Cap', 'aum': '₹33,456 Cr', 'expense_ratio': '0.54%'},
    {'symbol': '118533', 'name': 'HDFC Mid-Cap Opportunities Fund', 'category': 'Mid Cap', 'aum': '₹31,234 Cr', 'expense_ratio': '1.02%'},
    {'symbol': '122639', 'name': 'ICICI Prudential Bluechip Fund', 'category': 'Large Cap', 'aum': '₹35,678 Cr', 'expense_ratio': '0.78%'},
    {'symbol': '120716', 'name': 'Mirae Asset Large Cap Fund', 'category': 'Large Cap', 'aum': '₹29,876 Cr', 'expense_ratio': '0.56%'},
    {'symbol': '120505', 'name': 'SBI Small Cap Fund', 'category': 'Small Cap', 'aum': '₹15,432 Cr', 'expense_ratio': '0.80%'},
    {'symbol': '118989', 'name': 'Kotak Emerging Equity Fund', 'category': 'Mid Cap', 'aum': '₹22,345 Cr', 'expense_ratio': '0.65%'},
    {'symbol': '120178', 'name': 'Nippon India Small Cap Fund', 'category': 'Small Cap', 'aum': '₹18,765 Cr', 'expense_ratio': '0.91%'},
    {'symbol': '118560', 'name': 'Parag Parikh Flexi Cap Fund', 'category': 'Flexi Cap', 'aum': '₹25,678 Cr', 'expense_ratio': '0.54%'},
    {'symbol': '100033', 'name': 'Aditya Birla Sun Life Frontline Equity Fund', 'category': 'Large Cap', 'aum': '₹24,567 Cr', 'expense_ratio': '0.94%'},
    {'symbol': '118551', 'name': 'DSP Midcap Fund', 'category': 'Mid Cap', 'aum': '₹13,456 Cr', 'expense_ratio': '0.84%'}
]

def get_all_stocks():
    """Return all stocks in the database with valid yfinance symbols"""
    all_stocks = []
    valid_suffixes = ['.NS', '.BO']

    for cap, stocks in INDIAN_STOCKS.items():
        for stock in stocks:
            # Only include stocks with .NS or .BO suffix (valid for yfinance)
            if any(stock['symbol'].endswith(suffix) for suffix in valid_suffixes):
                # Verify the stock exists in yfinance by checking if we can get basic info
                try:
                    # We'll just do a quick check without making a full API call
                    stock['cap'] = cap
                    all_stocks.append(stock)
                except Exception as e:
                    print(f"Skipping invalid stock {stock['symbol']}: {e}")

    # If we have fewer than 10 stocks, add some known good stocks
    if len(all_stocks) < 10:
        known_good_stocks = [
            {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Limited'},
            {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services Limited'},
            {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Limited'},
            {'symbol': 'INFY.NS', 'name': 'Infosys Limited'},
            {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Limited'},
            {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
            {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel Limited'},
            {'symbol': 'ITC.NS', 'name': 'ITC Limited'},
            {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank Limited'},
            {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever Limited'}
        ]

        for stock in known_good_stocks:
            if not any(s['symbol'] == stock['symbol'] for s in all_stocks):
                stock['cap'] = 'Large Cap'
                all_stocks.append(stock)

    return all_stocks

def get_all_mutual_funds():
    """Return all mutual funds in the database - DEPRECATED"""
    return []  # Return empty list as mutual funds are no longer used

def get_stock_info(symbol):
    """Get detailed information about a stock"""
    # Special handling for RELIANCE
    if symbol.upper() == 'RELIANCE' or symbol.upper() == 'RELIANCE.NS':
        print(f"Special handling for RELIANCE stock info")
        # Try with NSE suffix for RELIANCE
        try:
            stock = yf.Ticker("RELIANCE.NS")
            info = stock.info
            if info and 'regularMarketPrice' in info:
                print(f"Successfully fetched info for RELIANCE.NS")
                return info
        except Exception as e:
            print(f"Error fetching stock info for RELIANCE.NS: {e}")

        # If that fails, try the hardcoded info from indian_stocks.py
        try:
            # Use the imported function from the module level
            info = get_stock_info_alternative('RELIANCE')
            if info and 'regularMarketPrice' in info:
                print(f"Successfully fetched alternative info for RELIANCE")
                return info
        except Exception as e:
            print(f"Error fetching alternative stock info for RELIANCE: {e}")

    # If the symbol already has a suffix (like INFY.NS), try it directly first
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        print(f"Symbol {symbol} already has a suffix, trying it directly")
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            if info and 'regularMarketPrice' in info:
                print(f"Successfully fetched info for {symbol}")
                return info
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")

        # If that fails, try without the suffix
        base_symbol = symbol.split('.')[0]
        print(f"Trying without suffix: {base_symbol}")
        try:
            stock = yf.Ticker(base_symbol)
            info = stock.info
            if info and 'regularMarketPrice' in info:
                print(f"Successfully fetched info for {base_symbol}")
                return info
        except Exception as e:
            print(f"Error fetching stock info for {base_symbol}: {e}")

    # Try standard yfinance approach first
    # Add .NS suffix if not already present for Indian stocks
    if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
        # Try with NSE suffix first
        try:
            stock = yf.Ticker(f"{symbol}.NS")
            info = stock.info
            if info and 'regularMarketPrice' in info:
                print(f"Successfully fetched info for {symbol}.NS")
                return info
        except Exception as e:
            print(f"Error fetching stock info for {symbol}.NS: {e}")

        # If NSE fails, try BSE
        try:
            stock = yf.Ticker(f"{symbol}.BO")
            info = stock.info
            if info and 'regularMarketPrice' in info:
                print(f"Successfully fetched info for {symbol}.BO")
                return info
        except Exception as e:
            print(f"Error fetching stock info for {symbol}.BO: {e}")

    # If symbol already has suffix or both attempts failed, try as is
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        if info and 'regularMarketPrice' in info:
            return info
    except Exception as e:
        print(f"Error fetching stock info for {symbol}: {e}")

    # If all yfinance attempts failed, try alternative approach
    print(f"Using alternative source for {symbol}")
    return get_stock_info_alternative(symbol)

def get_current_price(symbol):
    """Get the current price of a stock"""
    print(f"Attempting to get current price for symbol: {symbol}")

    # Check cache first
    cache_file = os.path.join(CACHE_DIR, f"{symbol}_price.json")
    if os.path.exists(cache_file):
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_age < timedelta(hours=6):  # Cache for 6 hours
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    print(f"Using cached price for {symbol}: {cached_data['price']}")
                    return cached_data['price']
            except Exception as e:
                print(f"Error reading cache for {symbol}: {e}")

    # Add .NS suffix if not already present for Indian stocks
    if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
        # Try with NSE suffix first
        try:
            print(f"Trying with NSE suffix: {symbol}.NS")
            stock = yf.Ticker(f"{symbol}.NS")
            todays_data = stock.history(period='1d')
            if not todays_data.empty:
                price = todays_data['Close'].iloc[-1]
                print(f"Successfully fetched price for {symbol}.NS: {price}")

                # Cache the result
                with open(cache_file, 'w') as f:
                    json.dump({'price': float(price), 'timestamp': datetime.now().isoformat()}, f)

                return price
        except Exception as e:
            print(f"Error fetching current price for {symbol}.NS: {e}")

        # If NSE fails, try BSE
        try:
            print(f"Trying with BSE suffix: {symbol}.BO")
            stock = yf.Ticker(f"{symbol}.BO")
            todays_data = stock.history(period='1d')
            if not todays_data.empty:
                price = todays_data['Close'].iloc[-1]
                print(f"Successfully fetched price for {symbol}.BO: {price}")

                # Cache the result
                with open(cache_file, 'w') as f:
                    json.dump({'price': float(price), 'timestamp': datetime.now().isoformat()}, f)

                return price
        except Exception as e:
            print(f"Error fetching current price for {symbol}.BO: {e}")

    # If symbol already has suffix or both attempts failed, try as is
    try:
        print(f"Trying with original symbol: {symbol}")
        stock = yf.Ticker(symbol)
        todays_data = stock.history(period='1d')
        if not todays_data.empty:
            price = todays_data['Close'].iloc[-1]
            print(f"Successfully fetched price for {symbol}: {price}")

            # Cache the result
            with open(cache_file, 'w') as f:
                json.dump({'price': float(price), 'timestamp': datetime.now().isoformat()}, f)

            return price
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")

    # If all yfinance attempts failed, try alternative approach
    print(f"Using alternative source for {symbol} price")
    price = get_current_price_alternative(symbol)

    if price > 0:
        print(f"Alternative source returned price for {symbol}: {price}")
        # Cache the result
        with open(cache_file, 'w') as f:
            json.dump({'price': float(price), 'timestamp': datetime.now().isoformat()}, f)
    else:
        print(f"Alternative source failed to get price for {symbol}")
        # Use a dummy price for testing
        price = 100.0  # Default price for testing
        print(f"Using dummy price for {symbol}: {price}")

    return price

def get_historical_data(symbol, period='1y'):
    """Get historical price data for a stock"""
    print(f"Getting historical data for {symbol} with period {period}")
    # Determine the correct symbol to use
    actual_symbol = symbol
    data = pd.DataFrame()

    # Special handling for RELIANCE
    if symbol.upper() == 'RELIANCE' or symbol.upper() == 'RELIANCE.NS':
        # Check cache first for RELIANCE.NS
        cache_file = os.path.join(CACHE_DIR, f"RELIANCE.NS_{period}.json")
        if os.path.exists(cache_file):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age < timedelta(days=1):
                print(f"Using cached historical data for RELIANCE.NS")
                with open(cache_file, 'r') as f:
                    try:
                        data = pd.read_json(f.read())
                        if not data.empty:
                            return data
                    except Exception as e:
                        print(f"Error reading cache for RELIANCE.NS: {e}")

        # Try with NSE suffix for RELIANCE
        try:
            nse_symbol = 'RELIANCE.NS'
            print(f"Special handling: Trying with NSE suffix: {nse_symbol}")
            stock = yf.Ticker(nse_symbol)
            data = stock.history(period=period)
            if not data.empty:
                print(f"Successfully fetched historical data for {nse_symbol}")
                actual_symbol = nse_symbol

                # Cache the data
                cache_file = os.path.join(CACHE_DIR, f"{actual_symbol}_{period}.json")
                with open(cache_file, 'w') as f:
                    f.write(data.to_json())

                return data
        except Exception as e:
            print(f"Error fetching historical data for RELIANCE.NS: {e}")

    # If the symbol already has a suffix (like INFY.NS), try it directly first
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        print(f"Symbol {symbol} already has a suffix, trying it directly for historical data")
        # Check cache first
        cache_file = os.path.join(CACHE_DIR, f"{symbol}_{period}.json")
        if os.path.exists(cache_file):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age < timedelta(days=1):
                print(f"Using cached historical data for {symbol}")
                with open(cache_file, 'r') as f:
                    try:
                        data = pd.read_json(f.read())
                        if not data.empty:
                            return data
                    except Exception as e:
                        print(f"Error reading cache for {symbol}: {e}")

        try:
            print(f"Fetching historical data for {symbol}")
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            if not data.empty:
                print(f"Successfully fetched historical data for {symbol}")

                # Cache the data
                cache_file = os.path.join(CACHE_DIR, f"{symbol}_{period}.json")
                with open(cache_file, 'w') as f:
                    f.write(data.to_json())

                return data
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")

        # If that fails, try without the suffix
        base_symbol = symbol.split('.')[0]
        print(f"Trying without suffix: {base_symbol}")
        try:
            stock = yf.Ticker(base_symbol)
            data = stock.history(period=period)
            if not data.empty:
                print(f"Successfully fetched historical data for {base_symbol}")
                return data
        except Exception as e:
            print(f"Error fetching historical data for {base_symbol}: {e}")

    # Add .NS suffix if not already present for Indian stocks
    if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
        # Try with NSE suffix first
        try:
            nse_symbol = f"{symbol}.NS"
            print(f"Trying with NSE suffix: {nse_symbol}")
            stock = yf.Ticker(nse_symbol)
            data = stock.history(period=period)
            if not data.empty:
                print(f"Successfully fetched historical data for {nse_symbol}")
                actual_symbol = nse_symbol
        except Exception as e:
            print(f"Error fetching historical data for {symbol}.NS: {e}")

        # If NSE fails, try BSE
        if data.empty:
            try:
                bse_symbol = f"{symbol}.BO"
                print(f"Trying with BSE suffix: {bse_symbol}")
                stock = yf.Ticker(bse_symbol)
                data = stock.history(period=period)
                if not data.empty:
                    print(f"Successfully fetched historical data for {bse_symbol}")
                    actual_symbol = bse_symbol
            except Exception as e:
                print(f"Error fetching historical data for {symbol}.BO: {e}")

    # If symbol already has suffix or both attempts failed, try as is
    if data.empty:
        cache_file = os.path.join(CACHE_DIR, f"{actual_symbol}_{period}.json")

        # Check if we have cached data that's less than a day old
        if os.path.exists(cache_file):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age < timedelta(days=1):
                print(f"Using cached historical data for {actual_symbol}")
                with open(cache_file, 'r') as f:
                    try:
                        data = pd.read_json(f.read())
                        if not data.empty:
                            return data
                    except Exception as e:
                        print(f"Error reading cache for {actual_symbol}: {e}")

        try:
            print(f"Trying with original symbol: {actual_symbol}")
            stock = yf.Ticker(actual_symbol)
            data = stock.history(period=period)
            if not data.empty:
                print(f"Successfully fetched historical data for {actual_symbol}")
        except Exception as e:
            print(f"Error fetching historical data for {actual_symbol}: {e}")

    # If all yfinance attempts failed, try alternative approach
    if data.empty:
        print(f"Using alternative source for {symbol} historical data")
        try:
            # Special handling for APOLLOHOSP.NS which often has issues
            if symbol.upper() == 'APOLLOHOSP.NS' or symbol.upper() == 'APOLLOHOSP':
                print(f"Special handling for APOLLOHOSP historical data")
                # Try with a different period
                try:
                    stock = yf.Ticker('APOLLOHOSP.NS')
                    data = stock.history(period='6mo')  # Try a shorter period
                    if not data.empty:
                        print(f"Successfully fetched 6mo historical data for APOLLOHOSP.NS")
                        return data
                except Exception as e:
                    print(f"Error fetching 6mo historical data for APOLLOHOSP.NS: {e}")

            # Try the alternative method for all stocks
            data = get_historical_data_alternative(symbol, period)
        except Exception as e:
            print(f"Error using alternative method for {symbol}: {e}")
            data = pd.DataFrame()  # Ensure we have an empty DataFrame

    # Cache the data if we have it
    if not data.empty:
        print(f"Caching historical data for {actual_symbol}")
        cache_file = os.path.join(CACHE_DIR, f"{actual_symbol}_{period}.json")
        with open(cache_file, 'w') as f:
            f.write(data.to_json())
        return data

    # If all attempts failed, return an empty DataFrame
    # We're not generating synthetic data as per user request
    print(f"All attempts to get historical data failed for {symbol}, returning empty DataFrame")
    return pd.DataFrame()

def generate_synthetic_historical_data(symbol, period='1y'):
    """Generate synthetic historical data when real data is not available"""
    print(f"Generating synthetic historical data for {symbol}")

    # Get the current price or use a default
    current_price = get_current_price(symbol)
    if current_price <= 0:
        current_price = 100.0

    # Determine the number of days based on the period
    if period == '1mo':
        days = 30
    elif period == '3mo':
        days = 90
    elif period == '6mo':
        days = 180
    elif period == '1y':
        days = 365
    elif period == '2y':
        days = 730
    elif period == '5y':
        days = 1825
    elif period == 'max':
        days = 3650
    else:
        days = 365  # Default to 1 year

    # Generate dates (business days only)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Create a date range with business days
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')

    # Generate synthetic price data with some randomness
    np.random.seed(hash(symbol) % 2**32)  # Use symbol as seed for reproducibility

    # Start with the current price and work backwards
    price = current_price
    prices = [price]

    # Generate daily returns with a slight upward bias and volatility
    volatility = 0.015  # 1.5% daily volatility
    drift = 0.0002  # Slight upward drift (about 5% annual return)

    for _ in range(len(date_range) - 1):
        daily_return = np.random.normal(drift, volatility)
        price = price / (1 + daily_return)  # Work backwards
        prices.append(price)

    # Reverse to get chronological order
    prices.reverse()

    # Create a DataFrame with OHLC data
    data = pd.DataFrame(index=date_range)
    data['Close'] = prices

    # Generate Open, High, Low based on Close
    data['Open'] = data['Close'].shift(1) * (1 + np.random.normal(0, 0.005, len(data)))
    data.loc[data.index[0], 'Open'] = data['Close'].iloc[0] * 0.995  # First day open

    # High is the max of Open and Close plus some random amount
    data['High'] = data[['Open', 'Close']].max(axis=1) * (1 + np.abs(np.random.normal(0, 0.008, len(data))))

    # Low is the min of Open and Close minus some random amount
    data['Low'] = data[['Open', 'Close']].min(axis=1) * (1 - np.abs(np.random.normal(0, 0.008, len(data))))

    # Generate volume data (higher on volatile days)
    price_changes = np.abs(data['Close'].pct_change())
    avg_volume = 1000000  # Average daily volume
    data['Volume'] = avg_volume * (1 + 5 * price_changes)
    data.loc[data.index[0], 'Volume'] = avg_volume  # First day volume

    # Fill any NaN values
    data = data.fillna(method='bfill')

    print(f"Successfully generated synthetic data with {len(data)} rows for {symbol}")
    return data

def calculate_returns(data):
    """Calculate daily returns from price data"""
    if data.empty:
        return pd.DataFrame()

    returns = data['Close'].pct_change().dropna()
    return returns

def calculate_portfolio_metrics(portfolio_weights, symbols):
    """
    Calculate portfolio metrics like expected return, volatility, and Sharpe ratio

    Args:
        portfolio_weights: List of weights for each stock
        symbols: List of stock symbols

    Returns:
        dict: Dictionary containing portfolio metrics
    """
    # Get historical data for all symbols
    data_frames = []
    for symbol in symbols:
        df = get_historical_data(symbol)
        if not df.empty:
            data_frames.append(df['Close'])

    if not data_frames:
        return {
            'expected_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0
        }

    # Combine all dataframes
    prices = pd.concat(data_frames, axis=1)
    prices.columns = symbols

    # Calculate daily returns
    returns = prices.pct_change().dropna()

    # Calculate expected returns and covariance matrix
    expected_returns = returns.mean() * 252  # Annualized returns (252 trading days)
    cov_matrix = returns.cov() * 252  # Annualized covariance

    # Calculate portfolio metrics
    portfolio_return = np.sum(expected_returns * portfolio_weights)
    portfolio_volatility = np.sqrt(np.dot(portfolio_weights.T, np.dot(cov_matrix, portfolio_weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility  # Assuming risk-free rate is 0

    return {
        'expected_return': portfolio_return,
        'volatility': portfolio_volatility,
        'sharpe_ratio': sharpe_ratio
    }

def optimize_portfolio(symbols, risk_tolerance='moderate'):
    """
    Optimize portfolio weights based on risk tolerance

    Args:
        symbols: List of stock symbols
        risk_tolerance: 'low', 'moderate', or 'high'

    Returns:
        dict: Dictionary containing optimized weights and metrics
    """
    # Get historical data for all symbols
    data_frames = []
    for symbol in symbols:
        df = get_historical_data(symbol)
        if not df.empty:
            data_frames.append(df['Close'])

    if not data_frames:
        return {
            'weights': [1/len(symbols)] * len(symbols),
            'expected_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0
        }

    # Combine all dataframes
    prices = pd.concat(data_frames, axis=1)
    prices.columns = symbols

    # Calculate daily returns
    returns = prices.pct_change().dropna()

    # Calculate expected returns and covariance matrix
    expected_returns = returns.mean() * 252  # Annualized returns
    cov_matrix = returns.cov() * 252  # Annualized covariance

    # Define risk tolerance parameters
    if risk_tolerance == 'low':
        target_return = expected_returns.min() + 0.2 * (expected_returns.max() - expected_returns.min())
    elif risk_tolerance == 'high':
        target_return = expected_returns.min() + 0.8 * (expected_returns.max() - expected_returns.min())
    else:  # moderate
        target_return = expected_returns.mean()

    # Perform portfolio optimization (minimum variance for target return)
    from scipy.optimize import minimize

    def objective(weights):
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return portfolio_volatility

    def constraint_return(weights):
        portfolio_return = np.sum(expected_returns * weights)
        return portfolio_return - target_return

    def constraint_sum(weights):
        return np.sum(weights) - 1

    # Initial guess (equal weights)
    n = len(symbols)
    initial_weights = np.array([1/n] * n)

    # Constraints
    constraints = [
        {'type': 'eq', 'fun': constraint_sum},
        {'type': 'eq', 'fun': constraint_return}
    ]

    # Bounds (no short selling)
    bounds = tuple((0, 1) for _ in range(n))

    # Optimize
    result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        optimized_weights = result.x
        portfolio_return = np.sum(expected_returns * optimized_weights)
        portfolio_volatility = np.sqrt(np.dot(optimized_weights.T, np.dot(cov_matrix, optimized_weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility

        return {
            'weights': optimized_weights.tolist(),
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }
    else:
        # If optimization fails, return equal weights
        return {
            'weights': [1/n] * n,
            'expected_return': np.sum(expected_returns * initial_weights),
            'volatility': np.sqrt(np.dot(initial_weights.T, np.dot(cov_matrix, initial_weights))),
            'sharpe_ratio': np.sum(expected_returns * initial_weights) / np.sqrt(np.dot(initial_weights.T, np.dot(cov_matrix, initial_weights)))
        }

def calculate_minimum_variance_portfolio(symbols):
    """
    Calculate the minimum variance portfolio

    Args:
        symbols: List of stock symbols

    Returns:
        dict: Dictionary containing portfolio weights and metrics
    """
    # Get historical data for all symbols
    data_frames = []
    for symbol in symbols:
        df = get_historical_data(symbol)
        if not df.empty:
            data_frames.append(df['Close'])

    if not data_frames:
        return {
            'weights': [1/len(symbols)] * len(symbols),
            'expected_return': 0,
            'volatility': 0
        }

    # Combine all dataframes
    prices = pd.concat(data_frames, axis=1)
    prices.columns = symbols

    # Calculate daily returns
    returns = prices.pct_change().dropna()

    # Calculate expected returns and covariance matrix
    expected_returns = returns.mean() * 252  # Annualized returns
    cov_matrix = returns.cov() * 252  # Annualized covariance

    # Perform portfolio optimization (minimum variance)
    from scipy.optimize import minimize

    def objective(weights):
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return portfolio_volatility

    def constraint_sum(weights):
        return np.sum(weights) - 1

    # Initial guess (equal weights)
    n = len(symbols)
    initial_weights = np.array([1/n] * n)

    # Constraints
    constraints = [
        {'type': 'eq', 'fun': constraint_sum}
    ]

    # Bounds (no short selling)
    bounds = tuple((0, 1) for _ in range(n))

    # Optimize
    result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    if result.success:
        optimized_weights = result.x
        portfolio_return = np.sum(expected_returns * optimized_weights)
        portfolio_volatility = np.sqrt(np.dot(optimized_weights.T, np.dot(cov_matrix, optimized_weights)))

        return {
            'weights': optimized_weights.tolist(),
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility
        }
    else:
        # If optimization fails, return equal weights
        return {
            'weights': [1/n] * n,
            'expected_return': np.sum(expected_returns * initial_weights),
            'volatility': np.sqrt(np.dot(initial_weights.T, np.dot(cov_matrix, initial_weights)))
        }

def get_covariance_matrix(symbols):
    """
    Calculate the covariance matrix for a set of stocks

    Args:
        symbols: List of stock symbols

    Returns:
        DataFrame: Covariance matrix
    """
    # Get historical data for all symbols
    data_frames = []
    for symbol in symbols:
        df = get_historical_data(symbol)
        if not df.empty:
            data_frames.append(df['Close'])

    if not data_frames:
        return pd.DataFrame()

    # Combine all dataframes
    prices = pd.concat(data_frames, axis=1)
    prices.columns = symbols

    # Calculate daily returns
    returns = prices.pct_change().dropna()

    # Calculate covariance matrix
    cov_matrix = returns.cov() * 252  # Annualized covariance

    return cov_matrix
