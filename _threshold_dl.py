import logging
import file_helpers as fh
import re
from _threshold_nav import navigate
from date_range_helpers import YearMonth
from datetime import date
from requests import Response
from params import REGULAR, SPECIALS

dl_directory = fh.tilde + '/datafeeds/products/threshold/catalog/'


class DownloadException(Exception):
    def __init__(self, message):
        super().__init__(message)


def parse_filename_from_header(response: Response, header : str):
    if header not in response.headers.keys():
        return None
    search_result = re.search(r'filename="(.+?)"', response.headers[header])
    return None if search_result == None else search_result.group(1)


def parse_downloaded_filename_from_response(response):
    filename_cont_type = parse_filename_from_header(response, "Content-Type")
    filename_cont_disp = parse_filename_from_header(response, "Content-Disposition")
    if not any([filename_cont_disp, filename_cont_type]):
        return None
    else:
        return filename_cont_disp if filename_cont_disp != None else filename_cont_type


###########
def download_file(session, download_url, yearmonth : YearMonth, _type):
    response = navigate(session, download_url)
    dled_filename = parse_downloaded_filename_from_response(response)
    ext = fh.get_file_extension(dled_filename) 
    filename = dled_filename
    filename_wo_ext = fh.get_filename_wo_ext(dled_filename)

    # REGULAR
    custom_name_wo_ext = f'{str(date.today())}_{filename_wo_ext}'
    exc_string = f"regular pricelist filename of download could not be found: {response.headers}"
    
    # SPECIALS
    if _type == SPECIALS:
        custom_name_wo_ext = f'{str(date.today())}_{yearmonth.month_name.capitalize()}_Specials'
        exc_string = f"<{yearmonth.month_name.capitalize()}> specials filename of download could not be found: {response.headers}"
    
    if not dled_filename:
        raise DownloadException(exc_string)
    
    if ext != ".zip":
        filename = f'{custom_name_wo_ext}{ext}'
    
    filepath = dl_directory + filename
    with open(filepath, "wb") as f:
        f.write(response.content)

    # LOG original name of downloaded file, and new name.
    logging.critical(f"File downloaded as <{dled_filename}> was saved as {filepath}")

    if ext == ".zip":
        mtimes = fh.unzip_file(dl_directory, filepath, custom_name_wo_ext)
        fh.revert_og_mtimes(mtimes)

    return response
###########

# {'Cache-Control': 'private', 
#  'Content-Type': 'application/zip', ....
# ...
#  'Content-Description': 'File Transfer', 
#  'Content-Disposition': 'inline; filename="threshold_price_catalog.zip";', 
#  'Content-Transfer-Encoding': 'binary',
# ...}