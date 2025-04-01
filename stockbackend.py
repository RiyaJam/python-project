import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import matplotlib.dates as mdates

def fetch_stock_data(symbol):
    """Fetch live stock data from Yahoo Finance"""
    stock = yf.Ticker(symbol)
    data = stock.history(period="1y")  
    data.index = pd.to_datetime(data.index)  
    return data, stock

def process_stock_data(data, stock):
    """Process stock data to extract relevant values"""
    if data.empty:
        return None
    
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["EMA_20"] = data["Close"].ewm(span=20, adjust=False).mean()
    data["BB_Mid"] = data["SMA_20"]
    data["BB_Upper"] = data["BB_Mid"] + 2 * data["Close"].rolling(window=20).std()
    data["BB_Lower"] = data["BB_Mid"] - 2 * data["Close"].rolling(window=20).std()

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    short_ema = data["Close"].ewm(span=12, adjust=False).mean()
    long_ema = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = short_ema - long_ema
    data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
    
    data["LTP"] = round(data["Close"].iloc[-1], 2)
    data["52_Week_High"] = round(data["High"].max(), 2)
    data["52_Week_Low"] = round(data["Low"].min(), 2)
    
    info = stock.info
    market_cap_crores = round(info.get("marketCap", 0) / 10**7, 2)  # Convert to crores
    dividend_yield = info.get("dividendYield", 0) * 100  # Convert to percentage
    pe_ratio = info.get("trailingPE", "N/A")
    eps = info.get("trailingEps", "N/A")
    volume = info.get("volume", "N/A")
    
    print(f"\nStock Information for {stock.ticker}")
    print(f"LTP: {data['LTP'].iloc[-1]}")
    print(f"52-Week High: {data['52_Week_High'].iloc[-1]}")
    print(f"52-Week Low: {data['52_Week_Low'].iloc[-1]}")
    print(f"Market Cap: {market_cap_crores} Crores")
    print(f"Dividend Yield: {dividend_yield:.2f}%")
    print(f"P/E Ratio: {pe_ratio}")
    print(f"EPS: {eps}")
    print(f"Volume: {volume}\n")
    
    return data

def plot_candlestick_chart(data, symbol):
    """Plot the candlestick chart in a separate window"""
    fig, ax = plt.subplots(figsize=(12, 6))
    mpf.plot(data[['Open', 'High', 'Low', 'Close', 'Volume']], type='candle', ax=ax, style='charles')
    ax.set_title(f"Candlestick Chart: {symbol}", fontsize=14)
    plt.show()

def plot_stock_graph(data, symbol):
    """Plot stock price, RSI, MACD, and additional indicators"""
    fig, ax = plt.subplots(4, 1, figsize=(14, 16), gridspec_kw={'height_ratios': [3, 1.5, 1.5, 1.5], 'hspace': 0.5})

    # Main stock price chart
    ax[0].plot(data.index, data["Close"], label="Close Price", color='b', alpha=0.6)
    ax[0].plot(data.index, data["SMA_20"], label="SMA 20", color='g', linestyle="--")
    ax[0].plot(data.index, data["EMA_20"], label="EMA 20", color='r', linestyle="--")
    ax[0].fill_between(data.index, data["BB_Upper"], data["BB_Lower"], color='gray', alpha=0.2, label="Bollinger Bands")
    ax[0].set_title(f"{symbol} Stock Price Trend", fontsize=14)
    ax[0].legend()
    ax[0].grid(True)

    # RSI Indicator
    ax[1].plot(data.index, data["RSI"], label="RSI", color="purple")
    ax[1].axhline(70, linestyle="--", color="red", alpha=0.5)
    ax[1].axhline(30, linestyle="--", color="green", alpha=0.5)
    ax[1].set_title("Relative Strength Index (RSI)", fontsize=12)
    ax[1].grid(True)

    # MACD Indicator
    ax[2].plot(data.index, data["MACD"], label="MACD", color="blue")
    ax[2].plot(data.index, data["MACD_Signal"], label="Signal Line", color="red", linestyle="--")
    ax[2].axhline(0, linestyle="--", color="black", alpha=0.5)
    ax[2].set_title("MACD (Moving Average Convergence Divergence)", fontsize=12)
    ax[2].legend()
    ax[2].grid(True)

    # Volume
    ax[3].bar(data.index, data["Volume"], label="Volume", color='gray', alpha=0.6)
    ax[3].set_title("Trading Volume", fontsize=12)
    ax[3].grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    stock_symbol = "RELIANCE.NS"
    stock_data, stock_info = fetch_stock_data(stock_symbol)
    processed_data = process_stock_data(stock_data, stock_info)

    if not processed_data.empty:
        plot_candlestick_chart(processed_data, stock_symbol)
        plot_stock_graph(processed_data, stock_symbol)
    else:
        print("Failed to retrieve stock data.")
