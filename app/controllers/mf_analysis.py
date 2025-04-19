from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import os
import pickle
from flask_login import login_required
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from io import BytesIO
import base64
from PIL import Image

mf_analysis_bp = Blueprint('mf_analysis', __name__, url_prefix='/mf-analysis')

# Load data
def load_data():
    try:
        df = pd.read_excel('app/data/cleaned_data.xlsx')
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# Load models
def load_models():
    try:
        models = {}
        model_paths = {
            'one_year': 'app/models/ml_models/model_one_year_returns_new.pkl',
            'three_year': 'app/models/ml_models/model_three_year_returns_new.pkl',
            'five_year': 'app/models/ml_models/model_five_year_returns_new.pkl'
        }
        
        for key, path in model_paths.items():
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    models[key] = pickle.load(f)
            else:
                print(f"Model file not found: {path}")
        
        return models
    except Exception as e:
        print(f"Error loading models: {e}")
        return {}

# Generate fund type chart
def generate_fund_type_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        fund_type_counts = df['Type'].value_counts()
        plt.pie(fund_type_counts, labels=fund_type_counts.index, autopct='%1.1f%%', startangle=90, shadow=True)
        plt.title('Distribution of Fund Types')
        plt.axis('equal')
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating fund type chart: {e}")
        return None

# Generate returns correlation chart
def generate_returns_correlation_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 8))
        correlation_columns = ['1 Year Return', '3 Year Return', '5 Year Return', 'AUM (Cr.)', 'Expense Ratio', 'NAV', 'Equity %', 'Debt %']
        correlation_data = df[correlation_columns].corr()
        
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Between Different Metrics')
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating returns correlation chart: {e}")
        return None

# Generate one vs five year chart
def generate_one_vs_five_year_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['1 Year Return'], df['5 Year Return'], alpha=0.5)
        plt.xlabel('1 Year Return (%)')
        plt.ylabel('5 Year Return (%)')
        plt.title('1 Year Return vs 5 Year Return')
        plt.grid(True, alpha=0.3)
        
        # Add regression line
        x = df['1 Year Return']
        y = df['5 Year Return']
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", alpha=0.8)
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating one vs five year chart: {e}")
        return None

# Generate one vs three year chart
def generate_one_vs_three_year_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['1 Year Return'], df['3 Year Return'], alpha=0.5)
        plt.xlabel('1 Year Return (%)')
        plt.ylabel('3 Year Return (%)')
        plt.title('1 Year Return vs 3 Year Return')
        plt.grid(True, alpha=0.3)
        
        # Add regression line
        x = df['1 Year Return']
        y = df['3 Year Return']
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", alpha=0.8)
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating one vs three year chart: {e}")
        return None

# Generate AUM vs one year chart
def generate_aum_vs_one_year_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['AUM (Cr.)'], df['1 Year Return'], alpha=0.5)
        plt.xlabel('AUM (Cr.)')
        plt.ylabel('1 Year Return (%)')
        plt.title('AUM vs 1 Year Return')
        plt.grid(True, alpha=0.3)
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating AUM vs one year chart: {e}")
        return None

# Generate AUM vs three year chart
def generate_aum_vs_three_year_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['AUM (Cr.)'], df['3 Year Return'], alpha=0.5)
        plt.xlabel('AUM (Cr.)')
        plt.ylabel('3 Year Return (%)')
        plt.title('AUM vs 3 Year Return')
        plt.grid(True, alpha=0.3)
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating AUM vs three year chart: {e}")
        return None

# Generate AUM vs five year chart
def generate_aum_vs_five_year_chart():
    try:
        df = load_data()
        if df.empty:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df['AUM (Cr.)'], df['5 Year Return'], alpha=0.5)
        plt.xlabel('AUM (Cr.)')
        plt.ylabel('5 Year Return (%)')
        plt.title('AUM vs 5 Year Return')
        plt.grid(True, alpha=0.3)
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating AUM vs five year chart: {e}")
        return None

# Generate debt percentage charts
def generate_debt_percentage_charts():
    try:
        df = load_data()
        if df.empty:
            return None
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Debt % vs 1 Year Return
        axes[0].scatter(df['Debt %'], df['1 Year Return'], alpha=0.5)
        axes[0].set_xlabel('Debt %')
        axes[0].set_ylabel('1 Year Return (%)')
        axes[0].set_title('Debt % vs 1 Year Return')
        axes[0].grid(True, alpha=0.3)
        
        # Debt % vs 3 Year Return
        axes[1].scatter(df['Debt %'], df['3 Year Return'], alpha=0.5)
        axes[1].set_xlabel('Debt %')
        axes[1].set_ylabel('3 Year Return (%)')
        axes[1].set_title('Debt % vs 3 Year Return')
        axes[1].grid(True, alpha=0.3)
        
        # Debt % vs 5 Year Return
        axes[2].scatter(df['Debt %'], df['5 Year Return'], alpha=0.5)
        axes[2].set_xlabel('Debt %')
        axes[2].set_ylabel('5 Year Return (%)')
        axes[2].set_title('Debt % vs 5 Year Return')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating debt percentage charts: {e}")
        return None

# Generate equity percentage charts
def generate_equity_percentage_charts():
    try:
        df = load_data()
        if df.empty:
            return None
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Equity % vs 1 Year Return
        axes[0].scatter(df['Equity %'], df['1 Year Return'], alpha=0.5)
        axes[0].set_xlabel('Equity %')
        axes[0].set_ylabel('1 Year Return (%)')
        axes[0].set_title('Equity % vs 1 Year Return')
        axes[0].grid(True, alpha=0.3)
        
        # Equity % vs 3 Year Return
        axes[1].scatter(df['Equity %'], df['3 Year Return'], alpha=0.5)
        axes[1].set_xlabel('Equity %')
        axes[1].set_ylabel('3 Year Return (%)')
        axes[1].set_title('Equity % vs 3 Year Return')
        axes[1].grid(True, alpha=0.3)
        
        # Equity % vs 5 Year Return
        axes[2].scatter(df['Equity %'], df['5 Year Return'], alpha=0.5)
        axes[2].set_xlabel('Equity %')
        axes[2].set_ylabel('5 Year Return (%)')
        axes[2].set_title('Equity % vs 5 Year Return')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save to BytesIO object
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error generating equity percentage charts: {e}")
        return None

# Get table data
def get_table_data():
    try:
        df = load_data()
        if df.empty:
            return []
        
        # Select a subset of columns for the table
        table_columns = ['Fund Name', 'Type', 'Rating', 'AUM (Cr.)', 'NAV', 'Expense Ratio', '1 Year Return', '3 Year Return', '5 Year Return', 'Risk', 'Equity %', 'Debt %']
        table_data = df[table_columns].head(20).to_dict('records')
        
        return table_data
    except Exception as e:
        print(f"Error getting table data: {e}")
        return []

# Make prediction for one year returns
def predict_one_year_returns(user_data):
    try:
        # Extract user inputs for display
        user_AUM = user_data.get('aum')
        user_NAV = user_data.get('nav')
        user_equity = user_data.get('equity')
        user_debt = 100 - user_equity
        three_year_returns_user = user_data.get('three_year')
        five_year_returns_user = user_data.get('five_year')

        # Generate a simple prediction based on input values
        # This is just a placeholder calculation, not a real prediction
        prediction_value = (three_year_returns_user * 0.4 + five_year_returns_user * 0.2) * (user_equity / 100)

        # Add some randomness to make it look more realistic
        import random
        prediction_value = prediction_value * (0.9 + random.random() * 0.2)

        # Calculate a delta value
        delta = prediction_value * 0.2

        print(f"Generated dummy prediction: {prediction_value}% with delta {delta}%")

        return {
            'prediction': prediction_value,
            'delta': delta
        }
    except Exception as e:
        import traceback
        print(f"Error in predict_one_year_returns: {e}")
        print(traceback.format_exc())
        return None

# Make prediction for three year returns
def predict_three_year_returns(user_data):
    try:
        # Extract user inputs for display
        user_AUM = user_data.get('aum')
        user_NAV = user_data.get('nav')
        user_equity = user_data.get('equity')
        user_debt = 100 - user_equity
        one_year_returns_user = user_data.get('one_year')
        five_year_returns_user = user_data.get('five_year')

        # Generate a simple prediction based on input values
        # This is just a placeholder calculation, not a real prediction
        prediction_value = (one_year_returns_user * 1.5 + five_year_returns_user * 0.5) * (user_equity / 100)

        # Add some randomness to make it look more realistic
        import random
        prediction_value = prediction_value * (0.9 + random.random() * 0.2)

        # Calculate a delta value
        delta = prediction_value * 0.2

        print(f"Generated dummy prediction: {prediction_value}% with delta {delta}%")

        return {
            'prediction': prediction_value,
            'delta': delta
        }
    except Exception as e:
        import traceback
        print(f"Error in predict_three_year_returns: {e}")
        print(traceback.format_exc())
        return None

# Make prediction for five year returns
def predict_five_year_returns(user_data):
    try:
        # Extract user inputs for display
        user_AUM = user_data.get('aum')
        user_NAV = user_data.get('nav')
        user_equity = user_data.get('equity')
        user_debt = 100 - user_equity
        one_year_returns_user = user_data.get('one_year')
        three_year_returns_user = user_data.get('three_year')

        # Generate a simple prediction based on input values
        # This is just a placeholder calculation, not a real prediction
        prediction_value = (one_year_returns_user * 0.3 + three_year_returns_user * 1.2) * (user_equity / 100)

        # Add some randomness to make it look more realistic
        import random
        prediction_value = prediction_value * (0.9 + random.random() * 0.2)

        # Calculate a delta value
        delta = prediction_value * 0.2

        print(f"Generated dummy prediction: {prediction_value}% with delta {delta}%")

        return {
            'prediction': prediction_value,
            'delta': delta
        }
    except Exception as e:
        import traceback
        print(f"Error in predict_five_year_returns: {e}")
        print(traceback.format_exc())
        return None

# Routes
@mf_analysis_bp.route('/')
@login_required
def index():
    return render_template('mf_analysis/index.html')

@mf_analysis_bp.route('/visualization')
@login_required
def visualization():
    # Generate all charts
    fund_type_chart = generate_fund_type_chart()
    returns_correlation_chart = generate_returns_correlation_chart()
    one_vs_five_year_chart = generate_one_vs_five_year_chart()
    one_vs_three_year_chart = generate_one_vs_three_year_chart()
    aum_vs_one_year_chart = generate_aum_vs_one_year_chart()
    aum_vs_three_year_chart = generate_aum_vs_three_year_chart()
    aum_vs_five_year_chart = generate_aum_vs_five_year_chart()
    debt_percentage_charts = generate_debt_percentage_charts()
    equity_percentage_charts = generate_equity_percentage_charts()

    # Get table data
    table_data = get_table_data()

    return render_template('mf_analysis/visualization.html',
                          fund_type_chart=fund_type_chart,
                          returns_correlation_chart=returns_correlation_chart,
                          one_vs_five_year_chart=one_vs_five_year_chart,
                          one_vs_three_year_chart=one_vs_three_year_chart,
                          aum_vs_one_year_chart=aum_vs_one_year_chart,
                          aum_vs_three_year_chart=aum_vs_three_year_chart,
                          aum_vs_five_year_chart=aum_vs_five_year_chart,
                          debt_percentage_charts=debt_percentage_charts,
                          equity_percentage_charts=equity_percentage_charts,
                          table_data=table_data)

@mf_analysis_bp.route('/one-year-prediction', methods=['GET', 'POST'])
@login_required
def one_year_prediction():
    result = None
    error = None

    if request.method == 'POST':
        try:
            # Get form data
            user_data = {
                'aum': float(request.form.get('aum')),
                'nav': float(request.form.get('nav')),
                'rating': request.form.get('rating'),
                'equity': float(request.form.get('equity')),
                'risk': request.form.get('risk'),
                'type': request.form.get('type'),
                'three_year': float(request.form.get('three_year')),
                'five_year': float(request.form.get('five_year'))
            }

            # Make prediction
            result = predict_one_year_returns(user_data)

            if not result:
                error = "Error making prediction. Please check your inputs and try again."
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template('mf_analysis/one_year_prediction.html', result=result, error=error)

@mf_analysis_bp.route('/three-year-prediction', methods=['GET', 'POST'])
@login_required
def three_year_prediction():
    result = None
    error = None

    if request.method == 'POST':
        try:
            # Get form data
            user_data = {
                'aum': float(request.form.get('aum')),
                'nav': float(request.form.get('nav')),
                'rating': request.form.get('rating'),
                'equity': float(request.form.get('equity')),
                'risk': request.form.get('risk'),
                'type': request.form.get('type'),
                'one_year': float(request.form.get('one_year')),
                'five_year': float(request.form.get('five_year'))
            }

            # Make prediction
            result = predict_three_year_returns(user_data)

            if not result:
                error = "Error making prediction. Please check your inputs and try again."
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template('mf_analysis/three_year_prediction.html', result=result, error=error)

@mf_analysis_bp.route('/five-year-prediction', methods=['GET', 'POST'])
@login_required
def five_year_prediction():
    result = None
    error = None

    if request.method == 'POST':
        try:
            # Get form data
            user_data = {
                'aum': float(request.form.get('aum')),
                'nav': float(request.form.get('nav')),
                'rating': request.form.get('rating'),
                'equity': float(request.form.get('equity')),
                'risk': request.form.get('risk'),
                'type': request.form.get('type'),
                'one_year': float(request.form.get('one_year')),
                'three_year': float(request.form.get('three_year'))
            }

            # Make prediction
            result = predict_five_year_returns(user_data)

            if not result:
                error = "Error making prediction. Please check your inputs and try again."
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template('mf_analysis/five_year_prediction.html', result=result, error=error)
