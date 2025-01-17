from time import sleep
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from playwright_helpers import *
import logging
from file_helpers import read_first_line

import os
from dotenv import load_dotenv
from strtobool import stringtobool
# from file_helpers import read_first_line

load_dotenv()
username = os.getenv("KEHE_USERNAME")
password = os.getenv("KEHE_PASSWORD")

HEADLESS = stringtobool(os.getenv("HEADLESS"))


def log_in(page):
    login_url = "https://connectretailer.kehe.com/"
    
    page.goto(login_url)
    page.wait_for_load_state(state="load")
    sleep(1)
    page.fill("#username", username)
    page.get_by_role("button", name="Next").click()
    page.fill("#password", password)
    page.get_by_role("button", name="Log In").click()
    page.wait_for_load_state(state="load")
    logging.debug('Successfully logged in')


def navigate_to_retailer_home(page):
    page.goto("https://connectretailer.kehe.com/every-day")
    page.wait_for_load_state(state="load")
    logging.debug("Successfully navigated to home retailer home page")


def click_account_number_dropdown(page):
    page.locator("div.customer-name", has_text="GEORGE").click(delay=300)
    page.wait_for_load_state(state="domcontentloaded")
    # page.wait_for_load_state(state="load")
    logging.debug("Successfully clicked account number dropdown")


def click_pricing_then_wait(page):
    click_element_by_text(
        page, text="Pricing & Publications",
        description="Pricing & Publications"
    )
    sleep(2.5)
    logging.debug("Successfully clicked Pricing & Publications")


def log_out(page):
    click_element_by_css_selector(page, selector=".top-bar-user-name", description="account button top of page")
    click_element_by_text(page, "logout", description="logout option from dropdown")
    logging.debug("Successfully logged out")
