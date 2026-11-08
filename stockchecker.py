import warnings
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
token = 'TOKEN'

#silence all warnings matching the "inplace" warning message pattern
warnings.filterwarnings("ignore",message=".*inplace.*")
#catcha and suppress everyrthing explicitly raised under the Pandas4Warning namespace
# warnings.filterwarnings("ignore",category=UserWarnins, module="yfinance")
# Replace 'AAPL' with any company ticker symbol you want to check (e.g., TSLA, MSFT, GOOGL)
# ticker_symbol = "AAPL"
# Create a Ticker object

user_input= input("Enter stock name:\n").upper().strip()
try:
    stock = yf.Ticker(user_input)
    # Fetch the current fast info or regular market price
    current_price = stock.fast_info['lastPrice']
    if current_price is None:
        print(f"Error: {user_input} is not a valid stock")
    else:
        print(f"The current value of {user_input} is: ${current_price:.2f}")
except Exception as e:
    print(f"Error: Could not fetch data for {user_input}, please confirm your symbol is correct.")
except ConnectionError as ce:
    print(f"there has been a connection rror: {ce}")
