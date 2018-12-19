import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
import re
import os
from pyvirtualdisplay import Display

chrome_path = '/home/centos/football/chromedriver'

# df_name = pd.read_csv('league_name.txt', encoding='utf8')
df_name = pd.read_csv('league_name_ml.txt', encoding='utf8')

base_url_en = 'http://www.nowgoal.com/'

today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=10))
ytd = str(datetime.now() - timedelta(hours=24))
kelly_sum = 1.94

def get_soup(url):
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome(executable_path=chrome_path)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    driver.quit()
    display.stop()
    return soup


def get_match_en(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'class': ['', 'b2']}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(str.lstrip(mlist[4]))
        match.append(mlist[5])
        match.append(str.rstrip(mlist[6]))
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    # ytd = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype','tm_utc08', 'home', 'result', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(today)[:10] if df['tm_utc08'][i] <= '06:00' else ytd[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date'] + ' ' + df['tm_utc08']
    df = df[['mtype', 'dt_utc08', 'home', 'result', 'away', 'href_nsc']]
    if lty==True:
        df = df.loc[df.mtype.isin(df_name['league'])].reset_index(drop=True)
    else:
        df = df
    return df

def get_asian_differ(dataframe):
    now = str(datetime.now())

    odds_table = []
    for ref in list(dataframe['href_nsc']):
        odds_url = 'http://score.nowscore.com/1x2/' + str(ref) + '.htm'
        soup = get_soup(odds_url)
        tb = soup.find('table', {'id': 'oddsList_tab'})

        if tb is not None:

            oddstr_list = [tr['id'] for tr in tb.find_all('tr')]
            if ('oddstr_80' in oddstr_list) & ('oddstr_432' in oddstr_list) & ('oddstr_649' in oddstr_list) & ('oddstr_81' in oddstr_list):
                print(ref, ",该比赛包含香港-澳门赔率，继续分析....")
                odd_list = [ref]

                mac = tb.find('tr', {'id': 'oddstr_80'})
                hk = tb.find('tr', {'id': 'oddstr_432'})
                wede = tb.find('tr', {'id': 'oddstr_81'})
                kbb_kelly = tb.find('tr', {'id': 'oddstr_499'})
                ibcbet_kelly = tb.find('tr', {'id': 'oddstr_649'})

                for td in mac.find_all('td')[3:6]:
                    odd_list.append((td.get_text()))
                for td in hk.find_all('td')[3:6]:
                    odd_list.append((td.get_text()))
                for td in wede.find_all('td')[3:6]:
                    odd_list.append(td.get_text())
                for td in kbb_kelly.find_all('td')[10:13]:
                    odd_list.append((td.get_text()))
                for td in ibcbet_kelly.find_all('td')[10:13]:
                    odd_list.append((td.get_text()))

                odds_table.append(odd_list)

    if len(odds_table) > 0:

        df_trend = pd.DataFrame(odds_table, columns=['href_nsc', 'hw1', 'dw1', 'aw1',
                                                     'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3', 'kly_h1',
                                                     'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2'])

        df_trend.iloc[:,1:]=df_trend.iloc[:,1:].astype(float)

        df_trend['differ_hw'] =  (df_trend['hw2'] - df_trend['hw1'])
        df_trend['differ_dw'] =  (df_trend['dw2'] - df_trend['dw1'])
        df_trend['differ_aw'] =  (df_trend['aw2'] - df_trend['aw1'])
        # df_trend = df_trend.round({'differ_hw': 2, 'differ_dw':2, 'differ_aw':2})
        df_trend['trend'] = 'NA'
        df_trend['asian_hdp'] = 'NA'
        for i in range(len(df_trend)):

            if (df_trend.loc[i, 'hw1'] <= 1.48) | (df_trend.loc[i, 'aw1'] <= 1.48):
                df_trend.loc[i, 'asian_hdp'] = 'Deep'
            elif (df_trend.loc[i, 'hw1'] <= 1.68) | (df_trend.loc[i, 'aw1'] <= 1.68):
                df_trend.loc[i, 'asian_hdp'] = 'Medium'
            elif (df_trend.loc[i, 'hw1'] <= 1.90) | (df_trend.loc[i, 'aw1'] <= 1.90):
                df_trend.loc[i, 'asian_hdp'] = 'Balanced'
            elif (df_trend.loc[i, 'hw1'] <= 2.15) | (df_trend.loc[i, 'aw1'] <= 2.15):
                df_trend.loc[i, 'asian_hdp'] = 'Lucky'
            else:
                df_trend.loc[i, 'asian_hdp'] = 'Shallow'

            if (df_trend.loc[i, 'differ_dw'] > 0) & (df_trend.loc[i, 'differ_hw'] > 0) & (
                df_trend.loc[i, 'differ_aw'] < 0) & (df_trend.loc[i, 'kly_a2'] + df_trend.loc[i, 'kly_a1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'A'

            elif (df_trend.loc[i, 'differ_dw'] > 0) & (df_trend.loc[i, 'differ_aw'] > 0) & (
                df_trend.loc[i, 'differ_hw'] < 0) & (df_trend.loc[i, 'kly_h2'] + df_trend.loc[i, 'kly_h1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'H'
            elif (df_trend.loc[i, 'differ_hw'] > 0) & (df_trend.loc[i, 'differ_aw'] > 0) & (
                df_trend.loc[i, 'differ_dw'] < 0) & (df_trend.loc[i, 'kly_d2'] + df_trend.loc[i, 'kly_d1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'D'
            else:
                df_trend.loc[i, 'trend'] = 'None'
                #         print(df_trend.head())
        df_trend['updated'] = now[11:16]
        # df_trend = df_trend.loc[(df_trend.hw1 >= 1.3) & (df_trend.aw1 >= 1.3)].reset_index(drop=True)

        df_table = df_trend.merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'result', 'away']], on='href_nsc', how='left')
        df_table = df_table[['dt_utc08', 'mtype', 'home', 'result', 'away', 'trend', 'href_nsc', 'asian_hdp','hw1', 'dw1', 'aw1',
                                                     'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3',  'kly_h1',
                                                     'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw']]
        # df_table = df_table.loc[df_table.trend!='None']

    else:
        print('No match found')
        df_table = pd.DataFrame(columns=['dt_utc08', 'mtype', 'home', 'result', 'away', 'trend', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
                                                     'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3',  'kly_h1',
                                                     'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw'])

    return df_table

cur_path = os.getcwd()
os.chdir('..')
cur_path = os.getcwd()
kelly_path =cur_path + '/data/ml_data/'
match_path = cur_path + '/data/'
match_file = 'kelly_' + ytd[:10] + '.txt'
his_file = 'en_his_' + ytd[:10] + '.txt'


def get_nowscore_asian_differ():
    match_nsc = pd.read_csv(match_path + '/his_data/' + his_file)
    match_nsc = match_nsc.loc[match_nsc.mtype.isin(df_name['league'])].reset_index(drop=True)
    print(match_nsc.shape)
    if len(match_nsc) > 0:
        df_differ = get_asian_differ(match_nsc)
        return df_differ
    else:
        return None

if not os.path.exists(kelly_path + match_file):
    differ = get_nowscore_asian_differ()

    if len(differ) > 0:
        print("UTC0:" ,today_utc0[:16])
        print("write files", match_file)
        with open(kelly_path + match_file, 'a+') as f:
            differ.to_csv(f,index=False)
    else:
        print("no result found")
