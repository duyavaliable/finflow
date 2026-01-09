from datetime import datetime
from typing import Any

def format_currency(amount: float) -> str:
    """Format số tiền thành VND"""
    return f"{amount:,.0f} đ"

def format_date(date_str: str) -> str:
    """Format ngày tháng"""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str

def validate_amount(amount: Any) -> float:
    """Validate và convert số tiền"""
    try:
        value = float(amount)
        if value < 0:
            raise ValueError("Số tiền không được âm")
        return value
    except (TypeError, ValueError) as e:
        raise ValueError(f"Số tiền không hợp lệ: {amount}")
