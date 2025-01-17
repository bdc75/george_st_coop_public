import logging
from requests import Session, Response
from bs4 import BeautifulSoup
from date_range_helpers import YearMonth

host = "https://www.thresholdenterprises.com"
pricingURL = host + "/pricing"
signinURL = host + "/accounts/signin"
signoutURL = host + "/accounts/signout"


class NavigationException(Exception):
    def __init__(self, message):
        super().__init__(message)

class WrongPasswordException(Exception):
    def __init__(self, message):
        super().__init__(message)


def signin_invalid(response : Response):
    pricing = scrape_url_from_page(response.text, "Threshold Pricing")
    download_ctr = scrape_url_from_page(response.text, "Download Center")
    thr_catalog = scrape_url_from_page(response.text, "Threshold Catalog")
    invalid_msg = "Please enter a valid email and password"
    return (not any([pricing,download_ctr,thr_catalog])) or invalid_msg in response.text
        

# TODO  make use of r.ok and r.reason with logging / exception handling
def signin(session : Session, credentials : dict):
    r = session.post(signinURL, data = credentials)
    if not r.ok:
        raise NavigationException(f'Sign-in failed: {r.reason}')
    elif signin_invalid(r):
        raise WrongPasswordException(f'Wrong pwd suspected: is file "password-threshold" up to date?')


def signout(session : Session):
    return navigate(session, signoutURL)


def nav_to_pricing(session : Session):
    return navigate(session, pricingURL)


def navigate(session : Session, url):
    r = session.get(url)
    if not r.ok:
        raise NavigationException(f"get request to <{url}> failed")
    else:
        return r


def get_page_content_from_request(session : Session, url):
    return navigate(session, url).text


def get_regular_download_link(session : Session):
    return scrape_url_from_keyword(session, pricingURL, keyword="Download the pricelist")


def nav_to_a_months_DL_page(session : Session, yearmonth : YearMonth):
    """
    :param session: current requests session
    :param yearmonth: object that contains desired month of specials

    Locates link whose text matches the month and the keyword "excel",
    then navigates to it and returns the download URL
    
    :return: download URL of desired monthly specials file
    """
    r = nav_to_pricing(session)
    specials_url = scrape_url_from_keyword(session, url=pricingURL, keyword="View the current monthly specials")
    r = navigate(session, specials_url)
    url, string = scrape_url_from_multiple_keywords(r.text, [yearmonth.month_name[:3], "excel"])
    if url == None:
        return None
        # TODO: log a critical that we did not found this month's link
        # TODO: notify failure
    else:
        return scrape_url_from_keyword(session, url, "Download File")

#TODO scrape_url_from_page exception handling / exceptions thrown

def scrape_url_from_keyword(session : Session, url, keyword, fail_msg = " "):
    page_to_scrape = get_page_content_from_request(session, url)
    return scrape_url_from_page(page_to_scrape, keyword)


def scrape_urls_from_keyword(session, current_url, keyword, fail_msg = " "):
    page_to_scrape = get_page_content_from_request(session, current_url)
    urls, strings = scrape_urls_from_page(page_to_scrape, keyword)
    return (urls, strings)


# Return href URL in "a" anchor element whose text contains the given keyword, case-insensitive
def scrape_url_from_page(html_page, keyword):
    if not html_page:
        raise NavigationException("given HTML page that is empty or None")
    soup = BeautifulSoup(html_page, features="html.parser")
    keyword = keyword.lower()
    #     Iterate through all "a" tags in the page (the hyperlink anchors)
    for tag in soup.find_all("a"):
        if tag.string is not None and tag.string.lower().find(keyword) >= 0:
            return host + tag["href"]
    return None


# Return href URL in "a" anchor element whose text contains the given keyword, case-insensitive
def scrape_url_from_multiple_keywords(html_page, keywords):
    if html_page == None:
        pass # raise Exception
    soup = BeautifulSoup(html_page, features="html.parser")
    keywords = list(map(lambda s: s.lower(), keywords))
    #     Iterate through all "a" tags in the page (the hyperlink anchors)
    for tag in soup.find_all("a"):
        if tag.string is not None:
            matches = list(map(lambda k: tag.string.lower().find(k) >= 0, keywords))
            if all(matches):
                return (host + tag["href"], tag.string)
    return (None, None)


# Return href URL in "a" anchor element whose text contains the given keyword, case-insensitive
# Returns tuple: (urls, strings)  where "strings" is the list of corresponding URL headlines which contain the keyword
def scrape_urls_from_page(html_page, keyword):
    soup = BeautifulSoup(html_page, features="html.parser")
    matches = []
    keyword = keyword.lower()
    #     Iterate through all "a" tags in the page (the hyperlink anchors)
    for tag in soup.find_all("a"):
        if tag.string is not None and tag.string.lower().find(keyword) >= 0:
            matches.append((host + tag["href"], tag.string))
    return matches

