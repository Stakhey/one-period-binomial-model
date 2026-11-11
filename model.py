import yfinance as yf 
from fredapi import Fred
from apikey import key
import math
import pandas as pd
import json
from datetime import datetime

def realStockData(selected_stock, K):

    # Uses yfinance to store specific stock data over the last 30 days to get volatility and spot price
    ticker = yf.Ticker(selected_stock)
    ticker_history = ticker.history(period = "1mo", interval = "1d")
    ticker_percentage = ticker_history["Close"].pct_change().dropna()
    volatility = ticker_percentage.std()
    print(volatility)

    # Uses CRR model to get values for u and d, t = 1 day so root delta t = 1
    u = math.exp(volatility)
    d = math.exp(-volatility)
    print(u)
    print(d)

    ticker_spotprice = ticker.info["currentPrice"]
    print(ticker_spotprice)

    # Connects to FRED API and fetches most recent r from 1 month US treasury yield time series
    fred = Fred(api_key=key)
    r_annual = (fred.get_series("DGS1MO").iloc[-1]) / 100 
    # Converts yearly r to daily r, (1+r_daily)^252 = 1 + r_annual
    r_daily = (1 + r_annual)**(1/252) - 1
    print (r_daily + 1)

    return onePeriodBinomialModel(K, ticker_spotprice, u, d, r_daily)

def onePeriodBinomialModel(K, S_0, u, d, r): 

    # Runs all functions of the model
    is_arbitrage = isArbitrageFree(d, r, u)
    S_u, S_d, C_u, C_d, C_0 = optionPrice(S_0, K, u, d, r)
    q = riskNeutralProbability(S_0, S_u, S_d, r)
    delta, B = replicationPortfolio(C_u, C_d, S_u, S_d, r)

    # Returns dictionary of collected data for display
    return {
        "arbitrage_free": is_arbitrage,
        "S_u": S_u,
        "S_d": S_d,
        "C_u": C_u,
        "C_d": C_d,
        "risk_neutral_probability": q,
        "option_price": C_0,
        "hedge_ratio": delta,
        "B": B
    }

# Function that checks market is arbitrage free: d < 1 + r < u
def isArbitrageFree(d, r, u):

    if ((d < (1 + r)) != True or ((1 + r) < u) != True): 
        arbitrageFlag = False; 
        raise ValueError("Arbitrage condition violated: d < 1 + r < u is false")
    else: 
        arbitrageFlag = True;

    return arbitrageFlag

def riskNeutralProbability(S_0, S_u, S_d, r_daily): 
    q = ((1 + r_daily)*S_0 - S_d) / (S_u - S_d)
    return q

def optionPrice(S_0, K, u, d, r_daily):  

    # Calculates up and down states using the deterministic multipliers
    S_u = S_0 * u 
    S_d = S_0 * d 

    # Calculates options payoffs
    C_u = max(S_u - K, 0) 
    C_d = max(S_d - K, 0)

    # Calculate option price
    q = riskNeutralProbability(S_0, S_u, S_d, r_daily)
    C_0 = (q * C_u + (1 - q) * C_d) / (1 + r_daily)

    return S_u, S_d, C_u, C_d, C_0

def replicationPortfolio(C_u, C_d, S_u, S_d, r_daily): 

    # Spread of option payoffs over spread of stock priecs
    hedge_ratio = (C_u - C_d) / (S_u - S_d)  

    # B, how much we should hegde by
    risk_free_asset = (C_u - S_u * hedge_ratio) / (1 + r_daily)

    return hedge_ratio, risk_free_asset 

def outputJSON(results, stock=None):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    output = {
        "timestamp": datetime.now().isoformat(),
        "stock": stock,
        "results": results
    }

    filename = f"{stock or 'imaginary_stock'}_{timestamp}.json"

    with open(filename, "w") as file:
        json.dump(output, file, indent=2)

    return filename

if __name__ == "__main__":

    entry_type = input("Real or imaginary stock data? (r/i: ") 

    # Prompts user to enter data for real stock
    if entry_type == "r": 

        selected_stock = input("Enter ticker symbol: ") 
        strike_price = float(input("Enter strike price (K): "))
        results = realStockData(selected_stock, strike_price) 
        json_output = outputJSON(results, selected_stock)
        print(f"Results saved to {json_output}")

    # Prompts user to enter data for imaginary stock
    elif entry_type == 'i': 

        strike_price = float(input("Enter strike price (K): "))
        spot_price = float(input("Enter spot price (S_0): "))
        up_factor = float(input("Enter up factor (u): "))
        down_factor = float(input("Enter down factor (d): "))
        risk_free_rate = float(input("Enter daily risk-free rate as a decimal (r): "))

        results = onePeriodBinomialModel(strike_price, spot_price, up_factor, down_factor, risk_free_rate)
        json_output = outputJSON(results)
        print(f"Results saved to {json_output}")

    else: 
        raise ValueError("Only 'r' and 'm' are acceptable inputs")