from playwright.sync_api import Playwright, sync_playwright, expect, Page, BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright._impl._api_types import TimeoutError as OtherTimeoutError
from time import sleep
from bs4 import BeautifulSoup
import re
import logging


def login(page : Page, username : str, password : str):
    page.goto("https://www.myunfi.com/")
    page.get_by_placeholder("Username").fill(username)
    #   or  <input id="signInName" class="textInput" type="text" placeholder="Username" ...>
    page.get_by_label("Continue").click()
    #   or  page.get_by_role("button", name="Log in to myUNFI").click()
    page.get_by_placeholder("Password").fill(password)
    #   or  <input type="password" id="password" name="Password" placeholder="Password"...>
    page.get_by_role("button", name="Log in to myUNFI").click()
    sleep(10)
    # we need to click somewhere on the page to get out of the popup, if it exists
    page.mouse.click(x=5, y=5, delay=180)


def nav_to_reports(page : Page):
    page.goto('https://www.myunfi.com/shopping/reports')
    sleep(10)


def logout(page):
    page.goto("https://www.myunfi.com/logoff")
    sleep(6)


