import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
import numpy as np
from .models import StockData


# Create your views here.

def Home(request):
    return render(request, 'index.html')


def Search(request):
    Ssymbol = request.POST.get('search', request.GET.get('search_query'))

    api_key = 'pk_ebcccfabab864fbd8ad043fe33c2ea48'

    # Define the stock symbol
    symbol = Ssymbol

    api_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/chart/1y?token={api_key}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # Delete existing data in the database
        StockData.objects.all().delete()

        for candle in data:
            timestamp = candle['date']
            date = datetime.strptime(timestamp, '%Y-%m-%d').date()
            close_price = candle['close']

            # Create or update the database entry
            StockData.objects.update_or_create(
                date=date,
                defaults={'close_price': close_price}
            )
    else:
        print("Error fetching data from the Finnhub API")

    # Make a request to get quote data
    quote_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={api_key}'
    quote_response = requests.get(quote_url).json()

    """# Make a request to get company profile data
    profile_url = f'https://api.polygon.io/v1/meta/symbols/{symbol}/company?apiKey={api_key}'
    profile_response = requests.get(profile_url).json()

    # Make a request to get aggregate indicator data
    aggregate_url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?apiKey={api_key}'
    aggregate_response = requests.get(aggregate_url).json()"""

    # Extract and print the relevant data
    company_name = quote_response['companyName']
    current_price = quote_response['latestPrice']
    prev_close = quote_response['previousClose']
    close_price = quote_response['close']
    open_price = quote_response['iexOpen']
    day_high = quote_response['week52High']
    day_low = quote_response['week52Low']
    avgtotalvolume = "{:,}".format(quote_response['avgTotalVolume'])

    # Function to format the price change
    def format_price_change(change):
        if change > 0:
            return f'<span style="color: green;">▲ up {change:.2f} ({(change / prev_close) * 100:.2f}%)</span>'
        elif change < 0:
            return f'<span style="color: red;">▼ down {change:.2f} ({(change / prev_close) * 100:.2f}%)</span>'
        else:
            return f'{change:.2f} (0.00%)'

    # Define the time period you want to retrieve historical data for (e.g., one year)
    start_date = '2022-01-01'
    end_date = '2023-01-01'

    # Convert start and end dates to Unix timestamps
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

    # Define the batch size (e.g., one month)
    batch_size = 30 * 24 * 60 * 60  # 30 days

    # Initialize lists to store dates and closing prices
    all_dates = []
    all_closing_prices = []

    # Iterate through batches
    for batch_start in np.arange(start_timestamp, end_timestamp, batch_size):
        batch_end = min(batch_start + batch_size, end_timestamp)

        """# Make the API request to get historical stock price data
        historical_endpoint = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{batch_start}/{batch_end}?apiKey={api_key}'
        historical_response = requests.get(historical_endpoint)"""

        if response.status_code == 200:
            historical_data = response.json()

            for candle in historical_data:
                timestamp = candle.get('date')
                date = datetime.strptime(timestamp, '%Y-%m-%d').date()
                close_price = candle.get('close')

                # Append to the overall lists
                all_dates.append(date)
                all_closing_prices.append(close_price)
        else:
            print(f"Failed to retrieve historical data. Status code: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')}")

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Create an attractive and professional line chart
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=all_dates, y=all_closing_prices, label=f'{symbol} Closing Price', linewidth=2, markers=True)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Closing Price', fontsize=12)
    plt.title(f'{symbol} Historical Closing Prices', fontsize=16)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(fontsize=12)
    plt.tight_layout()

    plt.savefig('static/images/historical_chart.png')

    format_price_formatted = format_price_change(current_price - prev_close)

    # Moving Average
    currentprices = []
    pricesum = 0
    stocksdataobjects = StockData.objects.order_by('-date')[:10]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)
        pricesum += currentprice
        avg10 = pricesum / len(currentprices)

    currentprices = []
    pricesum = 0
    stocksdataobjects = StockData.objects.order_by('-date')[:20]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)
        pricesum += currentprice
        avg20 = pricesum / len(currentprices)

    currentprices = []
    pricesum = 0
    stocksdataobjects = StockData.objects.order_by('-date')[:50]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)
        pricesum += currentprice
        avg50 = pricesum / len(currentprices)

    currentprices = []
    pricesum = 0
    stocksdataobjects = StockData.objects.order_by('-date')[:100]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)
        pricesum += currentprice
        avg100 = pricesum / len(currentprices)

    # returns
    currentprices = []
    stocksdataobjects = StockData.objects.order_by('-date')[:7]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)

    week1 = ((currentprices[0] - currentprices[-1]) / currentprices[-1]) * 100
    week1color = 'green' if week1 >= 0 else 'red'

    currentprices = []
    stocksdataobjects = StockData.objects.order_by('-date')[:30]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)

    month1 = ((currentprices[0] - currentprices[-1]) / currentprices[-1]) * 100
    month1color = 'green' if month1 >= 0 else 'red'

    currentprices = []
    stocksdataobjects = StockData.objects.order_by('-date')[:90]
    for data_point in stocksdataobjects:
        currentprice = data_point.close_price
        currentprices.append(currentprice)

    month3 = ((currentprices[0] - currentprices[-1]) / currentprices[-1]) * 100
    month3color = 'green' if month3 >= 0 else 'red'

    avg10 = "{:.2f}".format(avg10)
    avg20 = "{:.2f}".format(avg20)
    avg50 = "{:.2f}".format(avg50)
    avg100 = "{:.2f}".format(avg100)

    week1 = "{:.2f}".format(week1)
    month1 = "{:.2f}".format(month1)
    month3 = "{:.2f}".format(month3)

    context = {
        'search_query': Ssymbol,
        'company_name': company_name,
        'current_price': current_price,
        'format_price_formatted': format_price_formatted,
        'open_price': open_price,
        'day_high': day_high,
        'day_low': day_low,
        'prev_close': prev_close,
        'avg_10': avg10,
        'avg_20': avg20,
        'avg_50': avg50,
        'avg_100': avg100,
        '1_week': week1,
        '1_week_color': week1color,
        '1_month': month1,
        '1_month_color': month1color,
        '3_month': month3,
        '3_month_color': month3color,
        'avgtotalvolume': avgtotalvolume,

    }

    query_params = '&'.join([f'{key}={value}' for key, value in context.items()])
    return HttpResponseRedirect(f'/search_results/?{query_params}')


def search_results(request):
    search_query = request.GET.get('search_query')
    company_name = request.GET.get('company_name')
    current_price = request.GET.get('current_price')
    format_price_formatted = request.GET.get('format_price_formatted')
    open_price = request.GET.get('open_price')
    day_high = request.GET.get('day_high')
    day_low = request.GET.get('day_low')
    prev_close = request.GET.get('prev_close')
    avg_10 = request.GET.get('avg_10')
    avg_20 = request.GET.get('avg_20')
    avg_50 = request.GET.get('avg_50')
    avg_100 = request.GET.get('avg_100')
    week1 = request.GET.get('1_week')
    week1color = request.GET.get('1_week_color')
    month1 = request.GET.get('1_month')
    month1color = request.GET.get('1_month_color')
    month3 = request.GET.get('3_month')
    month3color = request.GET.get('3_month_color')
    avgtotalvolume = request.GET.get('avgtotalvolume')

    context = {
        'search_query': search_query,
        'company_name': company_name,
        'current_price': current_price,
        'format_price_formatted': format_price_formatted,
        'open_price': open_price,
        'day_high': day_high,
        'day_low': day_low,
        'prev_close': prev_close,
        'avg_10': avg_10,
        'avg_20': avg_20,
        'avg_50': avg_50,
        'avg_100': avg_100,
        '1_week': week1,
        '1_week_color': week1color,
        '1_month': month1,
        '1_month_color': month1color,
        '3_month': month3,
        '3_month_color': month3color,
        'avgtotalvolume': avgtotalvolume,
    }
    return render(request, 'search_results.html', context)

