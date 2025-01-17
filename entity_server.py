from flask import Flask, request
import sys
from time import sleep
import params as p
import logging

import _kehe_catalog
import random

from RequestParser import RequestParser
from default_parsers import UserInputException

app = Flask(__name__)

# file_handlers = dict({})


# def get_handler(filename):
#     """
#     Manage exactly one FileHandler for each file used as a log file
#     """
#     if filename not in file_handlers:
#         fh = logging.FileHandler(filename)
#         casual_format = '[%(levelname)8s] [%(asctime)s] --- %(message)s'
#         # debug_format  = '[%(levelname)8s] [%(asctime)s] in %(module)s.%(funcName)s on line %(lineno)d:\n>  %(message)s\n'
#         # _format = casual_format if loglevel > logging.DEBUG else debug_format
#         formatter = logging.Formatter(casual_format)
#         fh.setFormatter(formatter)
#         file_handlers[filename] = fh
#     return file_handlers[filename]

    
def download(argv, supplier, entity_type):
    if supplier == p.KEHE:
        if entity_type == p.CATALOG:
            return _kehe_catalog.main(argv)
        if entity_type == p.INVOICE:
            pass
    if supplier == p.THRESHOLD:
        if entity_type == p.CATALOG:
            pass
        if entity_type == p.INVOICE:
            pass


# def parse_supplier_and_entity_type(argv):
#     if p.SUPPLIER not in argv:
#         pass
#     if p.ENTITY_TYPE not in argv:
#         pass

#     supplier = argv[p.SUPPLIER]
#     entity_type = argv[p.ENTITY_TYPE]

#     if supplier not in p.OPTS_SUPPLIER:
#         raise 
#     if entity_type not in p.OPTS_ENTITY_TYPE:
#         pass

#     return (supplier, entity_type)



# enforce one log file

#log 
# logging.basicConfig(
#     filename='/Users/bean/datafeeds/logs/log.txt',
#     level=logging.DEBUG
# )

logging.basicConfig(
    filename='/dev/null',
    level=logging.DEBUG
)

#have the parsers do the logging setup??



@app.route('/download_entity', methods=['GET'])
def get_entity():
    argv = request.args.to_dict(flat=True)



    # print(argv)
    
    # supplier, entity_type = parse_supplier_and_entity_type(argv)
    # download(argv, supplier, entity_type)
    return 'success'


def main():
    try:
        request_parser = RequestParser(sys.argv)
    except UserInputException as uie:
        #print it to sys.stderr and also LOG
        pass
    except Exception as e:
        pass
    #  CURRENT challenge is how to implement notifyget/notifyfile for situation server request download
    # AND if a download script is run as __main__

    #setup logging . DEFAULT TO SYS.STDERR?  not .  or just print certain errors
    # like userinputerrors to sys.stderr

    app.run(host='localhost', port=4999)


if __name__ == '__main__':
    # app.run(host: str, port: int)
    main()