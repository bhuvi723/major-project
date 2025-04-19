from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
import builtins
from flask_login import login_required, current_user
from app.utils.mf_api import search_mutual_funds, get_mutual_fund_details, fetch_mutual_fund_data, get_top_gainers_and_losers, get_top_funds_by_category
from app.models.portfolio import Portfolio, PortfolioItem
from app import db
import pandas as pd
import json

mutual_funds = Blueprint('mutual_funds', __name__)

@mutual_funds.route('/mutual-funds', strict_slashes=False)
@login_required
def index():
    """
    Display the mutual funds dashboard
    """
    query = request.args.get('query', '')
    funds = search_mutual_funds(query)

    # Get top gainers and losers
    top_performers = get_top_gainers_and_losers(limit=5)

    # Get top performing funds by category
    top_large_cap = get_top_funds_by_category(category='large-cap', period='one_year_return', limit=5)
    top_mid_cap = get_top_funds_by_category(category='mid-cap', period='one_year_return', limit=5)
    top_small_cap = get_top_funds_by_category(category='small-cap', period='one_year_return', limit=5)

    return render_template('mutual_funds/index.html',
                          funds=funds,
                          query=query,
                          top_gainers=top_performers['top_gainers'],
                          top_losers=top_performers['top_losers'],
                          top_large_cap=top_large_cap,
                          top_mid_cap=top_mid_cap,
                          top_small_cap=top_small_cap)

@mutual_funds.route('/mutual-funds/<int:scheme_code>', strict_slashes=False)
@login_required
def view_details(scheme_code):
    """
    Display detailed information about a specific mutual fund
    """
    fund_data = get_mutual_fund_details(scheme_code)

    if not fund_data:
        flash('Unable to fetch mutual fund data. Please try again later.', 'danger')
        return redirect(url_for('mutual_funds.index'))

    # Prepare data for charts
    nav_history = []
    if 'nav_history' in fund_data:
        nav_history = fund_data['nav_history']

        # Format dates for chart
        for entry in nav_history:
            if isinstance(entry['date'], pd.Timestamp):
                entry['date'] = entry['date'].strftime('%Y-%m-%d')

    return render_template('mutual_funds/details.html',
                          fund=fund_data,
                          nav_history=json.dumps(nav_history),
                          min=builtins.min)

@mutual_funds.route('/api/mutual-funds/search', strict_slashes=False)
@login_required
def api_search():
    """
    API endpoint for searching mutual funds
    """
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 10))

    funds = search_mutual_funds(query, limit)
    return jsonify(funds)

@mutual_funds.route('/api/mutual-funds/<int:scheme_code>', strict_slashes=False)
@login_required
def api_get_details(scheme_code):
    """
    API endpoint for getting mutual fund details
    """
    fund_data = get_mutual_fund_details(scheme_code)

    if not fund_data:
        return jsonify({'error': 'Unable to fetch mutual fund data'}), 404

    return jsonify(fund_data)

@mutual_funds.route('/mutual-funds/buy/<int:scheme_code>', methods=['POST'], strict_slashes=False)
@login_required
def buy_mutual_fund(scheme_code):
    """
    Buy a mutual fund and add it to the portfolio
    """
    amount = float(request.form.get('amount', 0))
    units = float(request.form.get('units', 0))

    if amount <= 0 and units <= 0:
        flash('Please enter a valid amount or number of units to buy.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    # Get fund details
    fund_data = get_mutual_fund_details(scheme_code)
    if not fund_data:
        flash('Unable to fetch mutual fund data. Please try again later.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    # Calculate units if amount is provided
    if amount > 0 and units <= 0:
        nav = float(fund_data['scheme_nav'])
        units = amount / nav

    # Get or create user portfolio
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, name="My Portfolio")
        db.session.add(portfolio)

    # Check if this fund is already in the portfolio
    portfolio_item = PortfolioItem.query.filter_by(
        portfolio_id=portfolio.id,
        item_type='mutual_fund',
        item_id=str(scheme_code)
    ).first()

    if portfolio_item:
        # Update existing item
        portfolio_item.quantity += units
        portfolio_item.purchase_price = float(fund_data['scheme_nav'])  # Update to latest NAV
    else:
        # Create new portfolio item
        portfolio_item = PortfolioItem(
            portfolio_id=portfolio.id,
            item_type='mutual_fund',
            item_id=str(scheme_code),
            name=fund_data['scheme_name'],
            quantity=units,
            purchase_price=float(fund_data['scheme_nav']),
            purchase_date=pd.Timestamp.now().strftime('%Y-%m-%d')
        )
        db.session.add(portfolio_item)

    try:
        db.session.commit()
        flash(f'Successfully purchased {units:.2f} units of {fund_data["scheme_name"]}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error purchasing mutual fund: {str(e)}', 'danger')

    return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

@mutual_funds.route('/mutual-funds/sell/<int:scheme_code>', methods=['POST'], strict_slashes=False)
@login_required
def sell_mutual_fund(scheme_code):
    """
    Sell units of a mutual fund from the portfolio
    """
    units = float(request.form.get('units', 0))

    if units <= 0:
        flash('Please enter a valid number of units to sell.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    # Get portfolio item
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        flash('You do not have a portfolio.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    portfolio_item = PortfolioItem.query.filter_by(
        portfolio_id=portfolio.id,
        item_type='mutual_fund',
        item_id=str(scheme_code)
    ).first()

    if not portfolio_item:
        flash('This mutual fund is not in your portfolio.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    if portfolio_item.quantity < units:
        flash(f'You only have {portfolio_item.quantity:.2f} units to sell.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    # Update portfolio item
    portfolio_item.quantity -= units

    # If quantity is zero, remove the item
    if portfolio_item.quantity <= 0:
        db.session.delete(portfolio_item)

    try:
        db.session.commit()
        flash(f'Successfully sold {units:.2f} units.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error selling mutual fund: {str(e)}', 'danger')

    return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

@mutual_funds.route('/mutual-funds/add-to-watchlist/<int:scheme_code>', methods=['POST'], strict_slashes=False)
@login_required
def add_to_watchlist(scheme_code):
    """
    Add a mutual fund to the watchlist
    """
    # Get fund details
    fund_data = get_mutual_fund_details(scheme_code)
    if not fund_data:
        flash('Unable to fetch mutual fund data. Please try again later.', 'danger')
        return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))

    # Get or create user portfolio
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id, name="My Portfolio")
        db.session.add(portfolio)

    # Check if this fund is already in the watchlist
    portfolio_item = PortfolioItem.query.filter_by(
        portfolio_id=portfolio.id,
        item_type='watchlist_mf',
        item_id=str(scheme_code)
    ).first()

    if portfolio_item:
        flash('This mutual fund is already in your watchlist.', 'info')
    else:
        # Create new watchlist item
        portfolio_item = PortfolioItem(
            portfolio_id=portfolio.id,
            item_type='watchlist_mf',
            item_id=str(scheme_code),
            name=fund_data['scheme_name'],
            quantity=0,  # Watchlist items have zero quantity
            purchase_price=float(fund_data['scheme_nav']),
            purchase_date=pd.Timestamp.now().strftime('%Y-%m-%d')
        )
        db.session.add(portfolio_item)

        try:
            db.session.commit()
            flash(f'Added {fund_data["scheme_name"]} to your watchlist.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding to watchlist: {str(e)}', 'danger')

    return redirect(url_for('mutual_funds.view_details', scheme_code=scheme_code))
