from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.utils.stock_data import get_all_stocks, get_all_mutual_funds

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('portfolio.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get some market data for the dashboard
    stocks = get_all_stocks()
    mutual_funds = get_all_mutual_funds()
    
    return render_template('dashboard.html', 
                          stocks=stocks[:10],  # Show only top 10 stocks
                          mutual_funds=mutual_funds)
