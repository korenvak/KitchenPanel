# file: panel_app/utils/rtl.py
import arabic_reshaper
from bidi.algorithm import get_display

def rtl(text: str) -> str:
    """Reshape and apply bidi algorithm"""
    if not isinstance(text, str):
        text = str(text)
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text[::-1]
