from playwright.sync_api import Page
import _unfi_nav as nav
import _unfi_reports as reports
import _unfi_act as act

def verify_correct_report_defaults(page : Page):
    field_separator = page.get_by_role("button", name="Tab delimited").count() == 1
    please_select = page.get_by_role("button", name="All Product").count() == 1
    product_type = page.get_by_role("button", name="Both Full and Split-case items").count() == 1
    sorting_option = page.get_by_role("button", name="Un-sorted").count() == 1
    report_format = page.get_by_role("button", name="Text (txt)").count() == 1
    if not all([field_separator,please_select,product_type,sorting_option,report_format]):
        raise Exception("One of the report defaults could not be found or multiple elements matched")


def generate_report_procedure(page):
    nav.nav_to_reports(page)
    try:
        page.get_by_role("button", name="Dismiss", exact=True).click()
    except:
        pass
    act.click_generate_report(page)
    reports.verify_correct_report_defaults(page)
    act.complete_the_report(page)