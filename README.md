# One Period Binomial Model 
One-period binomial model for pricing European call and put options by replication. The model also checks that the market is arbitrage-free, and contains a test suite checking for consistency in calculation methods and that put-call parity is preserved. Inputs can either be entered manually or sourced from real stock data by calling the Yahoo Finance and FRED APIs. The model assumes that one period is one day, and that the 1-day risk free rate can be calculated from the 3-month rate data provided by the Federal Reserve Bank of St Louis. 

## User Guide
In order to install the required packages, run the command:
```
pip install yfinance fredapi pytest
``` 
A FRED API key can be requested at https://fred.stlouisfed.org/docs/api/api_key.html. This should be added to a file called api_key.py with the variable name key. 

In order to use the included tests, run the command: 
``` 
python -m pytest
```

## Replication Tables 
### Parameters
| Parameter | Value |
|---|---|
| S₀ | 100 |
| K | 100 |
| u | 1.3 |
| d | 0.8 |
| r | 0.1 |
| q | 0.6 |

### Call

Δ = 0.6, B = −43.64

| | Today (t = 0) | Up state | Down state |
|---|---|---|---|
| Stock price | 100.00 | 130.00 | 80.00 |
| Stock position | 60.00 | 78.00 | 48.00 |
| Bond position | −43.64 | −48.00 | −48.00 |
| **Replicating portfolio** | 16.36 | 30.00 | 0.00 |
| **Option value** | 16.36 | 30.00 | 0.00 |
| Difference | 0.00 | 0.00 | 0.00 |

### Put

Δ = −0.4, B = 47.27

| | Today (t = 0) | Up state | Down state |
|---|---|---|---|
| Stock price | 100.00 | 130.00 | 80.00 |
| Stock position | −40.00 | −52.00 | −32.00 |
| Bond position | 47.27 | 52.00 | 52.00 |
| **Replicating portfolio** | 7.27 | 0.00 | 20.00 |
| **Option value** | 7.27 | 0.00 | 20.00 |
| Difference | 0.00 | 0.00 | 0.00 |

## Project Reflections
### Takeaways
- Tech: Started learning how to use Yahoo Finance and FRED APIs 
- Tech: Started learning how to write tests using pytest  
- Tech: Learnt how to output data to an external JSON file for further processing
- Tech: Learnt how to manually create error messages in Python
- Finance: There are 252 trading days in a year, so this is often the number used rather than 365 in financial models
- Finance: Options are the right, but not the obligation, to buy or sell a stock at a fixed strike price. European options can only be exercised on the given expiration date, whereas American options can be exercised before the given expiration date
- Finance: Clients protect their position or speculate by buying options, the desk can borrow for cheaper and has fewer transaction fees, which incentivises the client to approach the desk for this service
- Finance: Arbitrage is a strategy that can never lose, the model is arbitrage free when d < 1 + r < u  
- Maths: $\Delta$, the hedge ratio, is equal to the spread of option payoffs over the spread of stock prices, derived from solving the simultaneous equations $\Delta S_u+(1+r)B = V_u$ and $\Delta S_d+(1+r)B = V_d$ to get $\Delta = \frac{V_u - V_d}{S_u - S_d}$
- Maths: The put-call parity equation is $C_0-P_0=S_0-\frac{K}{1+r}$ 
- Maths: The risk neutral probability, q, is a weight, and the option price is the discounted q-weighted average of the payoffs, $q=\frac{(1+r)S_0-S_d}{S_u-S_d}$


### Possible Extensions
- Extend from a one-period to an n-period binomial tree
- Translate from a Python to a C++ implementation 
- Learn how to make more aesthetic CLI apps using rich