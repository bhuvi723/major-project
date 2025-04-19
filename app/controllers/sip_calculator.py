from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.utils.sip_calculator import calculate_sip, generate_sip_growth_data
import json

sip_calculator_bp = Blueprint('sip_calculator', __name__, url_prefix='/sip-calculator')

@sip_calculator_bp.route('/')
@login_required
def index():
    return render_template('sip_calculator/index.html')

@sip_calculator_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    # Get form data
    monthly_investment = float(request.form.get('monthly_investment', 0))
    expected_return_rate = float(request.form.get('expected_return_rate', 0))
    time_period_years = int(request.form.get('time_period_years', 0))
    inflation_rate = float(request.form.get('inflation_rate', 0))
    
    if monthly_investment <= 0 or expected_return_rate <= 0 or time_period_years <= 0:
        return jsonify({'error': 'Please provide valid input values'}), 400
    
    # Calculate SIP returns
    result = calculate_sip(monthly_investment, expected_return_rate, time_period_years, inflation_rate)
    
    # Generate year-by-year growth data for visualization
    growth_data = generate_sip_growth_data(monthly_investment, expected_return_rate, time_period_years, inflation_rate)
    
    return jsonify({
        'result': result,
        'growth_data': growth_data
    })
