def format_currency(amount, currency_code="USD") -> str:
    """Formats a numeric amount into a currency string."""
    # This is a basic implementation. A real app might use a library like 'babel'.
    # For now, we'll format to 2 decimal places.
    formatted_amount = f"{amount:,.2f}"
    
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency_code.upper(), f"{currency_code} ")
    return f"{symbol}{formatted_amount}"