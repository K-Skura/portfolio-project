import yfinance as yf
import pandas as pd 
import streamlit as st
import time
import keyboard
import os
import psutil


class Security:
    def __init__(self,ticker, sec_type = "Stock"):
        self.ticker = ticker
        self.sec_type = sec_type    #As for now all will be Stock
        self.data  = None          #It will be fetched with yf data
        

    def upload_yf_data(self): 
        try:
            self.data = yf.download(self.ticker, period="max")
        except Exception as e:
            print(f"Error download the data for: {self.ticker}: {e}")
            self.data = None


# Read data of all the securities options listed in Nasdaq 
nasdaq = pd.read_csv("nasdaq-listed-symbols.csv")
nasdaq = nasdaq.dropna(subset=["Security Name", "Symbol"])


# Create values that will be displayed for a look up
nasdaq["Display"] = nasdaq.apply(lambda x: f"{x["Symbol"]} - {x["Security Name"]}", axis = 1)
securities_to_display = nasdaq["Display"].tolist()


# Streamlit app
st.title("Portfolio Overview")
st.write("Hi, I am gonna show your whole portolio in one place. Please select securities that you have :D ")

with st.container(border = True):
    opt = st.multiselect("Securities", securities_to_display, default = None)

#List comprehension to select only ticker

securities_tickers = [item.split(" - ")[0] for item in opt] 

st.write("You selected the following Tickers")

for ticker in securities_tickers:
    st.write(ticker)


# Apply the class 
portfolio = [Security(ticker= ticker) for ticker in securities_tickers]

for sec in portfolio:
    sec.upload_yf_data()
    #create an object using class Securities that download yf data for each security

# For the ease of use create a dic with tickers as keys and df as values

portfolio_data = {sec.ticker:sec.data for sec in portfolio if sec.data is not None}

all_close = []

for ticker,df in portfolio_data.items():
    if df is not None and not df.empty:
        try:
            close = df["Close"].copy()
            close.name = ticker
            all_close.append(close)
        except KeyError:
            print(f"{ticker} does not have a 'close' column.")


if all_close:
    close_prices = pd.concat(all_close, axis=1)
    st.line_chart(close_prices)
    st.dataframe(close_prices)
else:
    st.info("No securities selected yet or no data available.")


# Found on Stack overflow
exit_app = st._bottom.button("Shut Down")
if exit_app:
    # Give a bit of delay for user experience
    time.sleep(1)
    # Close streamlit browser tab
    keyboard.press_and_release('ctrl+w')
    # Terminate streamlit python process
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()