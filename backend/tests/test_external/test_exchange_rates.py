
import requests_mock
from app.api.external.exchange_rates import get_exchange_rate

def test_get_exchange_rate_success(client):
    """Test successfully fetching an exchange rate with mocking."""
    base_currency = "USD"
    target_currency = "EUR"
    
    # The mock response we expect from the API
    mock_response = {
        "result": "success",
        "rates": {
            "USD": 1,
            "EUR": 0.92,
            "GBP": 0.78
        }
    }
    
    with requests_mock.Mocker() as m:
        # Intercept any GET request to this URL
        m.get(f"https://open.er-api.com/v6/latest/{base_currency}", json=mock_response)
        
        # Call our service function
        rate = get_exchange_rate(base_currency, target_currency)
        
        # Assert we got the correct rate from our mock response
        assert rate == 0.92
        
        # Call it again to test caching
        rate_cached = get_exchange_rate(base_currency, target_currency)
        assert rate_cached == 0.92
        # Assert that the external API was only called once because the second call was cached
        assert m.call_count == 1