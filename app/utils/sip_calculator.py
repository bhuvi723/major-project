def calculate_sip(monthly_investment, expected_return_rate, time_period_years, inflation_rate=0):
    """
    Calculate SIP returns with optional inflation adjustment
    
    Args:
        monthly_investment: Monthly investment amount
        expected_return_rate: Expected annual return rate (in percentage)
        time_period_years: Investment time period in years
        inflation_rate: Annual inflation rate (in percentage)
    
    Returns:
        dict: Dictionary containing investment details and returns
    """
    # Convert percentages to decimals
    expected_return_rate_monthly = (expected_return_rate / 100) / 12
    inflation_rate_monthly = (inflation_rate / 100) / 12
    
    # Calculate number of months
    time_period_months = time_period_years * 12
    
    # Initialize variables
    total_investment = 0
    future_value = 0
    
    # Calculate future value with monthly compounding
    for month in range(1, time_period_months + 1):
        total_investment += monthly_investment
        future_value = (future_value + monthly_investment) * (1 + expected_return_rate_monthly)
    
    # Calculate inflation-adjusted future value
    inflation_adjusted_future_value = future_value
    if inflation_rate > 0:
        inflation_factor = (1 + inflation_rate / 100) ** time_period_years
        inflation_adjusted_future_value = future_value / inflation_factor
    
    # Calculate wealth gained
    wealth_gained = future_value - total_investment
    inflation_adjusted_wealth_gained = inflation_adjusted_future_value - total_investment
    
    # Calculate absolute returns
    absolute_returns = (future_value / total_investment - 1) * 100
    inflation_adjusted_absolute_returns = (inflation_adjusted_future_value / total_investment - 1) * 100
    
    # Calculate CAGR (Compound Annual Growth Rate)
    cagr = ((future_value / total_investment) ** (1 / time_period_years) - 1) * 100
    inflation_adjusted_cagr = ((inflation_adjusted_future_value / total_investment) ** (1 / time_period_years) - 1) * 100
    
    return {
        'monthly_investment': monthly_investment,
        'time_period_years': time_period_years,
        'time_period_months': time_period_months,
        'expected_return_rate': expected_return_rate,
        'inflation_rate': inflation_rate,
        'total_investment': total_investment,
        'future_value': future_value,
        'inflation_adjusted_future_value': inflation_adjusted_future_value,
        'wealth_gained': wealth_gained,
        'inflation_adjusted_wealth_gained': inflation_adjusted_wealth_gained,
        'absolute_returns': absolute_returns,
        'inflation_adjusted_absolute_returns': inflation_adjusted_absolute_returns,
        'cagr': cagr,
        'inflation_adjusted_cagr': inflation_adjusted_cagr
    }

def generate_sip_growth_data(monthly_investment, expected_return_rate, time_period_years, inflation_rate=0):
    """
    Generate year-by-year SIP growth data for visualization
    
    Args:
        monthly_investment: Monthly investment amount
        expected_return_rate: Expected annual return rate (in percentage)
        time_period_years: Investment time period in years
        inflation_rate: Annual inflation rate (in percentage)
    
    Returns:
        dict: Dictionary containing year-by-year investment data
    """
    # Convert percentages to decimals
    expected_return_rate_monthly = (expected_return_rate / 100) / 12
    inflation_rate_monthly = (inflation_rate / 100) / 12
    
    # Initialize variables
    total_investment = 0
    future_value = 0
    
    # Initialize data lists
    years = []
    invested_amounts = []
    future_values = []
    inflation_adjusted_values = []
    
    # Calculate year-by-year growth
    for month in range(1, time_period_years * 12 + 1):
        total_investment += monthly_investment
        future_value = (future_value + monthly_investment) * (1 + expected_return_rate_monthly)
        
        # Record data at the end of each year
        if month % 12 == 0:
            year = month // 12
            years.append(year)
            invested_amounts.append(total_investment)
            future_values.append(future_value)
            
            # Calculate inflation-adjusted value
            if inflation_rate > 0:
                inflation_factor = (1 + inflation_rate / 100) ** year
                inflation_adjusted_value = future_value / inflation_factor
            else:
                inflation_adjusted_value = future_value
            
            inflation_adjusted_values.append(inflation_adjusted_value)
    
    return {
        'years': years,
        'invested_amounts': invested_amounts,
        'future_values': future_values,
        'inflation_adjusted_values': inflation_adjusted_values
    }
