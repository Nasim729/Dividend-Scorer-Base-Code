import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

def calculate_score(payout_ratio, debt_levels, recession_perform, dividend_longevity, industry_cyclicality, free_cash_flow, recent_sales_and_earnings_growth):
    # Payout Ratio Score
    payout_score = payout_ratio / 100
    if payout_score < 0:
        payout_score = 0
    elif payout_score >= 1:
        payout_score = (-0.1 * payout_score) + 20
    else:
        payout_score = (-38 * payout_score) + 100

    # Debt Levels Score
    debt_score = (debt_levels * -26) + 100
    if debt_score < 0:
        debt_score = 0
    elif debt_score > 100:
        debt_score = 100

    # Recession Performance Score
    if recession_perform == "Good":
        recession_perform_score = 85
    elif recession_perform == "Bad":
        recession_perform_score = 25
    else:
        recession_perform_score = 50

    # Dividend Longevity Score
    dividend_longevity_score = dividend_longevity * 4.99

    # Industry Cyclicality Score
    if industry_cyclicality == "Not Cyclical":
        industry_cyclicality_score = 85
    elif industry_cyclicality == "Cyclical":
        industry_cyclicality_score = 50
    else:
        industry_cyclicality_score = 30

    # Free Cashflow Score
    free_cashflow_score = -50 * free_cash_flow + 100
    if free_cashflow_score < 0:
        free_cashflow_score = 0

    # Recent Sales and Earnings Growth Score
    recent_sales_and_earnings = recent_sales_and_earnings_growth / 100
    if recent_sales_and_earnings > 100:
        recent_sales_and_earnings = 100
    elif recent_sales_and_earnings < 0:
        recent_sales_and_earnings = 0
    else:
        recent_sales_and_earnings = (320 * recent_sales_and_earnings) + 5

    # Weighted Score Calculation
    weighted_score = (payout_score * 0.28) + (debt_score * 0.15) + (recession_perform_score * 0.01) + \
                     (dividend_longevity_score * 0.02) + (industry_cyclicality_score * 0.03) + \
                     (free_cashflow_score * 0.40) + (recent_sales_and_earnings * 0.16)

    return weighted_score

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    try:
        score = calculate_score(
            float(data['payout_ratio']),
            float(data['debt_levels']),
            data['recession_perform'],
            float(data['dividend_longevity']),
            data['industry_cyclicality'],
            float(data['free_cash_flow']),
            float(data['recent_growth'])
        )
        return jsonify({'score': round(score, 2)})
    except ValueError as e:
        return jsonify({'error': f'Invalid input. Please check your values. Error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/')
def index():
    return render_template('index.html') # Render index.html

@app.route('/get_stock_data', methods=['GET', 'POST']) 
def get_stock_data():
    ticker = request.form.get('ticker')
    api_key = 'VM9B620L0YMUD2RL'  # Replace with your actual Alpha Vantage API key
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    # Return only the necessary field
    return jsonify({
        'DividendYield': data.get('DividendYield', 'N/A')
    })

@app.route('/get_dividend_score', methods=['GET', 'POST'])
def get_dividend_score():
    ticker = request.form.get('ticker')
    api_key = 'VM9B620L0YMUD2RL'  # Replace with your actual Alpha Vantage API key
    url_cf = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={api_key}'
    url_bs = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={api_key}'
    response_cf = requests.get(url_cf)
    response_bs = requests.get(url_bs)
    data_cf = response_cf.json()
    data_bs = response_bs.json()

    try:
        # Extract latest annual dividend payout and net income
        latest_cashflow = data_cf['annualReports'][0]
        dividend_payout = float(latest_cashflow['dividendPayout'])
        net_income = float(latest_cashflow['netIncome'])

        # Calculate payout ratio
        payout_ratio = dividend_payout / net_income

        # Calculate payout ratio score
        payout_score = payout_ratio / 100
        if payout_score < 0:
            payout_score = 0
        elif payout_score >= 1:
            payout_score = (-0.1 * payout_score) + 20
        else:
            payout_score = (-38 * payout_score) + 100

        # Extract latest annual long-term debt and total shareholder equity
        latest_balancesheet = data_bs['annualReports'][0]
        long_term_debt = float(latest_balancesheet['longTermDebt'])
        total_shareholder_equity = float(latest_balancesheet['totalShareholderEquity'])

        # Calculate debt ratio
        debt_ratio = long_term_debt / total_shareholder_equity

        # Calculate debt score
        debt_score = (debt_ratio * -26) + 100
        if debt_score < 0:
            debt_score = 0
        elif debt_score > 100:
            debt_score = 100

        # Fetch data for LFCF calculation
        operating_cashflow = float(latest_cashflow.get('operatingCashflow', 0))
        capital_expenditures = float(latest_cashflow.get('capitalExpenditures', 0))
        short_term_debt_repayments = float(latest_cashflow.get('proceedsFromRepaymentsOfShortTermDebt', 0) or 0)
        long_term_debt_issuance = float(latest_cashflow.get('proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet', 0))

        # Calculate Net Debt Repayments
        net_debt_repayments = float(short_term_debt_repayments or 0) + float(long_term_debt_issuance)

        # Calculate LFCF
        lfcf = operating_cashflow - capital_expenditures - net_debt_repayments

        # Calculate LFCF Ratio
        lfcf_ratio = dividend_payout / lfcf if lfcf != 0 else 0 # Set to 0 if lfcf is 0

        # Calculate Free Cash Flow Score
        free_cashflow_score = -50 * lfcf_ratio + 100
        if free_cashflow_score < 0:
            free_cashflow_score = 0

        # Calculate weighted dividend score (1/3 weight for each metric)
        weighted_dividend_score = (payout_score / 3) + (debt_score / 3) + (free_cashflow_score / 3)

        return jsonify({'dividend_score': weighted_dividend_score, 
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
        return jsonify({'error': f'Error calculating dividend score: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
