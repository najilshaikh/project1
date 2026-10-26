import yfinance as yf
# Replace 'AAPL' with any company ticker symbol you want to check (e.g., TSLA, MSFT, GOOGL)
ticker_symbol = "AAPL"
# Create a Ticker object
stock = yf.Ticker(ticker_symbol)
# Fetch the current fast info or regular market price
current_price = stock.fast_info['lastPrice']
print(f"The current value of {ticker_symbol} is: ${current_price:.2f}")
