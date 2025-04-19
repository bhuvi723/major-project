from app import db
from datetime import datetime

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    holdings = db.relationship('Holding', backref='portfolio', lazy=True, cascade='all, delete-orphan')
    portfolio_items = db.relationship('PortfolioItem', backref='portfolio', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Portfolio {self.name}>'

    def total_value(self):
        return sum(holding.current_value() for holding in self.holdings)

    def total_investment(self):
        return sum(holding.total_investment for holding in self.holdings)

    def total_return(self):
        return self.total_value() - self.total_investment()

    def return_percentage(self):
        if self.total_investment() == 0:
            return 0
        return (self.total_return() / self.total_investment()) * 100

class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    total_investment = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    asset_type = db.Column(db.String(20), default='stock')  # 'stock' or 'mutual_fund'

    def __repr__(self):
        return f'<Holding {self.symbol} - {self.quantity}>'

    def current_value(self):
        # This will be calculated using yfinance in real-time
        from app.utils.stock_data import get_current_price
        current_price = get_current_price(self.symbol)
        return current_price * self.quantity

    def profit_loss(self):
        return self.current_value() - self.total_investment

    def profit_loss_percentage(self):
        if self.total_investment == 0:
            return 0
        return (self.profit_loss() / self.total_investment) * 100

class PortfolioItem(db.Model):
    """
    A more flexible portfolio item model that can represent various types of assets
    including mutual funds, stocks, bonds, etc.
    """
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # 'mutual_fund', 'stock', 'watchlist_mf', etc.
    item_id = db.Column(db.String(50), nullable=False)  # scheme_code for mutual funds, symbol for stocks
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=0)
    purchase_price = db.Column(db.Float, default=0)
    purchase_date = db.Column(db.String(20))  # YYYY-MM-DD format
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioItem {self.name} - {self.item_type}>'

    def current_value(self):
        """
        Calculate the current value of the portfolio item
        """
        if self.item_type == 'mutual_fund':
            # Get current NAV for mutual fund
            from app.utils.mf_api import get_mutual_fund_details
            fund_data = get_mutual_fund_details(int(self.item_id))
            if fund_data and 'scheme_nav' in fund_data:
                return float(fund_data['scheme_nav']) * self.quantity
        elif self.item_type == 'stock':
            # Get current price for stock
            from app.utils.stock_data import get_current_price
            current_price = get_current_price(self.item_id)
            return current_price * self.quantity

        return 0

    def total_investment(self):
        """
        Calculate the total investment amount
        """
        return self.purchase_price * self.quantity

    def profit_loss(self):
        """
        Calculate the profit or loss
        """
        return self.current_value() - self.total_investment()

    def profit_loss_percentage(self):
        """
        Calculate the profit or loss percentage
        """
        if self.total_investment() == 0:
            return 0
        return (self.profit_loss() / self.total_investment()) * 100
