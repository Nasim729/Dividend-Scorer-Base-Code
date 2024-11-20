document.addEventListener('DOMContentLoaded', function() {
    const stockTickerInput = document.getElementById('stock-ticker-input');
    const payoutRatioValue = document.getElementById('payout-ratio-value');
    const dividendYieldValue = document.getElementById('dividend-yield-value');
    const dividendScoreValue = document.getElementById('dividend-score-value');
    const debtRatioValue = document.getElementById('free-cashflow-generation-score-value'); 
    const lfcfRatioValue = document.getElementById('total-investment-value'); 
    const marketCapValue = document.getElementById('market-cap-value');

    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }

    stockTickerInput.addEventListener('input', debounce(function(e) {
        const ticker = e.target.value;
        if (ticker.length > 0) {
            fetchStockData(ticker);
            fetchDividendScore(ticker); 
        } else {
            payoutRatioValue.textContent = 'N/A';
            dividendYieldValue.textContent = 'N/A';
            dividendScoreValue.textContent = 'N/A';
            debtRatioValue.textContent = 'N/A'; 
            lfcfRatioValue.textContent = 'N/A'; 
            marketCapValue.textContent = 'N/A';
        }
    }, 300)); // Delay API calls by 300ms after typing stops

    async function fetchStockData(ticker) {
        try {
            const response = await fetch('/get_stock_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `ticker=${ticker}`
            });

            console.log("Response:", response);

            if (!response.ok) {
                const message = `HTTP error! status: ${response.status}`;
                throw new Error(message);
            }

            const data = await response.json();

            console.log("Data:", data);

            if (!data || !data['DividendYield']) {
                throw new Error('Invalid or missing data from API. Check your API key and ticker symbol.');
            }

            dividendYieldValue.textContent = `${(parseFloat(data['DividendYield']) * 100).toFixed(2)}%`; 
            marketCapValue.textContent = formatMarketCap(data['MarketCapitalization']); // Format market cap

        } catch (error) {
            console.error('Error:', error);
            dividendYieldValue.textContent = 'Error fetching data';
            marketCapValue.textContent = 'Error fetching data';
        }
    }

    async function fetchDividendScore(ticker) {
        try {
            const response = await fetch('/get_dividend_score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `ticker=${ticker}`
            });

            if (!response.ok) {
                const message = `HTTP error! status: ${response.status}`;
                throw new Error(message);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Round dividend score to a whole number
            dividendScoreValue.textContent = Math.round(data['dividend_score']); 
            payoutRatioValue.textContent = `${(data['payout_ratio'] * 100).toFixed(1)}%`; // Format payout ratio as percentage
            debtRatioValue.textContent = data['debt_ratio']; 
            lfcfRatioValue.textContent = data['lfcf_ratio']; 

        } catch (error) {
            console.error('Error:', error);
            dividendScoreValue.textContent = 'Error fetching data';
            payoutRatioValue.textContent = 'Error fetching data'; 
            debtRatioValue.textContent = 'Error fetching data'; 
            lfcfRatioValue.textContent = 'Error fetching data'; 
        }
    }

    // Function to format market cap
    function formatMarketCap(marketCap) {
        let value = parseFloat(marketCap);
        let suffix = '';

        if (value >= 1000000000000) {
            value /= 1000000000000;
            suffix = 'T';
        } else if (value >= 1000000000) {
            value /= 1000000000;
            suffix = 'B';
        } else if (value >= 1000000) {
            value /= 1000000;
            suffix = 'M';
        }

        return `$${value.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 2})}${suffix}`;
    }
});
