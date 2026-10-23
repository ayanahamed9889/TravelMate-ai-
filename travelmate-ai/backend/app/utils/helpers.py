from datetime import date, datetime, timedelta


def parse_date(value) -> date | None:
    """'YYYY-MM-DD' (or full ISO string) -> date, or None if missing/invalid."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).strip()[:10]).date()
    except ValueError:
        return None


def days_between(start: str | None, end: str | None, default: int = 3) -> int:
    """Inclusive number of days between two ISO dates."""
    s, e = parse_date(start), parse_date(end)
    if not s or not e:
        return default
    return max(1, (e - s).days + 1)


def date_plus(start: str | None, offset_days: int) -> str:
    s = parse_date(start)
    return (s + timedelta(days=offset_days)).isoformat() if s else ""


def today_iso() -> str:
    return date.today().isoformat()
