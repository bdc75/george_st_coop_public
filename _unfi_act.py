from playwright.sync_api import Playwright, sync_playwright, expect, Page, BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright._impl._api_types import TimeoutError as OtherTimeoutError
from time import sleep
from bs4 import BeautifulSoup
import re
import logging
import sys
import logs

ACCT7 = "75887"
ACCT3 = "3229"

def click_shopping(page: Page):
    # page.get_by_role("link").get_by_text("Shopping").first.click()
    page.goto("https://www.myunfi.com/shopping")


def selector_for_generate_report(content : str) -> str:
    soup = BeautifulSoup(content, features="html.parser")
    essentials = soup.find(string=re.compile("essentials", re.IGNORECASE))
    gen_rep_outer = essentials.parent.parent.parent.next_sibling
    gen_rep = gen_rep_outer.find(string="Generate Report")
    gen_rep_tag = gen_rep.parent
    defining_classes = gen_rep_tag.attrs['class']
    selector = ''
    for _class in defining_classes:
        selector += f'.{_class}'
    return selector


def click_generate_report(page):
    selector = selector_for_generate_report(page.content())
    page.locator(selector).click(delay=180)
    sleep(2)


def complete_the_report(page):
    page.get_by_label("Field choice").click()
    sleep(2)
    page.locator("label").filter(has_text=re.compile(r"^Select All$")).click()
    sleep(2)
    page.get_by_role("button", name="Apply").click()
    sleep(2)
    page.get_by_text("Email").click()
    sleep(3)
    page.keyboard.press("Escape")
    sleep(5)


def click_acct_dropdown(page):
    page.get_by_role("button", name="John Leary").click(delay=180)
    sleep(2)


# def select_acct_procedure(page : Page, context : BrowserContext, desired_acct : str):
def select_acct_procedure(page : Page, desired_acct : str):
    # Force it to default set of options in the dropdown
    # Ensures that "See All Accounts" button is clickable
    # Also ensures that the account dropdown is visible before doing beautifulsoup
    click_acct_dropdown(page)
    # exit dropdown
    page.keyboard.press("Escape")
    sleep(2)

    soup = BeautifulSoup(page.content(), features="html.parser")
    
    acct_dropdown_str = soup.find(string='John Leary')
    acct_dropdown_tag = acct_dropdown_str.parent
    current_acct_tag = acct_dropdown_tag.next_sibling

    if (current_acct_tag != None) and (not (ACCT3 in current_acct_tag.string or ACCT7 in current_acct_tag.string)):
        raise Exception("Could not figure out which account we are on (main or wellness)")

    if desired_acct in current_acct_tag.string:
        return
    
    # Change account
    click_acct_dropdown(page)
    page.get_by_role("button", name="See all Accounts").click(delay=180)
    sleep(2)
    page.get_by_text(desired_acct).click(delay=180)

    sleep(10)