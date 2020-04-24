from datetime import date

months = {
    'apr': 4,
    'april': 4,
    'may': 5,
    'jun': 6,
    'june': 6,
    'jul': 7,
    'july': 7,
    'aug': 8,
    'august': 8
}


def parse_offer_date(day: str, month: str):
    parsed_day = int(day)
    month = month.lower()

    if month in months:
        parsed_month = months[month]
    else:
        parsed_month = int(month)

    return date(2020, parsed_month, parsed_day)
