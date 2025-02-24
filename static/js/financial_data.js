$(document).ready(function() {
    // Check if historical_data is defined
    if (typeof historical_data !== 'undefined') {
        // Extract dates and closing prices
        var dates = historical_data['t'].map(function(timestamp) {
            return new Date(timestamp * 1000);  // Convert Unix timestamp to milliseconds
        });
        var closing_prices = historical_data['c'];

        // Plot historical chart using Plotly
        var historicalChart = {
            x: dates,
            y: closing_prices,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Closing Price'
        };

        var layout = {
            title: 'Historical Closing Prices',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Closing Price' }
        };

        Plotly.newPlot('historical-chart', [historicalChart], layout);
    }
});
