from app.utils.cache import generate_cache_key

def test_generate_cache_key():
    """Test the cache key generation utility."""
    assert generate_cache_key('profile', 123) == 'profile:123'
    assert generate_cache_key('transactions', 123, 'sent') == 'transactions:123:sent'
    assert generate_cache_key('user') == 'user:'