import pytest
from model import onePeriodBinomialModel

def test_knownValues(): 

    # Tests first manual calculation done on paper
    out = onePeriodBinomialModel(100, 100, 1.2, 0.9, 0.05, "c")
    assert out["outputs"]["option_price"] == pytest.approx(9.52, abs=0.005)
    
    # Tests a pre-calculated put-call pair
    out = onePeriodBinomialModel(100, 100, 1.3, 0.8, 0.1, "c")
    assert out["outputs"]["option_price"] == pytest.approx(16.36, abs=0.005)
    out = onePeriodBinomialModel(100, 100, 1.3, 0.8, 0.1, "p")
    assert out["outputs"]["option_price"] == pytest.approx(7.27, abs=0.005)
    