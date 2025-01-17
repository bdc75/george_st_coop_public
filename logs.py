import logging
import os
import sys
import traceback
import notify
import emailing
from datetime import datetime
from date_range_helpers import YearMonth
from file_helpers import interpret_tilde
from date_range_helpers import format_now

# python logging supports: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

log_dict = {
    # there is no python equivalent for 'emerg' and 'alert'
    'emerg':   logging.CRITICAL,
    'alert':   logging.CRITICAL,
    'crit':    logging.CRITICAL,
    'err':     logging.ERROR,
    'warning': logging.WARNING,
    'notice':  logging.INFO,
    'info':    logging.INFO,
    'debug':   logging.DEBUG
}

SUBJ_PARAM = 'Automated msg: parameter exception occurred'
def print_stderr(msg : str, caller : str, email_recip=None, subject=SUBJ_PARAM):
    msg = f'{caller}:\n  {msg}'
    print(msg, file=sys.stderr)
    emailing.send_email_if_desired(email_recip, subject, msg)


def setup_logging(level, filename, caller : str):
    symbols = 46 - len(caller) if len(caller) <= 46 else 0
    with open(filename, 'a') as f:
        f.write(f'[{format_now()}]\n{15 * "%"} BEGINNING EXECUTION OF {caller} {(symbols-1) * "%"}\n{85 * "%"}\n\n')

    loglevel = log_dict[level]
    casual_format = f'[%(asctime)s] [%(levelname)8s] {caller}:\n%(message)s\n'
    debug_format  = f'[%(asctime)s] [%(levelname)8s] {caller}: in %(module)s.%(funcName)s on line %(lineno)d:\n%(message)s\n'
    _format = debug_format if loglevel == logging.DEBUG else casual_format
    if filename == '/dev/null':
        logging.basicConfig(
            level = loglevel,
            stream = sys.stderr,
            format=_format, 
            datefmt='%Y-%m-%d %I:%M:%S %p'
        )
    else:
        logging.basicConfig(
            level = loglevel,
            filename = interpret_tilde(filename),
            format=_format, 
            datefmt='%Y-%m-%d %I:%M:%S %p'
        )
    # logging.critical(f'{15 * "%"} BEGINNING EXECUTION OF {caller}{symbols * "%"}\n{85 * "%"}')
    logging.info(f"Logging successfully set up in directory '{interpret_tilde(filename)}'")


def log_final_stack(e : BaseException, logfile='', prefix='', loglevel=logging.CRITICAL, _print=False, email_recip=None, subject=None):
    traceback_str = get_final_stack_trace(e)
    msg = prefix + traceback_str
    logging.log(level=loglevel, msg=msg)
    if _print and logfile != '/dev/null':
        print(traceback_str, file=sys.stderr)
    emailing.send_email_if_desired(email_recip, subject, msg)
    return notify.FAIL


def log_exc_only(e : BaseException, logfile='', prefix='', loglevel=logging.CRITICAL, _print=False, email_recip=None, subject=None):
    traceback_str = get_exception_str(e)
    msg = prefix + traceback_str
    logging.log(level=loglevel, msg=msg)
    if _print and logfile != '/dev/null':
        print(traceback_str, file=sys.stderr)
    emailing.send_email_if_desired(email_recip, subject, msg)
    return notify.FAIL


def get_final_stack_trace(e : BaseException):
    traces = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    indicator = 'Traceback (most recent call last)'
    final_trace = 0
    # Find last line of traceback that contains "Traceback (most recent call last)"
    # This indicates starting position of the final exception message
    for i, trace_line in enumerate(traces):
        if indicator in trace_line:
            final_trace = i
    return ''.join(traces[final_trace:])


def get_exception_str(e : BaseException):
    return ''.join(traceback.format_exception_only(etype=type(e), value=e))
    # return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__) [-1]

