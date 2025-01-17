import os
import logging
from datetime import date
from time import sleep

def click_regular(page):
   page.get_by_role("link", name="WholeSale Catalog (Excel)").click()

def click_specials(page):
   page.get_by_role("link", name="MonThly Specials (Excel)").click()

def download_regular(page):
  with page.expect_download() as download_info:
      click_regular(page)
  download = download_info.value
  tilde = os.environ['HOME']
  filename = "Wholesale_Catalog.xlsx"
  _date = str(date.today()) 
  filepath = f'{tilde}/datafeeds/products/frontier/catalog/{_date}_{filename}'
  download.save_as(filepath)
  sleep(10)
  logging.critical(f'Successful download: {filepath}')

def download_specials(page):
  with page.expect_download() as download_info:
      click_specials(page)
  download = download_info.value
  tilde = os.environ['HOME']
  filename = "Monthly_Specials.xlsx"
  _date = str(date.today()) 
  filepath = f'{tilde}/datafeeds/products/frontier/catalog/{_date}_{filename}'
  download.save_as(filepath)
  sleep(10)
  logging.critical(f'Successful download: {filepath}')
    