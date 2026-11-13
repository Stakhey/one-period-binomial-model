import pytest 
from model import onePeriodBinomialModel 

def test_putCallParity(): 
    # Outputs call and put price for the same stock
    outCall = onePeriodBinomialModel(100, 100, 1.3, 0.8, 0.1, "c")
    outPut = onePeriodBinomialModel(100, 100, 1.3, 0.8, 0.1, "p")
   
    # C_0 + X / (1 + r)^t = P_0 + S_0, t = 1
    lhs = outCall["outputs"]["option_price"] + (outCall["inputs"]["strike_K"]) / (1 + outCall["inputs"]["daily_rate_r"])
    rhs = outPut["outputs"]["option_price"] + (outPut["inputs"]["spot_S_0"])
   
    # Tests to see that put-call parity is maintained
    assert lhs == pytest.approx(rhs)