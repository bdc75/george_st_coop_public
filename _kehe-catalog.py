import _kehe_nav as nav
import _kehe_settings as settings
import _kehe_parsers as kehe_parse

import logs
from date_range_helpers import form_days_range_from_period, form_date_range_in_days
from default_parsers import UserInputException
from params import *
from notify import notify_file, notify_get
from emailing import JOHN, BEN, BOTH
from strtobool import stringtobool

import sys
import logging
from playwright.sync_api import sync_playwright
from time import sleep

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

# page.content  attribute!!

from headless_config import HEADLESS

from EntityDownload import EntityDownload

class KeheCatalog(EntityDownload):
    def __init__(self, argv, additional_parsers_dict=dict({}), default_values=dict({}) ):
        super().__init__(argv, additional_parsers_dict, default_values)

    def download(self):
        with sync_playwright() as playwright:
            self.browser = playwright.chromium.launch(headless=HEADLESS)
            self.page = self.browser.new_page()
            nav.log_in(self.page)
            self.download_requested_files()
            nav.log_out(self.page)
            self.browser.close()
    
    def download_requested_files(self):
        p = self.param_dict
        
        if p[CATALOG_TYPE] == 'DC Wholesale Pricing Catalog':
            logging.info('Downloading DC file(s)')
            for _format in p[FORMAT]:  
                settings.download_dc(
                    self.page,
                    p[ACCT],
                    _format
                )
            return
        
        # Otherwise, catalog_type must be Customer Specific Pricing
        # If provided, download the dates provided in the <period> parameter
        if PERIOD in p:
            _range = form_days_range_from_period(p[PERIOD])
        else:   # Otherwise refer to start and end parameters
            _range = form_date_range_in_days(p[START], p[END])
        for _date in _range:
            for _format in p[FORMAT]:    
                settings.download_customer_file(
                    self.page,
                    p[ACCT],
                    _date,
                    p[ITEM_GROUP],
                    _format
                )
# End of :class:KeheCatalog

usage = '''Parameters (in alphabetical order):
acct         ::  {172011, 049698}    
  * Defaults to "172011"

catalog_type ::  {dc, customer}    (customer indicates Customer Specific Pricing)
  * Always defaults to "customer"

format       ::  comma-separated list from {.txt, .csv, .xls} (note the period "." before each)    
  * Defaults to ".txt"

item_group   ::  {master, authorized, current, history}
  * Defaults to "master" when acct=172011, and  "authorized" when acct=049698

log          ::  file directory, ~ (tilde) IS allowed e.g. ~/my.log
  * Defaults to "/dev/null"

loglevel     ::  digits 0 through 7 or one of {emerg, alert, crit, err, warning, notice, info, debug}
  * Defaults to "warning" (i.e. level 4)

notifyfile   ::  file directory, ~ (tilde) IS allowed e.g. ~/notify.txt
  * No default
'''

def main(argv=sys.argv):
    # Define default values and application-specific param parsers
    default_values = {ACCT:'172011', FORMAT:['.txt'], CATALOG_TYPE:'Customer Specific Pricing Catalog'}
    parsers = {
        ITEM_GROUP:kehe_parse.parse_item_group, ACCT:kehe_parse.parse_kehe_acct, FORMAT:kehe_parse.parse_kehe_format, 
        CATALOG_TYPE:kehe_parse.parse_catalog_type
    }

    file = '_kehe-catalog.py'

    # To be used for notifyfile
    SUCCESS = 'success'
    FAIL = 'fail'

    # Initialize KeheCatalog with argv to process parameters for download and log/notify setup
    try:
        kehe_catalog = KeheCatalog(
            argv=argv, 
            additional_parsers_dict=parsers, 
            default_values=default_values
        )
        # check that filenames for notify and log are writable
        kehe_catalog.process_files()
    except UserInputException as uie:
        logs.print_stderr(msg=logs.get_exception_str(uie), caller=file)
        return
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=BEN, subject='Auto msg: unknown exception trying to process files')
        return

    # Instance was successful, and log/notify files are good to go
    # Grab param dict with a shorter name
    p = kehe_catalog.param_dict


    # if logging setup fails, try to notify file
    try:
        # Set up logging in desired file
        # If default is used, /dev/null, then we log errors to stderr
        logs.setup_logging(level=p[LOGLEVEL], filename=p[LOG], caller=file)
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=BEN, subject='Error with setting up logging')
        notify_file(p, FAIL)
        return
 

    # PROCESS PARAMETERS
    status = SUCCESS
    try:
        kehe_catalog.process_params()
    except UserInputException as uie:
        status = logs.log_exc_only(e=uie, logfile=p[LOG], _print=True)
        # print(usage, file=sys.stderr)
    except Exception as e:
        status = logs.log_final_stack(e=e, logfile=p[LOG], prefix='UNEXPECTED EXCEPTION:\n', _print=True)


    # NOTIFYFILE if exception occurs
    if status == FAIL:
        notify_file(p, FAIL)
        return
    
    
    #######    NORMAL PROGRAM FLOW    #######
    # Everything is working if we get to this point in the code
    logging.info('params processed, beginning download shortly')
    status = SUCCESS
    
    is_main  =  (p[ACCT] == '172011')
    if ITEM_GROUP not in p:
        p[ITEM_GROUP] = 'Item Master' if is_main else 'Authorized List'

    logging.info(f'params passed:\n{p}')

    # print(p)


    # DOWNLOAD ATTEMPT: the real business logic
    try:
        kehe_catalog.download()
    except PlaywrightTimeoutError as pte:
        status = logs.log_final_stack(
            e=pte, logfile=p[LOG], _print=True,
            prefix='Wrong password? Otherwise, probably could not find an element, or loss of synchronicity between program and webpage\n',
            email_recip=BOTH
        )
    except settings.DateTypeException as dte:
        status = logs.log_final_stack(
            e=dte, logfile=p[LOG], _print=True,
            email_recip=BOTH
        )
    except PlaywrightError as pe:
        status = logs.log_final_stack(
            e=pe, logfile=p[LOG], _print=True,
            prefix='Multiple elements matched or some other error occurred\n',
            email_recip=BOTH
        )
    except Exception as e:
        status = logs.log_final_stack(
            e=e, logfile=p[LOG], _print=True,
            prefix='Unexpected exception occurred:\n',
            loglevel=logging.CRITICAL,
            email_recip=BOTH
        )

    # 'success' or 'fail'
    notify_file(p, status)
    

if __name__ == "__main__":
    main()
