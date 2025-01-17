from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright._impl._api_types import TimeoutError as OtherTimeoutError
from time import sleep
import re
import logging


orderGuides_url = "https://www.myunfi.com/shopping/lists/orderGuides"

def add_order_guide_to_download_center(page : Page, order_guide : str):
    page.goto(orderGuides_url)
    try:
        page.get_by_role("link", name=order_guide).click()
    except:
        logging.error(f"Order guide <{order_guide}> isn't available or couldn't click it")
        return False
    sleep(2)
    page.get_by_text("Export asPrint").click()
    sleep(2)
    page.get_by_role("menuitem", name="Excel (.xlsx)").click()
    sleep(2)
    logging.info(f"Successfully added order guide <{order_guide}> to the list")
    return True


def count_files_in_download_center(page : Page, _print=True):
    re_num_files = re.compile("[0-9]+ file")
    # ensure that it has loaded
    page.locator("p").filter(has_text=re_num_files).click()
    # then wait a moment
    sleep(3)

    num_files_raw = page.locator("p").filter(has_text=re_num_files).text_content()
    num_files_raw = num_files_raw.replace(" files",'')
    files = int(num_files_raw.replace(" file",''))
    return files


def delete_all_files_from_download_center(page : Page):
    num_files = count_files_in_download_center(page)
    if num_files == 0:
        return
    elif num_files == 1:
        page.locator("div").get_by_title("Delete", exact=True).click()
    else:
        page.locator("#select-all-packets-toggle").check()
        sleep(2)
        page.locator("span").filter(has_text="Delete").click()
    page.locator("span.BaseButton-Label").filter(has_text="Delete").click()
    sleep(5)


def count_success_in_download_center(page : Page):
    try:
        page.locator("tspan").filter(has_text=re.compile(r"^SUCCESS$")).first.click()
    except OtherTimeoutError:
        return 0
    successes = len(page.locator("tspan").filter(has_text=re.compile(r"^SUCCESS$")).all())
    return successes


def all_files_ready(page : Page):
    return count_files_in_download_center(page) == count_success_in_download_center(page)


def email_files(page : Page):
    page.locator("#select-all-packets-toggle").check()
    sleep(2)
    page.get_by_role("button", name="Email").click()
    sleep(2)
    page.get_by_text(re.compile(r"^Send Files$")).click()
    sleep(6)