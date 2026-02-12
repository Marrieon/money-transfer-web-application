import requests
from flask import current_app
from app.extensions import cache

# A free API that doesn't require a key for basic use.
# In production, you'd use a more robust service with an API key.
BASE_URL = "https://open.er-api.com/v6/latest/"

def get_exchange_rate(base_currency: str, target_currency: str) -> float:
    """
    Fetches the exchange rate between two currencies.
    Results are cached for 1 hour to reduce external API calls.
    """
    # Create a unique cache key
    cache_key = f"exchange_rate_{base_currency}_{target_currency}"
    cached_rate = cache.get(cache_key)
    
    if cached_rate:
        return cached_rate

    try:
        url = f"{BASE_URL}{base_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        
        if data.get("result") == "error":
            # Handle API-specific errors
            raise ConnectionError(f"Exchange rate API error: {data.get('error-type')}")

        rate = data.get("rates", {}).get(target_currency)
        
        if rate is None:
            raise ValueError(f"Target currency '{target_currency}' not found in API response.")

        # Cache the result for 1 hour (3600 seconds)
        cache.set(cache_key, float(rate), timeout=3600)
        
        return float(rate)

    except (requests.exceptions.RequestException, ConnectionError, ValueError) as e:
        current_app.logger.error(f"Could not fetch exchange rate: {e}")
        # Return a default/fallback rate or raise the error
        # For simplicity, we'll return a default of 1.0 on failure
        return 1.0