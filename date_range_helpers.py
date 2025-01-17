from datetime import date, timedelta
import datetime

month_dict = {
    1:'january',
    2:'february',
    3:'march',
    4:'april',
    5:'may',
    6:'june', 
    7:'july',
    8:'august',
    9:'september',
    10:'october',
    11:'november',
    12:'december'
}

short_month_dict = {
    1:'jan',
    2:'feb',
    3:'mar',
    4:'apr',
    5:'may',
    6:'jun', 
    7:'jul',
    8:'aug',
    9:'sep',
    10:'oct',
    11:'nov',
    12:'dec'
}


# This class is used to represent an incomplete isodate, like 2023-06, which represents
# a date with month-granularity
class YearMonth:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.day = 1
        self.month_name = month_dict[month]
        self.short_month_name = short_month_dict[month]
    
    def __str__(self):
        month_str = '0' + str(self.month) if self.month < 10 else str(self.month)
        return str(self.year) + '-' + month_str
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month

    def copy(self):
        return YearMonth(self.year, self.month)
    
    def increment_month(self):
        if self.month == 12:
            self.year += 1
            self.month = 1
        else:
            self.month += 1
        # self.d = date(self.year, self.month, 1)

    def get_current_yearmonth():
        today = date.today()
        return YearMonth(today.year, today.month)
# def standardize_date(_date):
#     if _date.day:
#         return _date
#     else:
#         return date(_date.year, _date.month, 1)
    

def convert_to_date(_date):
    if type(_date) == int:
        today = date.today()
        _date = today + timedelta(_date)
    return _date


# I'm 99% sure this is bug-free
def form_date_range_in_days(start, end):
    """
    Given start and end dates (each of which has year, month, and day attributes), create a list of dates
    covering the given range, inclusive of start and exclusive of end
    """
    # start = standardize_date(start)
    # end   = standardize_date(end)
    if start == end:
        return [start]
    dates = []
    _date = date(start.year, start.month, start.day)
    # end   = date(end.year,   end.month,   end.day  )
    while _date != end:
        dates.append(_date)
        _date = _date + timedelta(days=1)
    return dates


def form_days_range_from_period(period):
    days = []
    for _date in period:
        if type(_date) == YearMonth:
            days.extend(collect_days_of_month(_date))
        else:
            days.append(_date)
    return days


def form_date_range_in_months(start : YearMonth, end : YearMonth) -> list:
    if start == end:
        return [start]
    months = []
    yearmonth = YearMonth(start.year, start.month)
    while yearmonth != end:
        months.append(yearmonth)
        new_ym = yearmonth.copy()
        new_ym.increment_month()
        yearmonth = new_ym
    return months


def collect_days_of_month(yearmonth : YearMonth):
    boundary = yearmonth.copy()
    boundary.increment_month()
    return form_date_range_in_days(yearmonth, boundary)


def format_now():
    n = datetime.datetime.now()
    ampm = 'am'
    hour = n.hour
    if hour > 12:
        hour -= 12
        ampm = 'pm'
    ym = YearMonth(n.year, n.month)
    return f'{str(ym)}-{n.day} {hour}:{n.minute}:{n.second} {ampm}'


def main():
    s = YearMonth(2024,3)
    e = YearMonth(2024,4)
    form_date_range_in_months(s,e)

# if __name__ == '__main__':
#     main()