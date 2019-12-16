
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def get_soup(url, timesleep=1.1):
    if sys.platform=='darwin':
        chrome_path = '/Users/wei/PycharmProjects/tickets/chromedriver'

        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        time.sleep(timesleep)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        return soup
    else:
        from pyvirtualdisplay import Display
        chrome_path = '../../chromedriver'

        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        time.sleep(timesleep)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        display.stop()
        return soup


def get_pn_validation(url, pn_id, pn, clk_class):
    if sys.platform=='darwin':
        chrome_path = '/Users/wei/PycharmProjects/tickets/chromedriver'

        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        driver.find_element_by_id(pn_id).send_keys(str(pn))
        driver.find_element_by_class_name(clk_class).click()
        time.sleep(30)

        driver.quit()

    else:
        from pyvirtualdisplay import Display
        chrome_path = '../../chromedriver'

        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        driver.find_element_by_id(pn_id).send_keys(pn)
        driver.find_element_by_class_name(clk_class).click()
        time.sleep(30)

        driver.quit()
        display.stop()

