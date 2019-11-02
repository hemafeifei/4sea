
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys

chrome_options = Options()
# chrome_options.add_argument('--headless')
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
        chrome_path = '/home/centos/PythonApp/chromedriver'

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
