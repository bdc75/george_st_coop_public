from datetime import date
from date_range_helpers import YearMonth
import sys
import params as p
import file_helpers


class UserInputException(Exception):
    def __init__(self, message):
        super().__init__(message)


def parse_entity_type(ent : str):
    if ent not in p.OPTS_ENTITY_TYPE:
        raise UserInputException(f"Unrecognized entity type <{ent}>")
    return ent


def parse_supplier(sup : str):
    if sup not in p.OPTS_SUPPLIER:
        raise UserInputException(f"Unrecognized supplier <{sup}>")
    return sup


def parse_int(integ : str):
    """
    Try to convert to integer
    e.g. "7" -> 7,  "-11" -> -11,  "+18" -> 18
    """
    try:
        return int(integ)
    except Exception:
        raise UserInputException(f"Expected an integer as an argument, received <{integ}> instead")


def parse_acct(acct : str):
    try:
        acct_number = int(acct)
    except Exception:
        raise UserInputException(f"Could not parse parameter <acct>, expected an account number, received <{acct}>")
    # Keep in the form of a string
    return acct


def parse_string(string : str):
    """
    Do nothing
    """
    return string


def parse_comma_list(clist : str) -> list:
    """
    Given non-empty string, return list split by the comma character
    e.g. "apple,banana" -> ['apple', 'banana']   or   "apple" -> ['apple']
    """
    comma_list = clist.split(',')
    for item in comma_list:
        if len(item) == 0:
            raise UserInputException(f'Empty string found in comma-separated list; list received as <{clist}>')
    return comma_list


def parse_loglevel(string : str) -> tuple:
    log_list = ['emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug']
    try:
        index = parse_int(string)
        return log_list[index]
    except IndexError:  # If index is not between 0-7
        raise UserInputException(
            f"Invalid log level <{index}> was provided, must be between 0-7 or one of {log_list}"
        )
    except Exception:  # If string value isn't an integer
        if string in log_list:
            return string
        else:  # If given string isn't one of the allowed debug types
            raise UserInputException(f"Invalid log level <{string}> was provided, must be between 0-7 or one of {log_list}")

    
def parse_date(isodate : str):
    #YYYY-MM-DD   or   YYYY-MM
    # If YYYY-MM-DD, a date object is returned
    # If YYYY-MM, a YearMonth object is returned
    try:
        return date.fromisoformat(isodate)
    except ValueError:
        if len(isodate) > len("2023-01"):
            raise UserInputException(f"Provided date <{isodate}> could not be parsed: incorrect format / day is out of range for month / month doesn't exist")
        if len(isodate) < len("2023-01"):
            raise UserInputException(f"Provided date <{isodate}> could not be parsed: not enough digits provided")
        try:
            # Fabricate a date with same year and month so it can be parsed using fromisoformat()
            new_isodate = isodate + "-01"    # Every month has a 1st of the month
            new_isodate = date.fromisoformat(new_isodate)
            return YearMonth(new_isodate.year, new_isodate.month)
        except ValueError:
            raise UserInputException(f"Provided date <{isodate}> could not be parsed: incorrect format / day is out of range for month / month doesn't exist")
       
    
def parse_startdate(startdate : str):
    try:
        return parse_date(startdate)
    except Exception:
        try:
            int_date_offset = parse_int(startdate)
            # if int_date_offset > 0:
            #     raise UserInputException("Expected non-positive date offset for parameter <start>")
            if int_date_offset < -2000:
                raise UserInputException(f"Exception: without this exception, the start date <{startdate}> would be treated as an integer offset")
            return int_date_offset
        except ValueError:
            raise UserInputException(f"Could not parse start date <{startdate}>")
            
    
def parse_enddate(enddate : str):
    try:
        return parse_date(enddate)
    except Exception:
        try:
            int_date_offset = parse_int(enddate)
            # if int_date_offset < 0:
            #     raise UserInputException("Expected positive date offset for parameter <end>")
            if int_date_offset > 2000:
                raise UserInputException(f"Exception: without this exception, the end date <{enddate}> would be treated as an integer offset")
            return int_date_offset
        except ValueError:
            raise UserInputException(f"Could not parse end date <{enddate}>")
            
            
#  FOR CATALOGS ONLY
def parse_period(period : str):
    raw_date_list = parse_comma_list(period)
    try:
        return list(map(parse_date, raw_date_list))
    except Exception:
        raise UserInputException("At least one of the dates provided with parameter <period> could not be parsed. Expected YYYY-MM or YYYY-MM-DD")


def parse_notifyfile(filename : str):
    filename = file_helpers.interpret_tilde(filename)
    # check file exists, and if so check write permissions
    if not file_helpers.file_is_writeable(filename):
        raise UserInputException(f'Notifyfile <{filename}> does not have write permissions')
    return filename


def parse_log(filename : str):
    filename = file_helpers.interpret_tilde(filename)
    # check file exists, and if so check write permissions
    if not file_helpers.file_is_writeable(filename):
        raise UserInputException(f'Log file <{filename}> does not have write permissions')
    return filename


def parse_throttle(throttle: str):
    """
    throttle=1M  (or 1m)  mibibits/sec
    throttle=256k         kibibits/sec
    throttle=1024

    return int, in units of bits per second
    """
    multipliers = {'k':1000, 'm':1000000}
    if throttle.isdigit():
        return parse_int(throttle)
    
    last_letter = throttle[-1].lower()
    digit = throttle[:-1]
    if (last_letter == 'k' or last_letter == 'm') and digit.isdigit():
        mult = multipliers[last_letter]
        return mult * parse_int(digit)
    else:
        raise UserInputException(
            f"Could not parse param <throttle>, expected digit or digit ending in 'k' or 'm'. Given '{throttle}'"
        )

