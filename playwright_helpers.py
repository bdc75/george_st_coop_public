from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError


def click_element_by_text(page, text, description):
    # error_prefix = f'Could not find and click {description}'
    try:
        page.wait_for_load_state(state="load")
        page.get_by_text(text).click(delay=180, timeout=10000)
        page.wait_for_load_state(state="load")
    except PlaywrightTimeoutError as pte:
        raise Exception(f'Could not find and click element with description <{description}> using text "{text}"')
    except PlaywrightError as pe:
        raise Exception(f'Multiple "{text}" elements found or some other playwright error occurred')
    except Exception as e:
        raise Exception(f'Unexpected error occurred:\n{e}')


def click_element_by_css_selector(page, selector, description):
    # error_prefix = f'Error on KeHE click_element_by_css_selector() trying to find and click "{description}": '
    try:
        page.wait_for_load_state(state="load")
        page.locator(selector).click(delay=180, timeout=10000)
        page.wait_for_load_state(state="load")
    except PlaywrightTimeoutError as pte:
        raise Exception(f'Could not find and click element with description <{description}> using selector "{selector}"')
    except PlaywrightError as pe:
        raise Exception(f'Multiple "{selector}" elements found or some other playwright error occurred')
    except Exception as e:
        raise Exception(f'Unexpected error occurred:\n{e}')