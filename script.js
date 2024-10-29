document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dividend-form');
    const resultDiv = document.getElementById('result');
    const categoryDiv = document.getElementById('category');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        calculateScore();
    });

    async function calculateScore() {
        const formData = {
            payout_ratio: document.getElementById('payout-ratio').value,
            debt_levels: document.getElementById('debt-levels').value,
            recession_perform: document.getElementById('recession-perform').value,
            dividend_longevity: document.getElementById('dividend-longevity').value,
            industry_cyclicality: document.getElementById('industry-cyclicality').value,
            free_cash_flow: document.getElementById('free-cash-flow').value,
            recent_growth: document.getElementById('recent-growth').value
        };

        try {
            const response = await fetch('http://localhost:8000/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            const weightedScore = data.score;

            // Categorize the score
            let category;
            if (weightedScore >= 78 && weightedScore <= 100) {
                category = "Extremely Safe";
            } else if (weightedScore >= 60 && weightedScore <= 77) {
                category = "Safe";
            } else if (weightedScore >= 36 && weightedScore <= 59) {
                category = "Unsafe";
            } else {
                category = "Extremely Unsafe";
            }

            // Display the result and category
            resultDiv.textContent = `Your Aggregated Weighted Score is: ${weightedScore}`;
            categoryDiv.textContent = `Category: ${category}`;
            categoryDiv.className = category.toLowerCase().replace(' ', '-');
        } catch (error) {
            console.error('Error:', error);
            resultDiv.textContent = 'An error occurred while calculating the score. Please try again.';
            categoryDiv.textContent = '';
        }
    }
});
