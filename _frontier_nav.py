from time import sleep
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from playwright_helpers import *
import logging
import os
from dotenv import load_dotenv
# from file_helpers import read_first_line

load_dotenv()
username = os.getenv("FRONTIER_USERNAME")
password = os.getenv("FRONTIER_PASSWORD")


def log_in(page):
    page.goto("https://wholesale.frontiercoop.com/")
    page.get_by_role("link", name="Sign In/Create Account").click()
    page.get_by_role("textbox", name="Email*").fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign In").click()
    logging.debug('Successfully logged in')


def to_datafeeds(page):
    page.goto("https://wholesale.frontiercoop.com/data-feeds/")


def log_out(page):
    page.goto("https://wholesale.frontiercoop.com/customer/account/logout")
    sleep(5)
