import yfinance as yf 
import numpy as np 
import matplotlib.pyplot as plt 
import mplfinance as mpf 
import pandas as pd 
import tkinter as tk 
from tkinter import messagebox, ttk 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

NIFTY_50_STOCKS = [ "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "HCLTECH.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "NTPC.NS", "POWERGRID.NS", "NESTLEIND.NS", "INDUSINDBK.NS", "BAJAJFINSV.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "ONGC.NS", "COALINDIA.NS", "GRASIM.NS", "TECHM.NS", "TATASTEEL.NS", "HDFCLIFE.NS", "ADANIPORTS.NS", "HINDALCO.NS", "CIPLA.NS", "DIVISLAB.NS", "SBILIFE.NS", "BRITANNIA.NS", "EICHERMOT.NS", "APOLLOHOSP.NS", "HEROMOTOCO.NS", "BPCL.NS", "UPL.NS", "DRREDDY.NS", "BAJAJ-AUTO.NS", "M&M.NS", "TATACONSUM.NS", "SHREECEM.NS", "IOC.NS" ]

def fetch_stock_data(symbol): 
    #Fetch live stock data from Yahoo Finance
    stock = yf.Ticker(symbol) 
    data = stock.history(period="1y") 
    data.index = pd.to_datetime(data.index) 
    return data, stock

def process_stock_data(data, stock): #"""Process stock data to extract relevant values""" 
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
    
    return data

def plot_candlestick_chart(data, symbol): 
    fig, ax = plt.subplots(figsize=(8, 4)) 
    mpf.plot(data, type='candle', ax=ax, style='charles') 
    ax.set_title(f"Candlestick Chart: {symbol}", fontsize=12) 
    return fig

def on_fetch(): 
    symbol = stock_combo.get().strip().upper() 
    if not symbol: 
        messagebox.showerror("Error", "Please select a stock symbol.") 
        return

    stock_data, stock_info = fetch_stock_data(symbol)
    processed_data = process_stock_data(stock_data, stock_info)

    if processed_data is None:
        messagebox.showerror("Error", "Failed to retrieve stock data.")
        return

    fig = plot_candlestick_chart(processed_data, symbol)
    canvas = FigureCanvasTkAgg(fig, master=frame_chart)
    canvas.get_tk_widget().pack()
    canvas.draw()

#Create the main application window

root = tk.Tk() 
root.title("Nifty 50 Stock Analysis Tool") 
root.geometry("800x600")

frame_input = tk.Frame(root) 
frame_input.pack(pady=10)

label = tk.Label(frame_input, text="Select Stock:")
label.pack(side=tk.LEFT)

stock_combo = ttk.Combobox(frame_input, values=NIFTY_50_STOCKS, width=20) 
stock_combo.pack(side=tk.LEFT, padx=5)

button = tk.Button(frame_input, text="Fetch Data", command=on_fetch)
button.pack(side=tk.LEFT)

frame_chart = tk.Frame(root) 
frame_chart.pack(pady=20)

root.mainloop()
