from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import Optional
import re


def normalize_date(raw: str, day_first: bool | None = None) -> Optional[str]:
    # Try multiple parsing heuristics
    candidates = []
    try:
        if day_first is None:
            dt = parser.parse(raw, default=None)
            return dt.date().isoformat()
        dt = parser.parse(raw, dayfirst=day_first)
        return dt.date().isoformat()
    except Exception:
        # Try strip ordinal suffixes like '1st', '2nd'
        raw2 = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", raw)
        try:
            dt = parser.parse(raw2)
            return dt.date().isoformat()
        except Exception:
            return None


def add_months(date_iso: str, months: int) -> str:
    dt = parser.isoparse(date_iso)
    dt2 = dt + relativedelta(months=months)
    return dt2.date().isoformat()


def days_between(date_iso1: str, date_iso2: str) -> int:
    d1 = parser.isoparse(date_iso1).date()
    d2 = parser.isoparse(date_iso2).date()
    return (d2 - d1).days
