from playwright.sync_api import Playwright, sync_playwright, expect, Page, BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from time import sleep
from bs4 import BeautifulSoup
import re
import logging
from strtobool import stringtobool

import _unfi_act as act
import _unfi_nav as nav
import _unfi_reports as reports
import _unfi_orderGuides as orderGuides
from default_parsers import UserInputException
import emailing
from notify import notify_file
from params import LOGLEVEL, LOG
# import file_helpers
import logs
import sys

import os
from dotenv import load_dotenv
# from file_helpers import read_first_line

load_dotenv()
user_main_wellness = os.getenv("UNFI_WELLNESS_USER")
wellness_password = os.getenv("UNFI_WELLNESS_PASS")

user_alberts = os.getenv("UNFI_ALBERTS_USER") 
alberts_password = os.getenv("UNFI_ALBERTS_PASS")

ACCT7 = os.getenv("UNFI_ACCT7")
ACCT3 = os.getenv("UNFI_ACCT3")

HEADLESS = stringtobool(os.getenv("HEADLESS"))

 
alberts_order_guides = ['Organic Produce','Logan Conv Dairy New', 'Logan Fresh']

from EntityDownload import EntityDownload
class UnfiCatalog(EntityDownload):
    def __init__(self, argv, additional_parsers_dict=dict({}), default_values=dict({}) ):
        super().__init__(argv, additional_parsers_dict, default_values)

    
    def email_three_accounts(self):
        with sync_playwright() as playwright:
            self.browser = playwright.chromium.launch(headless=HEADLESS)
            self.page = self.browser.new_page()
            self.email_main_wellness()
            self.email_all_order_guides()
            self.browser.close()


    def email_main_wellness(self):
        nav.login(self.page, user_main_wellness, wellness_password)
        act.click_shopping(self.page)
        act.select_acct_procedure(self.page, ACCT3)
        reports.generate_report_procedure(self.page)
        act.select_acct_procedure(self.page, ACCT7)
        reports.generate_report_procedure(self.page)
        nav.logout(self.page)


    def email_all_order_guides(self):
        nav.login(self.page, user_alberts, alberts_password)
        act.click_shopping(self.page)
        sleep(4)
        self.page.goto("https://www.myunfi.com/download-center")
        # first ensure no files are in download center
        orderGuides.delete_all_files_from_download_center(self.page)
        # add download of each order guide to download center
        for order_guide in alberts_order_guides:
            orderGuides.add_order_guide_to_download_center(self.page, order_guide)
        self.page.goto("https://www.myunfi.com/download-center")
        self.page.get_by_text("Refresh").click(delay=180)
        num_files_found = orderGuides.count_files_in_download_center(self.page)
        num_files_ready = orderGuides.count_success_in_download_center(self.page)
        num_attempts = 4
        # ensure that all files are ready to be emailed
        for attempt in range(num_attempts):
            if num_files_found != num_files_ready:
                if attempt == (num_attempts-1):
                    logs.log_final_stack(
                        e=Exception(f'We detect {num_files_found} order guides but could only verify that {num_files_ready} of them are ready to be emailed. Proceeding anyways.'), 
                        logfile=self.param_dict[LOG], _print=False,
                        prefix='Unexpected exception occurred:\n',
                        loglevel=logging.CRITICAL,
                        email_recip=emailing.BEN
                    )
                sleep(5)
                self.page.get_by_text("Refresh").click(delay=180)
                sleep(3)
                num_files_found = orderGuides.count_files_in_download_center(self.page)
                num_files_ready = orderGuides.count_success_in_download_center(self.page)
            else:
                break
        if num_files_found == num_files_ready:
            logging.info(f'Proceeding to email {num_files_ready} order guide(s)...')
        orderGuides.email_files(self.page)
        orderGuides.delete_all_files_from_download_center(self.page)
        nav.logout(self.page)



def main(argv=sys.argv):
    file = '_unfi-catalog.py'

    # To be used for notifyfile
    SUCCESS = 'success'
    FAIL = 'fail'

    # Initialize UnfiCatalog with argv to process parameters for download and log/notify setup
    try:
        unfi_catalog = UnfiCatalog(
            argv=argv #, 
            # additional_parsers_dict=parsers, 
            # default_values=default_values
        )
        # check that filenames for notify and log are writable
        unfi_catalog.process_files()
    except UserInputException as uie:
        logs.print_stderr(msg=logs.get_exception_str(uie), caller=file)
        return
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=emailing.BEN, subject='Auto msg: unknown exception trying to process files')
        return

    # Instance was successful, and log/notify files are good to go
    # Grab param dict with a shorter name
    p = unfi_catalog.param_dict


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
        unfi_catalog.process_params()
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
        unfi_catalog.email_three_accounts()
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