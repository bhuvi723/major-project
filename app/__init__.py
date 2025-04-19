from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///finance_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.main import main_bp
    from app.controllers.portfolio import portfolio_bp
    from app.controllers.stocks import stocks_bp
    from app.controllers.chatbot import chatbot_bp
    from app.controllers.sip_calculator import sip_calculator_bp
    from app.controllers.mutual_funds import mutual_funds
    from app.controllers.mf_analysis import mf_analysis_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(sip_calculator_bp)
    app.register_blueprint(mutual_funds)
    app.register_blueprint(mf_analysis_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
