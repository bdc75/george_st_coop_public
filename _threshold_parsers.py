from default_parsers import parse_comma_list, YearMonth, UserInputException
from datetime import date
from params import REGULAR, SPECIALS


def parse_threshold_types(selections : str):
    selections = parse_comma_list(selections)
    options = ['regular', 'specials']
    for selection in selections:
        if selection not in {REGULAR, SPECIALS}:
            raise UserInputException(f"Option for param <type> must be one of {options}: was given <{selection}>")
    else:
        return selections
        

def parse_threshold_period(comma_list : str):
    isodate_list = parse_comma_list(comma_list)
    yearmonth_objs = []
    for isodate in isodate_list:
        try:
            # Fabricate a date with same year and month so it can be parsed using fromisoformat()
            new_isodate = isodate + "-01"    # Every month has a 1st of the month
            new_isodate = date.fromisoformat(new_isodate)
            yearmonth_objs.append(YearMonth(new_isodate.year, new_isodate.month))
        except ValueError:
            raise UserInputException(f"Provided date <{isodate}> could not be parsed: expected YYYY-MM / month doesn't exist")
    return yearmonth_objs