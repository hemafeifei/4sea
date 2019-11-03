from pyvirtualdisplay import Display
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys

chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_path = '/home/centos/PythonApp/chromedriver'


def get_soup(url):
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    driver.quit()
    display.stop()
    return soup

