import yfinance as yf

stocks = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "NFLX",
    "BA",
    "DIS"
]

def fetch_data():
    data = {}
    for stock in stocks:
        ticker = yf.Ticker(stock)
        hist = ticker.history(period="1d")
        data[stock] = {
            "close": hist["Close"].iloc[-1],
            "volume": hist["Volume"].iloc[-1]
        }
    return data
