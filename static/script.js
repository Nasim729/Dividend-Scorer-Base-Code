document.addEventListener('DOMContentLoaded', function() {
    const stockTickerInput = document.getElementById('stock-ticker-input');
    const payoutRatioValue = document.getElementById('payout-ratio-value');
    const dividendYieldValue = document.getElementById('dividend-yield-value'); 

    stockTickerInput.addEventListener('input', function(e) {
        const ticker = e.target.value;
        if (ticker.length > 0) {
            fetchStockData(ticker);
        } else {
            payoutRatioValue.textContent = 'N/A';
            dividendYieldValue.textContent = 'N/A'; 
        }
    });

    async function fetchStockData(ticker) {
        try {
            const response = await fetch('/get_stock_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `ticker=${ticker}`
            });

            console.log("Response:", response); // Log the response object

            if (!response.ok) {
                const message = `HTTP error! status: ${response.status}`;
                throw new Error(message);
            }

            const data = await response.json();

            console.log("Data:", data); // Log the parsed JSON data

            // Access the correct fields from the JSON response
            if (!data || !data['PayoutRatio'] || !data['DividendYield']) {
                throw new Error('Invalid or missing data from API. Check your API key and ticker symbol.');
            }

            payoutRatioValue.textContent = data['PayoutRatio'];
            dividendYieldValue.textContent = data['DividendYield']; 

        } catch (error) {
            console.error('Error:', error);
            payoutRatioValue.textContent = 'Error fetching data';
            dividendYieldValue.textContent = 'Error fetching data'; 
        }
    }
});
