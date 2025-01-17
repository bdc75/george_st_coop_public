from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from time import sleep
from playwright_helpers import click_element_by_text, click_element_by_css_selector
import _kehe_nav as nav
import os
from datetime import date, datetime
import logging

class DateTypeException(Exception):
    def __init__(self, message):
        super().__init__(message)

def download_dc(page, acct, _format):
    nav.navigate_to_retailer_home(page)
    select_acct_number(page, acct)
    # nav.click_pricing_then_wait(page)
    # dc = 'DC Wholesale Pricing Catalog'
    # nav.click_element_by_text(page, dc, dc)
    ####
    click_catalog_type_procedure(page, 'dc')
    ####
    prepare_dc_download_settings(page, _format)
    filename = create_dc_filename(acct, _format)
    request_download(page, filename)
    return filename


# $filename = "{$catalog_type}_{$acct_num}_{$price_date_iso}_{$order_quant}.{$ext}";
# change to: "<price_date_iso>_<catalog_type>_<acct_num>_<order_quant>.<ext>"
def create_dc_filename(acct, _format):
    catalog_type = 'DC-Wholesale-Pricing'
    _date = str(date.today())
    return _date + '_' + catalog_type + '_' + acct + '_' + _format


def download_customer_file(page, acct, date, item_group, _format):
    nav.navigate_to_retailer_home(page)
    select_acct_number(page, acct)
    # nav.click_pricing_then_wait(page)
    # customer = 'Customer Specific Pricing Catalog'
    # nav.click_element_by_text(page, customer, customer)
    ####
    click_catalog_type_procedure(page, 'customer')
    ####
    prepare_customer_download_settings(page, date, item_group, _format)
    filename = create_customer_filename(acct, date, item_group, _format)
    request_download(page, filename)
    return filename


def click_catalog_type_procedure(page, catalog_type):
    catalog_type_str = 'Customer Specific Pricing Catalog' if catalog_type == 'customer' else 'DC Wholesale Pricing Catalog'
    success = False
    attempts = 0
    while not success and attempts < 5:
        try:
            nav.click_pricing_then_wait(page)
            click_catalog_type(page, catalog_type_str)
            success = True
            logging.debug(f'Successfully clicked catalog type {catalog_type} on attempt #{attempts+1}')
        except PlaywrightTimeoutError as pte:
            success = False
        attempts += 1


def click_catalog_type(page, catalog_type_str):
    page.get_by_text(catalog_type_str).click(delay=180, timeout=2000)


# follows convention:
# $filename = "{$catalog_type}_{$acct_num}_{$price_date_iso}_{$order_quant}_{$item_group}.{$ext}";
# change to <price_date_iso>_<catalog_type>_<acct_num>_<order_quant>_<item_group>.<ext>
def create_customer_filename(acct, _date, item_group, _format):
    catalog_type = 'Customer-Specific-Pricing'
    return str(_date) + '_' + catalog_type + '_' + acct + '_' + item_group + _format


def prepare_dc_download_settings(page, _format):
    if _format != '.xls':
        click_element_by_text(page, ".xls", description="file format dropdown menu")
        click_element_by_text(page, _format, description=f"file format option '{_format}'")
    logging.debug("Successfully prepared DC download settings")

def prepare_customer_download_settings(page, date, item_group, _format):
    select_item_group_from_dropdown(page, item_group)
    type_date(page, date)
    if _format != '.xls':
        click_element_by_text(page, ".xls", description="file format dropdown menu")
        click_element_by_text(page, _format, description=f"file format option '{_format}'")
    logging.debug("Successfully prepared 'customer pricing' download settings")


def type_date(page, raw_date):
    # Old selector, replaced 2023-10-27
    # selector = "span.k-dateinput-wrap > input.k-input"
    selector = "kendo-datepicker"
    typeable_date = make_date_typeable(raw_date)
    datepicker = page.locator(selector)
    datepicker.click()
    sleep(1)

    # for _ in range(2):
    #     datepicker.press("ArrowRight")
    # for _ in range(2):   # Press left arrow key 24 times (lowest multiple of 8 and 3)
    #     datepicker.press("ArrowLeft")

    for _ in range(24):   # Press left arrow key 24 times (lowest multiple of 8 and 3)
        datepicker.press("ArrowLeft")
    datepicker.type(typeable_date)

    # Assert that the date we typed matches the desired date
    raw_typed_date = page.locator("kendo-dateinput>input").input_value()
    format_s = '%m/%d/%Y'
    typed_date = datetime.strptime(raw_typed_date, format_s).date()
    if typed_date != raw_date:
        raise DateTypeException(f'Change in KeHE datepicker: Typed date <{typed_date}> does not match desired date <{raw_date}>, the program typed <{raw_typed_date}> verbatim')
    
    page.wait_for_load_state(state="load")
    logging.debug(f"Date {raw_date} entered successfully")



def click_account_number_dropdown(page):
    page.locator("div.customer-name", has_text="GEORGE").click(delay=100)
    page.wait_for_load_state(state="load")
    sleep(1.5)


def select_acct_number(page, acct_number):
    acct_default = page.locator('.customer-number')
    # already selected
    if acct_number in acct_default.inner_text():
        page.wait_for_load_state(state="load")
        sleep(0.5)
        return
    click_account_number_dropdown(page)
    click_element_by_text(page, acct_number, description="Account number")
    sleep(6.5)

def request_download(page, filename):
    # Disable timeout with argument timeout=0 (we want to wait indefinitely for download)
    # Set timeout to 5 minutes
    five_minutes = 300000 # msec
    with page.expect_download(timeout=five_minutes) as download_info:
        click_download_button(page)
    download = download_info.value
    tilde = os.environ['HOME']
    filepath = tilde + '/datafeeds/products/kehe/catalog/' + filename
    download.save_as(filepath)
    logging.critical(f'Successful download: {filepath}')


def click_download_button(page):
    page.get_by_role("button", name="Download").click(delay=100)


def select_item_group_from_dropdown(page, item_group):
    click_item_group_dropdown(page)
    click_item_group_option(page, item_group)


def click_item_group_dropdown(page):
    page.locator("#export-price-customer").get_by_text("Authorized List").click(delay=100)
    page.wait_for_load_state(state="load")


def click_item_group_option(page, item_group):
    page.get_by_role("option", name=item_group).click(delay=100)
    page.wait_for_load_state(state="load")


def make_date_typeable(date):
    day   = '0' + str(date.day)   if date.day < 10   else str(date.day)
    month = '0' + str(date.month) if date.month < 10 else str(date.month)
    return f'{month}{day}{date.year}'