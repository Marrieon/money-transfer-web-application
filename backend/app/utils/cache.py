def generate_cache_key(prefix: str, *args) -> str:
    """
    Generates a consistent cache key from a prefix and arguments.
    Example: generate_cache_key('user_profile', 123) -> 'user_profile:123'
    """
    key_parts = [str(arg) for arg in args]
    return f"{prefix}:" + ":".join(key_parts)