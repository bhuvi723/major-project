from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.portfolio import Portfolio, Holding
from app.models.transaction import Transaction
from app.utils.stock_data import (
    get_historical_data, calculate_portfolio_metrics, 
    optimize_portfolio, calculate_minimum_variance_portfolio,
    get_covariance_matrix, get_current_price, get_all_stocks
)
from app import db
import pandas as pd
import json

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')

@portfolio_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's portfolios
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    
    # Calculate total portfolio value
    total_value = sum(portfolio.total_value() for portfolio in portfolios)
    total_investment = sum(portfolio.total_investment() for portfolio in portfolios)
    total_return = total_value - total_investment
    
    # Calculate return percentage
    if total_investment > 0:
        return_percentage = (total_return / total_investment) * 100
    else:
        return_percentage = 0
    
    # Get portfolio performance data for charts
    portfolio_data = []
    for portfolio in portfolios:
        holdings = Holding.query.filter_by(portfolio_id=portfolio.id).all()
        symbols = [holding.symbol for holding in holdings]
        weights = [holding.quantity * get_current_price(holding.symbol) / portfolio.total_value() 
                  for holding in holdings] if portfolio.total_value() > 0 else []
        
        if symbols and weights:
            # Convert weights to numpy array for calculations
            import numpy as np
            weights_array = np.array(weights)
            
            # Calculate portfolio metrics
            metrics = calculate_portfolio_metrics(weights_array, symbols)
            
            portfolio_data.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'value': portfolio.total_value(),
                'investment': portfolio.total_investment(),
                'return': portfolio.total_return(),
                'return_percentage': portfolio.return_percentage(),
                'expected_return': metrics['expected_return'],
                'volatility': metrics['volatility'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'holdings_count': len(holdings)
            })
    
    return render_template('portfolio/dashboard.html',
                          portfolios=portfolios,
                          portfolio_data=portfolio_data,
                          total_value=total_value,
                          total_investment=total_investment,
                          total_return=total_return,
                          return_percentage=return_percentage)

@portfolio_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_portfolio():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Portfolio name is required', 'danger')
            return redirect(url_for('portfolio.create_portfolio'))
        
        portfolio = Portfolio(name=name, description=description, user_id=current_user.id)
        db.session.add(portfolio)
        db.session.commit()
        
        flash('Portfolio created successfully', 'success')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio.id))
    
    return render_template('portfolio/create.html')

@portfolio_bp.route('/<int:portfolio_id>')
@login_required
def view_portfolio(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    holdings = Holding.query.filter_by(portfolio_id=portfolio.id).all()
    
    # Get historical performance data
    performance_data = {}
    symbols = [holding.symbol for holding in holdings]
    
    if symbols:
        # Get historical data for each symbol
        for symbol in symbols:
            data = get_historical_data(symbol)
            if not data.empty:
                performance_data[symbol] = data['Close'].tolist()
    
    # Get transactions for this portfolio
    transactions = Transaction.query.filter_by(portfolio_id=portfolio.id).order_by(Transaction.transaction_date.desc()).all()
    
    return render_template('portfolio/view.html',
                          portfolio=portfolio,
                          holdings=holdings,
                          transactions=transactions,
                          performance_data=json.dumps(performance_data))

@portfolio_bp.route('/<int:portfolio_id>/add_holding', methods=['GET', 'POST'])
@login_required
def add_holding(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        quantity = float(request.form.get('quantity'))
        price = float(request.form.get('price'))
        asset_type = request.form.get('asset_type', 'stock')
        
        if not symbol or quantity <= 0 or price <= 0:
            flash('Please fill all fields with valid values', 'danger')
            return redirect(url_for('portfolio.add_holding', portfolio_id=portfolio.id))
        
        # Check if holding already exists
        existing_holding = Holding.query.filter_by(portfolio_id=portfolio.id, symbol=symbol).first()
        
        if existing_holding:
            # Update existing holding
            total_investment = existing_holding.total_investment + (quantity * price)
            new_quantity = existing_holding.quantity + quantity
            existing_holding.average_price = total_investment / new_quantity
            existing_holding.quantity = new_quantity
            existing_holding.total_investment = total_investment
        else:
            # Create new holding
            holding = Holding(
                symbol=symbol,
                quantity=quantity,
                average_price=price,
                total_investment=quantity * price,
                portfolio_id=portfolio.id,
                asset_type=asset_type
            )
            db.session.add(holding)
        
        # Create transaction record
        transaction = Transaction(
            symbol=symbol,
            transaction_type='buy',
            quantity=quantity,
            price=price,
            total_amount=quantity * price,
            user_id=current_user.id,
            portfolio_id=portfolio.id,
            asset_type=asset_type
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        flash('Holding added successfully', 'success')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio.id))
    
    # Get all available stocks for the dropdown
    stocks = get_all_stocks()
    
    return render_template('portfolio/add_holding.html',
                          portfolio=portfolio,
                          stocks=stocks)

@portfolio_bp.route('/<int:portfolio_id>/sell_holding/<int:holding_id>', methods=['GET', 'POST'])
@login_required
def sell_holding(portfolio_id, holding_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    holding = Holding.query.filter_by(id=holding_id, portfolio_id=portfolio.id).first_or_404()
    
    if request.method == 'POST':
        quantity = float(request.form.get('quantity'))
        price = float(request.form.get('price'))
        
        if not quantity or quantity <= 0 or price <= 0:
            flash('Please fill all fields with valid values', 'danger')
            return redirect(url_for('portfolio.sell_holding', portfolio_id=portfolio.id, holding_id=holding.id))
        
        if quantity > holding.quantity:
            flash('Cannot sell more than you own', 'danger')
            return redirect(url_for('portfolio.sell_holding', portfolio_id=portfolio.id, holding_id=holding.id))
        
        # Update holding
        if quantity == holding.quantity:
            # Sell all shares
            db.session.delete(holding)
        else:
            # Sell partial shares
            # Calculate new average price and total investment
            remaining_quantity = holding.quantity - quantity
            remaining_investment = holding.total_investment * (remaining_quantity / holding.quantity)
            
            holding.quantity = remaining_quantity
            holding.total_investment = remaining_investment
            holding.average_price = remaining_investment / remaining_quantity
        
        # Create transaction record
        transaction = Transaction(
            symbol=holding.symbol,
            transaction_type='sell',
            quantity=quantity,
            price=price,
            total_amount=quantity * price,
            user_id=current_user.id,
            portfolio_id=portfolio.id,
            asset_type=holding.asset_type
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        flash('Holding sold successfully', 'success')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio.id))
    
    return render_template('portfolio/sell_holding.html',
                          portfolio=portfolio,
                          holding=holding)

@portfolio_bp.route('/<int:portfolio_id>/optimize')
@login_required
def optimize(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=current_user.id).first_or_404()
    holdings = Holding.query.filter_by(portfolio_id=portfolio.id).all()
    
    symbols = [holding.symbol for holding in holdings]
    
    if not symbols:
        flash('Portfolio must have holdings to optimize', 'danger')
        return redirect(url_for('portfolio.view_portfolio', portfolio_id=portfolio.id))
    
    # Get risk tolerance from query parameter (default to moderate)
    risk_tolerance = request.args.get('risk_tolerance', 'moderate')
    
    # Optimize portfolio
    optimization_result = optimize_portfolio(symbols, risk_tolerance)
    
    # Calculate minimum variance portfolio
    min_var_result = calculate_minimum_variance_portfolio(symbols)
    
    # Get covariance matrix
    cov_matrix = get_covariance_matrix(symbols)
    
    return render_template('portfolio/optimize.html',
                          portfolio=portfolio,
                          holdings=holdings,
                          symbols=symbols,
                          optimization_result=optimization_result,
                          min_var_result=min_var_result,
                          cov_matrix=cov_matrix.to_html(),
                          risk_tolerance=risk_tolerance)
