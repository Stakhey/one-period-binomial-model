import yfinance as yf 
from fredapi import Fred
from apikey import key
import math
import pandas as pd
import json
from datetime import datetime

def realStockData(selected_stock, option_type, K):

    # Uses yfinance to store specific stock data over the last 90 days to get volatility and spot price
    ticker = yf.Ticker(selected_stock)
    ticker_history = ticker.history(period = "3mo", interval = "1d")
    ticker_percentage = ticker_history["Close"].pct_change().dropna()
    volatility = ticker_percentage.std()

    # Uses CRR model to get values for u and d, t = 1 day so root delta t = 1
    u = math.exp(volatility)
    d = math.exp(-volatility)

    ticker_spotprice = ticker.info["currentPrice"]

    # Connects to FRED API and fetches most recent r from 3 month US treasury yield time series
    fred = Fred(api_key=key)
    r_annual = (fred.get_series("DGS3MO").dropna().iloc[-1]) / 100 
    # Converts yearly r to daily r, (1+r_daily)^252 = 1 + r_annual, 252 trading days in a year
    r_daily = (1 + r_annual)**(1/252) - 1

    return onePeriodBinomialModel(K, ticker_spotprice, u, d, r_daily, option_type)

def onePeriodBinomialModel(K, S_0, u, d, r, option_type): 

    # Runs all functions of the model
    is_arbitrage = isArbitrageFree(d, r, u)
    S_u, S_d, V_u, V_d, V_0 = optionPrice(S_0, K, u, d, r, option_type)
    q = riskNeutralProbability(S_0, S_u, S_d, r)
    delta, B = replicationPortfolio(V_u, V_d, S_u, S_d, r)

    # Returns dictionary of collected data for display
    return {
        "inputs": {
            "option_type": option_type,
            "strike_K": K,
            "spot_S_0": S_0,
            "up_factor_u": u,
            "down_factor_d": d,
            "daily_rate_r": r,
        },
        "outputs": {
            "arbitrage_free": is_arbitrage,
            "S_u": S_u,
            "S_d": S_d,
            "V_u": V_u,
            "V_d": V_d,
            "risk_neutral_probability": q,
            "option_price": V_0,
            "hedge_ratio": delta,
            "B": B,
        },
    }

# Function that checks market is arbitrage free: d < 1 + r < u
def isArbitrageFree(d, r, u):

    if d < 1 + r < u: 
        arbitrageFlag = True; 
    
    else:
        arbitrageFlag = False;
        print("Arbitrage condition violated: d < 1 + r < u is false")

    return arbitrageFlag

def riskNeutralProbability(S_0, S_u, S_d, r_daily): 
    q = ((1 + r_daily)*S_0 - S_d) / (S_u - S_d)
    return q

# Calculates payoffs depending on if it's a call option or put option
def payoff(S, K, option_type):
    if option_type == "c":
        return max(S - K, 0)
    elif option_type == "p":
        return max(K - S, 0)
    
def optionPrice(S_0, K, u, d, r_daily, option_type):  

    # Calculates up and down states using the deterministic multipliers
    S_u = S_0 * u 
    S_d = S_0 * d 

    # Calculates options payoffs
    V_u = payoff(S_u, K, option_type)
    V_d = payoff(S_d, K, option_type)

    # Calculate option price
    q = riskNeutralProbability(S_0, S_u, S_d, r_daily)
    V_0 = (q * V_u + (1 - q) * V_d) / (1 + r_daily)

    return S_u, S_d, V_u, V_d, V_0

def replicationPortfolio(V_u, V_d, S_u, S_d, r_daily): 

    # Spread of option payoffs over spread of stock priecs
    hedge_ratio = (V_u - V_d) / (S_u - S_d)  

    # B, how much we should hegde by
    risk_free_asset = (V_u - S_u * hedge_ratio) / (1 + r_daily)

    return hedge_ratio, risk_free_asset 

def outputJSON(results, stock=None):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    output = {
        "timestamp": timestamp,
        "stock": stock,
        "results": results
    }

    filename = f"{stock or 'imaginary_stock'}_{timestamp}.json"

    with open(filename, "w") as file:
        json.dump(output, file, indent=2)

    return filename

def inputValidation(option_type): 
    if option_type != "call" or option_type != "put": 
        raise ValueError("Option input must be 'c' or 'p'")
        

if __name__ == "__main__":

    entry_type = input("Real or imaginary stock data? (r/i): ") 

    # Prompts user to enter data for real stock
    if entry_type == "r": 

        option_type = input("Is the option a call or a put? (c/p): ")
        selected_stock = input("Enter ticker symbol: ") 
        strike_price = float(input("Enter strike price (K): "))
        results = realStockData(selected_stock, option_type, strike_price) 
        json_output = outputJSON(results, selected_stock)
        print(f"Results saved to {json_output}")

    # Prompts user to enter data for imaginary stock
    elif entry_type == 'i': 

        option_type = input("Is the option a call or a put? (c/p): ")
        strike_price = float(input("Enter strike price (K): "))
        spot_price = float(input("Enter spot price (S_0): "))
        up_factor = float(input("Enter up factor (u): "))
        down_factor = float(input("Enter down factor (d): "))
        risk_free_rate = float(input("Enter daily risk-free rate as a decimal (r): "))

        results = onePeriodBinomialModel(strike_price, spot_price, up_factor, down_factor, risk_free_rate, option_type)
        json_output = outputJSON(results)
        print(f"Results saved to {json_output}")

    else: 
        raise ValueError("Only 'r' and 'i' are acceptable inputs")