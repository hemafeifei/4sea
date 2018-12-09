import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
import re
import os
from pyvirtualdisplay import Display

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_path = '/home/centos/football/chromedriver'

df_name = pd.read_csv('league_name.txt', encoding='utf8')
base_url = 'http://score.nowscore.com/index.aspx'
base_url_007 = 'http://www.win0168.com/'
base_url_en = 'http://www.nowgoal.com/'
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=10))

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


def get_match(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'class': ['ts1', 'ts2']}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(str.lstrip(mlist[4]))
        match.append(mlist[5])
        match.append(str.lstrip(mlist[6]))
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    # tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype','tm_utc08', 'home', 'result', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(today)[:10] if df['tm_utc08'][i] <= '06:00' else today_utc0[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date'] + ' ' + df['tm_utc08']
    df = df[['mtype', 'dt_utc08', 'home', 'result', 'away', 'href_nsc']]
    if lty==True:
        df = df.loc[df.mtype.isin(df_name['league_nsc'])].reset_index(drop=True)
    else:
        df = df
    return df

def get_match_007(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'id': (lambda value: value and value.startswith("tr1_"))}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(mlist[3])
        match.append(mlist[4])
        match.append(mlist[5])
        match.append(mlist[6])
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    # tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype','tm_utc08', 'status', 'home', 'result', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(today)[:10] if df['tm_utc08'][i] <= '06:00' else today_utc0[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date']  + ' ' + df['tm_utc08']
    df = df.loc[df.status=='完']
    df = df[['mtype', 'dt_utc08', 'home', 'result', 'away', 'href_nsc']]
    if lty==True:
        df = df.loc[df.mtype.isin(df_name['league_007'])].reset_index(drop=True)
    else:
        df = df
    return df


def get_match_en(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'class': ['', 'b2']}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(mlist[3])
        match.append(str.lstrip(mlist[4]))
        match.append(mlist[5])
        match.append(str.rstrip(mlist[6]))
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    # ytd = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype','tm_utc08', 'status', 'home', 'result', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(today)[:10] if df['tm_utc08'][i] <= '06:00' else today_utc0[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date'] + ' ' + df['tm_utc08']
    df = df.loc[df.status=='FT']
    df = df[['mtype', 'dt_utc08', 'home', 'result', 'away', 'href_nsc']]
    if lty==True:
        df = df.loc[df.mtype.isin(df_name['league'])].reset_index(drop=True)
    else:
        df = df
    return df

cur_path = os.getcwd()
os.chdir('..')
cur_path = os.getcwd()
his_path = cur_path + '/data/his_data/'
match_file ='nsc_his_' + today_utc0[:10] + '.txt'
match_file_en = 'en_his_' + today_utc0[:10]  + '.txt'
# match_file_td = 'td_his_' + today_utc0[:10]  + '.txt'

if not os.path.exists(his_path + match_file_en):
    print("UTC-2: ", today_utc0)
    df_en = get_match_en(base_url_en)
    df_en['lang'] = 'en'
    df_en.to_csv(his_path + match_file_en, index=False)
    print("generated file: " ,match_file_en )


    df = get_match_007(base_url_007)
    df['lang'] = 'zh_cn'
    df.to_csv(his_path + match_file, index=False, encoding='utf-8')
    print(df.shape)
    print("generated file: " ,match_file )
