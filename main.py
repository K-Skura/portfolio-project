import yfinance as yf
import pandas as pd 
import streamlit as st
import time
import keyboard
import os
import psutil


class Security:
    def __init__(self,ticker, sec_type = "Stock", quantity = 1):
        self.ticker = ticker
        self.sec_type = sec_type    #As for now all will be Stock
        self.data  = None          #It will be fetched with yf data
        self.quantity = quantity

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


# Apply the class 
portfolio = {ticker: Security(ticker = ticker) for ticker in securities_tickers}

#Download the data for each security
for sec in portfolio.values():
    sec.upload_yf_data()


#Ask for the quantity, can be below the downloading of data 

st.write("You selected the following Tickers, now please add the quantity")

for sec in portfolio.values():
    sec.quantity = st.number_input(
        f"{sec.ticker} quantity", min_value = 0
    )

try:
    hist_performance = pd.concat({
        ticker: sec.data["Close"]
        for ticker, sec in portfolio.items()
        if sec.data is not None and not sec.data.empty and "Close" in sec.data.columns 
    }, 
    axis = 1)
    hist_performance.columns = hist_performance.columns.get_level_values(0) # Added due to the problem with multiindexing
    st.line_chart(hist_performance)

except ValueError:
    st.info("No securities selected yet or no data available.")


portfolio_value = 0

for sec in portfolio.values():
    if sec.data is not None:
        try: 
            latest_price = sec.data["Close"].iloc[-1].item() #Error occured due to the returning the whole single element series - repaired using item()
            value = latest_price * sec.quantity
            portfolio_value += value
        except KeyError:
            print("There was a problem with calculating the value per security. ")

st.write(f"Total value of your portfolio is: {portfolio_value}")


# Source: https://discuss.streamlit.io/t/close-streamlit-app-with-button-click/35132
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