import _threshold_nav as nav
from _threshold_dl import download_file, DownloadException
from _threshold_parsers import parse_threshold_period, parse_threshold_types

from date_range_helpers import YearMonth
import logs
from params import PERIOD, TYPE, REGULAR, SPECIALS, LOGLEVEL, LOG
from notify import notify_file, notify_get, SUCCESS, FAIL
from file_helpers import read_first_line
from default_parsers import UserInputException
from emailing import JOHN, BEN, BOTH

import sys
import logging
import requests

from EntityDownload import EntityDownload

class ThresholdCatalog(EntityDownload):
    def __init__(self, argv, additional_parsers_dict=dict({}), default_values=dict({}) ):
        super().__init__(argv, additional_parsers_dict, default_values)
        self.signin_payload = {
            "data[accounts][email]" : read_first_line('email-ordering'),
            "data[accounts][password]" : read_first_line("password-threshold")
        }
        self.signed_in = False

    def download(self):
        """
        * Downloads regular pricelist catalog if "regular" is in param <type>
        * If "specials" is in param <type>, we download specials catalogs for the desired months in "period" parameter
        
        Returns "success" if downloads ensue with no exceptions thrown, and if
        all specials catalogs for the desired months were available

        Otherwise returns "fail"
        """
        self.session = requests.session()
        nav.signin(self.session, self.signin_payload)
        self.signed_in = True
        
        params = self.param_dict
        status = SUCCESS
        # TODO: regular must detect failure from within these functions
        if REGULAR in params[TYPE]:
            download_url = nav.get_regular_download_link(self.session)
            if not download_url:
                status = FAIL
                raise nav.NavigationException("Could not find download_url for regular pricelist")
            r = download_file(self.session, download_url, None, REGULAR)

        if SPECIALS in params[TYPE]:
            for yearmonth in params[PERIOD]:
                download_url = nav.nav_to_a_months_DL_page(self.session, yearmonth)
                # If there are specials available for the given month, download it
                if download_url:
                    download_file(self.session, download_url, yearmonth, SPECIALS)
                else:
                    logging.critical(f"Could not download {yearmonth.month_name.capitalize()} specials, not found on threshold")
                    status = FAIL

        return status


def main(argv=sys.argv):
    # Define default values and application-specific param parsers
    default_values = {PERIOD : [YearMonth.get_current_yearmonth()]} #specials catalog of current month
    parsers = {
        PERIOD:parse_threshold_period, TYPE:parse_threshold_types
    }

    # CREATE EntityDownload object.  Check that logfile and notifyfile can be accessed
    file = "_threshold-catalog.py"
    try:
        thr_catalog = ThresholdCatalog(
            argv=argv, 
            additional_parsers_dict=parsers, 
            default_values=default_values
        )
        thr_catalog.process_files()
    except UserInputException as uie:
        logs.print_stderr(msg=logs.get_exception_str(uie), caller=file, email_recip=JOHN, subject='Auto msg: param or file error')
        return
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=BEN, subject='Auto msg: unknown exception trying to process files')
        return


    params = thr_catalog.param_dict


    # SETUP LOGGING
    # if logging setup fails, try to notify file
    try:
        # Set up logging in desired file
        # If default is used, /dev/null, then we log errors to stderr
        logs.setup_logging(level=params[LOGLEVEL], filename=params[LOG], caller=file)
    except Exception as e:
        logs.print_stderr(msg=logs.get_final_stack_trace(e), caller=file, email_recip=BOTH, subject='Error with setting up logging')
        notify_file(params, FAIL)
        return


    # PROCESS PARAMETERS
    status = SUCCESS
    try:
        thr_catalog.process_params()
    except UserInputException as uie:
        status = logs.log_exc_only(e=uie, logfile=params[LOG], _print=True, email_recip=JOHN)
        # status = logs.log_exc_only(e=uie, logfile=params[LOG], _print=True, email_recip=BEN)
        # print(usage, file=sys.stderr)
    except Exception as e:
        status = logs.log_final_stack(e=e, logfile=params[LOG], prefix='UNEXPECTED EXCEPTION:\n', _print=True, email_recip=BEN)


    # NOTIFYFILE if exception occurs
    if status == FAIL:
        notify_file(params, FAIL)
        return


    #######    NORMAL PROGRAM FLOW    #######
    # Everything is working if we get to this point in the code
    logging.info('params processed, beginning download now')
    status = SUCCESS
    logging.info(f'params passed:\n{params}')
    
    # DOWNLOAD ATTEMPT: the real business logic
    try:
        status = thr_catalog.download()
    except DownloadException as de:
        status = logs.log_final_stack(
            e=de, logfile=params[LOG], _print=True,
            email_recip=BOTH
        )
    except nav.NavigationException as ne:
        status = logs.log_final_stack(
            e=ne, logfile=params[LOG], _print=True,
            email_recip=BOTH
        )
    except nav.WrongPasswordException as wpe:
        status = logs.log_final_stack(
            e=wpe, logfile=params[LOG], _print=True,
            email_recip=BOTH
        )
    except Exception as e:
        status = logs.log_final_stack(
            e=e, logfile=params[LOG], _print=True,
            prefix='Unexpected exception occurred:\n',
            email_recip=BOTH
        )
    finally:
        if thr_catalog.signed_in:
            nav.signout(thr_catalog.session)
        thr_catalog.session.close()

    # notify 'success' or 'fail'
    notify_file(params, status)
    


if __name__ == '__main__':
    main()


    