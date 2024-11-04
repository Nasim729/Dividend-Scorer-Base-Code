from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True)
