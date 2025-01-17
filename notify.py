import requests
from file_helpers import interpret_tilde
from params import NOTIFYFILE
import logs
from params import LOG
import emailing
import logging

SUCCESS = 'success'
FAIL = 'fail'

def notify_get(url : str, status : str):
    # if url[5:] != 'http:':
    #     url = 'http://' + url
    # it doesn't work like this
    requests.get(url, params={'status':status})


def notify_file(p : dict, status : str):
    logging.critical(f"Program exited with status <{status}>")
    if NOTIFYFILE not in p:
        return
    try:
        filename = p[NOTIFYFILE]
        with open(interpret_tilde(filename), 'w') as f:
            f.write(status)
        logging.info(f"File was notified of status <{status}>")
    except Exception as e:
        logs.log_final_stack(e=e, logfile=p[LOG], prefix='Notifyfile exception:\n', _print=True, email_recip=emailing.BEN, subject='Error with notifyfile')