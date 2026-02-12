from app.utils.helpers import format_currency
from decimal import Decimal

def test_format_currency():
    """Test the currency formatting helper."""
    assert format_currency(Decimal("1234.56")) == "$1,234.56"
    assert format_currency(Decimal("50.00"), "EUR") == "€50.00"
    assert format_currency(Decimal("100"), "JPY") == "JPY 100.00"