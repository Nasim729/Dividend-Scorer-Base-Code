import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route('/calculate', methods=['POST'])
def calculate():
    # Receive JSON data from the client
    data = request.json
    try:
        # Calculate the dividend score using various financial metrics
        score = calculate_score(
            float(data['payout_ratio']),
            float(data['debt_levels']),
            data['recession_perform'],
            float(data['dividend_longevity']),
            data['industry_cyclicality'],
            float(data['free_cash_flow']),
            float(data['recent_growth'])
        )
        # Return the score in JSON format, rounded to two decimal places
        return jsonify({'score': round(score, 2)})
    except ValueError as e:
        # Handle invalid input values and return a 400 error with a message
        return jsonify({'error': f'Invalid input. Please check your values. Error: {str(e)}'}), 400
    except Exception as e:
        # Handle unexpected errors and return a 500 error with a message
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/')
def index():
    # Render the main page (index.html) for the application
    return render_template('index.html')

@app.route('/get_stock_data', methods=['GET', 'POST']) 
def get_stock_data():
    # Retrieve the stock ticker from the form data
    ticker = request.form.get('ticker')
    api_key = os.getenv ('API_KEY') # Load the API key securely from the environment
    if not api_key:
        return jsonify({'error':'API key is missing'}), 500
    # Create API URL to get stock data
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    print(f"Raw API Response: {data}")

    # Handle cases where the API returns an error
    if 'Error Message' in data:
        return jsonify({'error': data['Error Message']}), 500

    # Return relevant stock data (Dividend Yield and Market Capitalization)
    return jsonify({
        'DividendYield': data.get('DividendYield', 'N/A'),
        'MarketCapitalization': data.get('MarketCapitalization', 'N/A'),
        'Name': data.get('Name', 'N/A'), # Include stock name in response
        'EPS': data.get('EPS', 'N/A') # Include EPS in response
    })

@app.route('/get_dividend_score', methods=['GET', 'POST'])
def get_dividend_score():
    # Retrieve the stock ticker from the form data
    ticker = request.form.get('ticker')
    api_key = os.getenv ('API_KEY') 
    if not api_key:
        return jsonify({'error': 'API key is missing'}), 500 # Load the API key securely from the environment
    # URLs to get cash flow and balance sheet data
    url_cf = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={api_key}'
    url_bs = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={api_key}'
    response_cf = requests.get(url_cf)
    response_bs = requests.get(url_bs)
    data_cf = response_cf.json()
    data_bs = response_bs.json()

    try:
        # Check if cash flow data is available and 'annualReports' is not empty
        if 'annualReports' not in data_cf or not data_cf['annualReports']:
            return jsonify({'error': 'No cash flow data available for this ticker'}), 500

        # Extract latest annual dividend payout and net income from cash flow data
        latest_cashflow = data_cf['annualReports'][0]
        dividend_payout = float(latest_cashflow['dividendPayout'])
        net_income = float(latest_cashflow['netIncome'])

        # Calculate payout ratio and its corresponding score
        payout_ratio = dividend_payout / net_income

        # Calculate payout ratio score
        payout_score = payout_ratio / 100
        if payout_score < 0:
            payout_score = 0
        elif payout_score >= 1:
            payout_score = (-0.1 * payout_score) + 20
        else:
            payout_score = (-38 * payout_score) + 100

        # Extract latest annual long-term debt and total shareholder equity from balance sheet data
        latest_balancesheet = data_bs['annualReports'][0]
        long_term_debt = float(latest_balancesheet['longTermDebt'])
        total_shareholder_equity = float(latest_balancesheet['totalShareholderEquity'])

        # Calculate debt ratio and its corresponding score
        debt_ratio = long_term_debt / total_shareholder_equity

        # Calculate debt score
        debt_score = (debt_ratio * -26) + 100
        if debt_score < 0:
            debt_score = 0
        elif debt_score > 100:
            debt_score = 100

        # Calculate weighted dividend score
        weighted_dividend_score = (payout_score * 0.5) + (debt_score * 0.5)

        # Fetch data for LFCF calculation
        operating_cashflow = float(latest_cashflow.get('operatingCashflow', 0))
        capital_expenditures = float(latest_cashflow.get('capitalExpenditures', 0))
        short_term_debt_repayments = float(latest_cashflow.get('proceedsFromRepaymentsOfShortTermDebt', 0) or 0)
        long_term_debt_issuance = float(latest_cashflow.get('proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet', 0))

        # Calculate Net Debt Repayments
        net_debt_repayments = float(short_term_debt_repayments or 0) + float(long_term_debt_issuance)

        # Calculate LFCF (Levered Free Cash Flow)
        lfcf = operating_cashflow - capital_expenditures - net_debt_repayments

        # Calculate LFCF Ratio and Free Cash Flow Score
        lfcf_ratio = dividend_payout / lfcf if lfcf != 0 else 'N/A'
        free_cashflow_score = -50 * lfcf_ratio + 100
        if free_cashflow_score < 0:
            free_cashflow_score = 0

        # Calculate the weighted dividend score (1/3 weight for each metric)
        weighted_dividend_score = (payout_score / 3) + (debt_score / 3) + (free_cashflow_score / 3)

        # Return all calculated data as JSON response
        return jsonify({
            'dividend_score': weighted_dividend_score, 
            'payout_ratio': payout_ratio, 
            'debt_ratio': debt_ratio, 
            'operatingCashflow': operating_cashflow,
            'capitalExpenditures': capital_expenditures,
            'shortTermDebtRepayments': short_term_debt_repayments,
            'longTermDebtIssuance': long_term_debt_issuance,
            'netDebtRepayments': net_debt_repayments,
            'lfcf': lfcf,
            'lfcf_ratio': lfcf_ratio
        })

    except (KeyError, ValueError, ZeroDivisionError) as e:
        # Handle errors in calculation or missing data
        return jsonify({'error': f'Error calculating dividend score: {str(e)}'}), 500

@app.route('/api/cashflow/<symbol>')
def get_cashflow_data(symbol):
    api_key = os.getenv('API_KEY')
    if not api_key:
        return jsonify({'error': 'API key is missing'}), 500
    url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'annualReports' not in data:
        return jsonify({'error': 'No data available'})

    annual_reports = data['annualReports']

    # Extract relevant data
    cashflow_data = {
        'labels': [],
        'operatingCashflow': [],
        'capitalExpenditures': [],
        'freeCashflow': []
    }

    for report in annual_reports:
        cashflow_data['labels'].append(report['fiscalDateEnding'])
        cashflow_data['operatingCashflow'].append(float(report['operatingCashflow']) / 1e9)  # Convert to billions
        cashflow_data['capitalExpenditures'].append(float(report['capitalExpenditures']) / 1e9)  # Convert to billions
        cashflow_data['freeCashflow'].append(
            float(report['operatingCashflow']) / 1e9 + float(report['capitalExpenditures']) / 1e9
        )

    # Reverse the data to show chronological order
    for key in cashflow_data:
        cashflow_data[key].reverse()

    return jsonify(cashflow_data)

def calculate_score(payout_ratio, debt_levels, recession_perform, dividend_longevity, industry_cyclicality, free_cash_flow, recent_growth):
    # Placeholder for the actual dividend score calculation logic
    # Replace this with your actual calculation
    return (payout_ratio + debt_levels + dividend_longevity + free_cash_flow + recent_growth) / 5


if __name__ == '__main__':
    app.run(debug=True)  # Run the application in debug mode
