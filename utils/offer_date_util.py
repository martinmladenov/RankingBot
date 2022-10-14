from datetime import date
import constants

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


def parse_offer_date(day: str, month: str, year: int = constants.current_year):
    parsed_day = int(day)
    month = month.lower()

    if month in months:
        parsed_month = months[month]
    else:
        parsed_month = int(month)

    return date(year, parsed_month, parsed_day)


def format_offer_date(offer_date: date):
    return offer_date.strftime('%-d %B')
