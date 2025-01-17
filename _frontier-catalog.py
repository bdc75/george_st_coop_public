from playwright.sync_api import Playwright, sync_playwright, expect, Page, BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from time import sleep
from bs4 import BeautifulSoup
import re
import logging
import sys

from default_parsers import UserInputException, parse_comma_list
import emailing
from notify import notify_file
from params import LOGLEVEL, LOG, TYPE, REGULAR, SPECIALS
import file_helpers
import logs

from headless_config import HEADLESS

import _frontier_nav as nav
import _frontier_dl as dl


from EntityDownload import EntityDownload
class FrontierCatalog(EntityDownload):
    def __init__(self, argv, additional_parsers_dict=dict({}), default_values=dict({}) ):
        super().__init__(argv, additional_parsers_dict, default_values)

    def download(self):
        with sync_playwright() as playwright:
            self.browser = playwright.chromium.launch(headless=HEADLESS)
            self.page = self.browser.new_page()
            
            nav.log_in(self.page)
            nav.to_datafeeds(self.page)
            if REGULAR in self.param_dict[TYPE]:
                dl.download_regular(self.page)
                
            if SPECIALS in self.param_dict[TYPE]:
                dl.download_specials(self.page)
                
            nav.log_out(self.page)
            self.browser.close()


def parse_frontier_types(selections : str):
    selections = parse_comma_list(selections)
    options = [REGULAR, SPECIALS]
    for selection in selections:
        if selection not in {REGULAR, SPECIALS}:
            raise UserInputException(f"Option for param <type> must be one of {options}: was given <{selection}>")
    else:
        return selections


def main(argv=sys.argv):
    file = '_frontier-catalog.py'

    # To be used for notifyfile
    SUCCESS = 'success'
    FAIL = 'fail'

    # Initialize FrontierCatalog with argv to process parameters for download and log/notify setup
    try:
        frontier_catalog = FrontierCatalog(
            argv=argv, 
            additional_parsers_dict={TYPE: parse_frontier_types} #, 
            # default_values=default_values
        )
        # check that filenames for notify and log are writable
        frontier_catalog.process_files()
    except UserInputException as uie:
        logs.print_stderr(msg=logs.get_exception_str(uie), caller=file)
        return
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=emailing.BEN, subject='Auto msg: unknown exception trying to process files')
        return

    # Instance was successful, and log/notify files are good to go
    # Grab param dict with a shorter name
    p = frontier_catalog.param_dict


    # if logging setup fails, try to notify file
    try:
        # Set up logging in desired file
        # If default is used, /dev/null, then we log errors to stderr
        logs.setup_logging(level=p[LOGLEVEL], filename=p[LOG], caller=file)
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=emailing.BEN, subject='Error with setting up logging')
        notify_file(p, FAIL)
        return
 

    # PROCESS PARAMETERS
    status = SUCCESS
    try:
        frontier_catalog.process_params()
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
    logging.info(f'params passed:\n{p}')

    # DOWNLOAD ATTEMPT: the real business logic
    try:
        frontier_catalog.download()        
    except PlaywrightTimeoutError as pte:
        status = logs.log_final_stack(
            e=pte, logfile=p[LOG], _print=True,
            prefix='Could not find an element, or loss of synchronicity between program and webpage\n',
            email_recip=emailing.BOTH
        )
    except PlaywrightError as pe:
        status = logs.log_final_stack(
            e=pe, logfile=p[LOG], _print=True,
            prefix='Multiple elements matched or some other error occurred\n',
            email_recip=emailing.BOTH
        )
    except Exception as e:
        status = logs.log_final_stack(
            e=e, logfile=p[LOG], _print=True,
            prefix='Unexpected exception occurred:\n',
            loglevel=logging.CRITICAL,
            email_recip=emailing.BOTH
        )

    # 'success' or 'fail'
    notify_file(p, status)
    

if __name__ == "__main__":
    main()
