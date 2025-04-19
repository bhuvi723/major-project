# FinDash - Financial Web Application

FinDash is a comprehensive financial web application built with Flask and Plotly Dash. It provides portfolio management, stock and mutual fund tracking, portfolio optimization, SIP calculation, and an AI-powered chatbot for financial advice.

## Features

- **Portfolio Dashboard**: Track your investments, analyze performance, and visualize your portfolio allocation in real-time.
- **Stocks & Mutual Funds Dashboard**: Explore Indian stocks and mutual funds with detailed information, historical data, and performance metrics.
- **Portfolio Optimization**: Optimize your portfolio using modern portfolio theory, Sharpe ratio, and minimum variance techniques.
- **SIP Calculator**: Plan your investments with our SIP calculator that includes inflation adjustment for realistic projections.
- **AI-Powered Chatbot**: Get instant answers to your financial questions and personalized investment advice.

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/findash.git
cd findash
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/Scripts/activate  # On Windows
# OR
source venv/bin/activate  # On macOS/Linux
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URI=sqlite:///finance_app.db
```

5. Run the application:
```
python run.py
```

6. Open your browser and navigate to `http://127.0.0.1:5000/`

## Project Structure

```
findash/
├── app/
│   ├── controllers/       # Route handlers
│   ├── dashboards/        # Plotly Dash applications
│   ├── models/            # Database models
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   ├── utils/             # Utility functions
│   └── __init__.py        # Application factory
├── venv/                  # Virtual environment
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
└── run.py                 # Application entry point
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Plotly, Dash
- **Financial Data**: yfinance
- **AI Chatbot**: OpenAI API
- **Database**: SQLite

## For Students

This project is designed with students in mind, making complex financial concepts accessible and practical. It includes:

- **Portfolio Optimization**: Learn about Sharpe ratio, minimum variance, and covariance matrix.
- **SIP Calculator**: Understand the impact of inflation on long-term investments.
- **Indian Stock Market**: Access data for 60+ hand-picked Indian stocks across large, mid, and small-cap segments.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Plotly](https://plotly.com/)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [OpenAI](https://openai.com/)
- [Bootstrap](https://getbootstrap.com/)
