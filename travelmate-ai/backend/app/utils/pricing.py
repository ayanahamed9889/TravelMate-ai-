"""Rough price level per country, relative to India (= 1.0).

Used to scale local transport and activity costs, so a cab ride in Paris is not priced like
an auto-rickshaw in Jaipur. These are planning estimates, not quotes.
"""
DEFAULT_INDEX = 3.0

COUNTRY_INDEX = {
    "IN": 1.0, "NP": 0.9, "LK": 1.0, "BT": 1.2,
    "TH": 1.8, "VN": 1.4, "KH": 1.5, "ID": 1.7, "MY": 1.9, "PH": 1.6, "SG": 4.5, "JP": 3.8, "KR": 3.3,
    "HK": 4.0, "CN": 2.2, "MV": 4.0, "TW": 3.0,
    "AE": 3.4, "QA": 3.6, "OM": 2.8, "JO": 2.4, "TR": 2.2, "SA": 3.0, "IL": 5.0,
    "EG": 1.3, "MA": 1.6, "ZA": 1.9, "KE": 2.2, "TZ": 2.2, "MU": 3.0,
    "FR": 4.5, "GB": 5.0, "IT": 4.0, "ES": 3.5, "NL": 4.5, "CZ": 2.8, "AT": 4.2, "CH": 7.0, "GR": 3.3,
    "PT": 3.2, "IS": 6.5, "DE": 4.2, "HU": 2.6, "PL": 2.4, "SE": 5.0, "NO": 6.5, "DK": 5.5, "IE": 4.8, "BE": 4.4,
    "US": 5.5, "CA": 4.8, "MX": 2.5, "BR": 2.2, "AR": 2.0, "PE": 1.8, "CL": 2.6, "CO": 1.8, "CU": 2.0,
    "AU": 5.0, "NZ": 4.6, "FJ": 3.0,
}


def price_index(cc: str | None) -> float:
    return COUNTRY_INDEX.get((cc or "").upper(), DEFAULT_INDEX)
