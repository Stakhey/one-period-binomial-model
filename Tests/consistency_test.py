import pytest 
from model import onePeriodBinomialModel

def test_consistency():
    
    # (Delta * S_0) + B = V_0
    out = onePeriodBinomialModel(100, 100, 1.3, 0.8, 0.1, "c")
    replicationCost = out["outputs"]["hedge_ratio"] * out["inputs"]["spot_S_0"] + out["outputs"]["B"]
    assert  replicationCost == pytest.approx(out["outputs"]["option_price"])
