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

// Stock data
const stocks = [
    {name: "Apple", price: 310.40, shares: 100, return: -1.10},
    {name: "Meta", price: 140.45, shares: 50, return: -0.10},
    {name: "Microsoft", price: 240.98, shares: 75, return: 0.85},
    {name: "Google", price: 99.12, shares: 30, return: -0.04}
];

// Render stock cards
const stockCardsContainer = document.getElementById('stockCards');
stocks.forEach(stock => {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.innerHTML = `
        <h3>${stock.name}</h3>
        <p>Total Shares</p>
        <h2>$${stock.price.toFixed(2)}</h2>
        <p style="color: ${stock.return > 0 ? 'green' : 'red'};">${stock.return.toFixed(2)}%</p>
    `;
    stockCardsContainer.appendChild(card);
});

// Portfolio chart
const portfolioCtx = document.getElementById('portfolioChart').getContext('2d');
const portfolioChart = new Chart(portfolioCtx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Portfolio Value',
            data: [12000, 19000, 15000, 17000, 16000, 23000],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Volume chart
const volumeCtx = document.getElementById('volumeChart').getContext('2d');
const volumeChart = new Chart(volumeCtx, {
    type: 'bar',
    data: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [{
            label: 'Trading Volume',
            data: [1000, 1200, 1500, 1300, 1100, 1400, 1600, 1800, 2000, 2200, 2400, 2600],
            backgroundColor: 'rgba(75, 192, 192, 0.6)'
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Watchlist
const watchlist = [
    {name: "Amazon.com, Inc.", symbol: "AMZN", price: 102.24, change: 3.02},
    {name: "Coca-Cola Co", symbol: "KO", price: 60.49, change: -0.32},
    {name: "Bayerische Motoren Werke AG", symbol: "BMW", price: 92.94, change: 0.59},
    {name: "Microsoft Corp", symbol: "MSFT", price: 248.16, change: 0.16},
    {name: "United Parcel Service, Inc.", symbol: "UPS", price: 182.09, change: 2.39},
];

const watchlistContainer = document.getElementById('watchlistItems');
watchlist.forEach(stock => {
    const item = document.createElement('div');
    item.className = 'watchlist-item';
    item.innerHTML = `
        <div>
            <strong>${stock.name}</strong> (${stock.symbol})
        </div>
        <div>
            <div>$${stock.price.toFixed(2)}</div>
            <div style="color: ${stock.change > 0 ? 'green' : 'red'};">${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}</div>
        </div>
    `;
    watchlistContainer.appendChild(item);
});

// Time range selector
document.getElementById('timeRange').addEventListener('change', function(e) {
    // In a real application, this would fetch new data and update the chart
    console.log('Selected time range:', e.target.value);
});
