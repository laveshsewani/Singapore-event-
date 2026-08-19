from datetime import datetime
from dateutil import parser as dateparser

from .sources import DATE_WINDOW_START, DATE_WINDOW_END

WINDOW_START = datetime.fromisoformat(DATE_WINDOW_START)
WINDOW_END = datetime.fromisoformat(DATE_WINDOW_END)


def is_in_window(date_text):
    """True if date_text falls in the window, or if it can't be parsed
    confidently. Unknowns are kept — the generic-listing filter in
    pipeline.py already catches the real source of junk (multi-year
    category pages), so this can stay lenient without letting those back in."""
    if not date_text:
        return True
    try:
        parsed = dateparser.parse(date_text, fuzzy=True, default=datetime(2026, 1, 1))
    except (ValueError, OverflowError):
        return True
    return WINDOW_START <= parsed <= WINDOW_END