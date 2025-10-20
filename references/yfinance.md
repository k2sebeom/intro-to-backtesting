# yfinance Documentation

## Overview

yfinance is a Python library that provides easy access to Yahoo! Finance's API for retrieving financial market data. It offers a Pythonic way to fetch historical market data, company information, financial statements, and more.

**Important Legal Disclaimer**: yfinance is not affiliated with Yahoo, Inc. It's an open-source tool for research and educational purposes only. Refer to Yahoo!'s terms of use for data usage rights.

## Installation

```bash
pip install yfinance
```

## Main Components

- **Ticker**: Single ticker data access
- **Tickers**: Multiple tickers data access  
- **download**: Download market data for multiple tickers
- **Market**: Market summary information
- **WebSocket/AsyncWebSocket**: Live streaming data
- **Search**: Search functionality
- **Sector/Industry**: Sector and industry information
- **EquityQuery/Screener**: Market screening tools

## Basic Usage

### Single Ticker

```python
import yfinance as yf

# Create ticker object
ticker = yf.Ticker("AAPL")

# Get company info
info = ticker.info
print(f"Company: {info['longName']}")
print(f"Sector: {info['sector']}")
print(f"Market Cap: {info['marketCap']}")
```

### Historical Data

```python
# Get historical data
hist = ticker.history(period="1mo")
print(hist.head())

# Available periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
# Available intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
```

## Data Structures

### Historical Price Data (DataFrame)

**Shape**: (n_days, 7)  
**Index**: DatetimeIndex with timezone-aware timestamps  
**Columns**:
- `Open`: Opening price
- `High`: Highest price  
- `Low`: Lowest price
- `Close`: Closing price
- `Volume`: Trading volume
- `Dividends`: Dividend payments (0.0 if none)
- `Stock Splits`: Stock split ratios (0.0 if none)

```python
# Example output
#                                 Open        High         Low       Close    Volume  Dividends  Stock Splits
# Date                                                                                                        
# 2025-10-13 00:00:00-04:00  249.380005  249.690002  246.050003  247.670006  45280900        0.0           0.0
# 2025-10-14 00:00:00-04:00  246.600006  248.850006  245.100006  248.850006  38845600        0.0           0.0
```

### Company Information (Dict)

Key fields in `ticker.info`:
- `longName`: Company full name
- `sector`: Business sector
- `industry`: Specific industry
- `marketCap`: Market capitalization
- `enterpriseValue`: Enterprise value
- `trailingPE`: Trailing P/E ratio
- `forwardPE`: Forward P/E ratio
- `dividendYield`: Dividend yield
- `beta`: Stock beta
- `52WeekHigh`: 52-week high price
- `52WeekLow`: 52-week low price
- `averageVolume`: Average trading volume
- `currency`: Trading currency
- `exchange`: Stock exchange

### Financial Statements (DataFrame)

**Income Statement**: `ticker.income_stmt`
**Balance Sheet**: `ticker.balance_sheet`  
**Cash Flow**: `ticker.cash_flow`

**Shape**: (n_line_items, n_years)  
**Index**: Financial line items  
**Columns**: Timestamp objects for fiscal year ends

```python
# Get quarterly data
quarterly_income = ticker.quarterly_income_stmt
quarterly_balance = ticker.quarterly_balance_sheet
quarterly_cashflow = ticker.quarterly_cash_flow
```

### Dividends (Series)

**Index**: DatetimeIndex  
**Values**: Dividend amounts per share

```python
dividends = ticker.dividends
# Date
# 2024-08-12 00:00:00-04:00    0.25
# 2024-11-08 00:00:00-05:00    0.25
# 2025-02-10 00:00:00-05:00    0.25
```

### Options Data (NamedTuple)

```python
option_chain = ticker.option_chain(expiration_date)
calls = option_chain.calls  # DataFrame
puts = option_chain.puts    # DataFrame
```

**Options DataFrame Columns**:
- `contractSymbol`: Option contract symbol
- `lastTradeDate`: Last trade timestamp
- `strike`: Strike price
- `lastPrice`: Last traded price
- `bid`: Bid price
- `ask`: Ask price
- `change`: Price change
- `percentChange`: Percentage change
- `volume`: Trading volume
- `openInterest`: Open interest
- `impliedVolatility`: Implied volatility
- `inTheMoney`: Boolean if in-the-money
- `contractSize`: Contract size
- `currency`: Currency

## Advanced Features

### Multiple Tickers

```python
# Method 1: Using Tickers class
tickers = yf.Tickers('MSFT AAPL GOOG')
data = tickers.tickers['MSFT'].info

# Method 2: Using download function
data = yf.download(['MSFT', 'AAPL', 'GOOG'], period='1mo')
```

### Financial Analysis Data

```python
# Analyst recommendations
recommendations = ticker.recommendations
recommendations_summary = ticker.recommendations_summary

# Earnings data
earnings = ticker.earnings
quarterly_earnings = ticker.quarterly_earnings
earnings_dates = ticker.earnings_dates

# Analyst estimates
analyst_price_targets = ticker.analyst_price_targets
earnings_estimate = ticker.earnings_estimate
revenue_estimate = ticker.revenue_estimate
eps_trend = ticker.eps_trend
eps_revisions = ticker.eps_revisions
growth_estimates = ticker.growth_estimates

# Institutional data
institutional_holders = ticker.institutional_holders
major_holders = ticker.major_holders
insider_transactions = ticker.insider_transactions
```

### Fund Data

```python
# For ETFs and mutual funds
spy = yf.Ticker('SPY')
fund_data = spy.funds_data

if fund_data:
    print(fund_data.description)
    print(fund_data.top_holdings)
```

### Market Data

```python
# Market summary
market = yf.Market()
market_data = market.get_market_summary()
```

### Live Data Streaming

```python
# WebSocket for live data
ws = yf.WebSocket(['AAPL', 'MSFT'])
ws.start()

# Async WebSocket
import asyncio
async_ws = yf.AsyncWebSocket(['AAPL'])
asyncio.run(async_ws.start())
```

## Common Parameters

### History Method Parameters

```python
ticker.history(
    period="1mo",        # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval="1d",       # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    start="2020-01-01",  # Start date (alternative to period)
    end="2023-01-01",    # End date (alternative to period)
    prepost=True,        # Include pre/post market data
    auto_adjust=True,    # Auto-adjust prices for splits/dividends
    back_adjust=False,   # Back-adjust prices
    repair=False,        # Repair bad data
    keepna=False,        # Keep NaN values
    proxy=None,          # Proxy settings
    rounding=False,      # Round values
    timeout=10           # Request timeout
)
```

## Error Handling

```python
import yfinance as yf

try:
    ticker = yf.Ticker("INVALID")
    data = ticker.history(period="1mo")
    if data.empty:
        print("No data found for ticker")
except Exception as e:
    print(f"Error fetching data: {e}")
```

## Best Practices

1. **Rate Limiting**: Yahoo Finance has rate limits. Add delays between requests for large datasets.

2. **Data Validation**: Always check if returned data is empty or contains expected columns.

3. **Timezone Awareness**: Historical data includes timezone information. Handle accordingly.

4. **Caching**: yfinance caches some data. Use `ticker.get_info(proxy=None)` to force refresh.

5. **Error Handling**: Wrap API calls in try-catch blocks as network issues can occur.

## Common Use Cases

### Backtesting Data Preparation

```python
def get_stock_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)
    data = ticker.history(start=start_date, end=end_date)
    
    # Validate data
    if data.empty:
        raise ValueError(f"No data found for {symbol}")
    
    # Clean data
    data = data.dropna()
    
    return data[['Open', 'High', 'Low', 'Close', 'Volume']]
```

### Portfolio Analysis

```python
def get_portfolio_data(symbols, period="1y"):
    data = yf.download(symbols, period=period)['Close']
    returns = data.pct_change().dropna()
    return returns
```

### Fundamental Analysis

```python
def get_fundamental_metrics(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    return {
        'pe_ratio': info.get('trailingPE'),
        'market_cap': info.get('marketCap'),
        'dividend_yield': info.get('dividendYield'),
        'beta': info.get('beta'),
        'debt_to_equity': info.get('debtToEquity')
    }
```

## Limitations

1. **Data Quality**: Yahoo Finance data may have gaps or errors
2. **Rate Limits**: Heavy usage may trigger rate limiting
3. **Real-time Data**: Free tier has 15-20 minute delays
4. **Historical Limits**: Some data may not be available for older periods
5. **Corporate Actions**: Stock splits and dividends may affect historical data consistency

## Alternative Data Sources

For production use, consider:
- Alpha Vantage
- Quandl
- IEX Cloud
- Polygon.io
- Bloomberg API (paid)
- Refinitiv (paid)
