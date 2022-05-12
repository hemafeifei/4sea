#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 4sea


import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import sys

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def get_soup(url, timesleep=1.1):
    if sys.platform=='darwin':
        chrome_path = '/Users/wei/opt/chromedriver'

        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        time.sleep(timesleep)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        return soup
    else:
        from pyvirtualdisplay import Display
        chrome_path = '/home/ubuntu/tmp/chromedriver'

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
        chrome_path = '/Users/wei/opt/chromedriver'

        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        driver.find_element(by=By.ID, value=pn_id).send_keys(str(pn))
        driver.find_element(by=By.NAME, value=clk_class).click()
        time.sleep(31)

        driver.quit()

    else:
        from pyvirtualdisplay import Display
        chrome_path = '/home/ubuntu/tmp/chromedriver'

        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        driver.find_element_by_id(pn_id).send_keys(pn)
        driver.find_element_by_class_name(clk_class).click()
        time.sleep(31)

        driver.quit()
        display.stop()


def get_jisilu_validation(url_login, user, pwd, url_parse):
    if sys.platform=='darwin':
        chrome_path = '/Users/wei/opt/chromedriver'

        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url_login)
        driver.find_element(by=By.NAME, value='user_name').send_keys(user)
        driver.find_element(by=By.NAME, value='password').send_keys(pwd)
        driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[2]/div/div[1]/div[1]/div[3]/form/div[5]/div/input').click()
        driver.find_element(by=By.XPATH,
                            value="/html/body/div[3]/div[2]/div/div[1]/div[1]/div[3]/form/div[6]/a").click()
        time.sleep(2)
        driver.get(url_parse)
        time.sleep(1.1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        return soup

    else:
        from pyvirtualdisplay import Display
        chrome_path = '/home/ubuntu/tmp/chromedriver'
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url_login)
        driver.find_element(by=By.NAME, value='user_name').send_keys(user)
        driver.find_element(by=By.NAME, value='password').send_keys(pwd)
        driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[2]/div/div[1]/div[1]/div[3]/form/div[5]/div[2]/input').click()
        driver.find_element(by=By.XPATH, value="/html/body/div[3]/div[2]/div/div[1]/div[1]/div[3]/form/div[6]/a").click()
        time.sleep(2)
        driver.get(url_parse)
        time.sleep(1.1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        display.stop()
        return soup


def get_eastmoney_index(url, tab_xpath, page_xpath=None):
    # scrapy HS300 and SH50 Index
    if sys.platform == 'darwin':
        chrome_path = '/Users/wei/opt/chromedriver'
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        driver.find_element(by=By.XPATH, value=tab_xpath).click()
        time.sleep(1.1)
        if page_xpath is not None:
            driver.find_element(by=By.XPATH, value=page_xpath).click()
            time.sleep(1.3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        return soup
    else:
        from pyvirtualdisplay import Display
        chrome_path = '/home/ubuntu/tmp/chromedriver'
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        driver.get(url)
        driver.find_element(by=By.XPATH, value=tab_xpath).click()
        time.sleep(1.1)
        if page_xpath is not None:
            driver.find_element(by=By.XPATH, value=page_xpath).click()
            time.sleep(1.3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        driver.quit()
        display.stop()
        return soup



