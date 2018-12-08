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
df_name = pd.read_csv('league_name_ml.txt', encoding='utf8')
base_url = 'http://score.nowscore.com/index.aspx'
base_url_en = 'http://www.nowgoal.com/'
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=8))
kelly_sum = 1.94
# balanced_mtype = ['ENG PR', 'GER D1', 'ITA D1', 'SPA D1', 'HOL D1', 'KOR D1', 'POR D1',
#                   'UEFA CL', 'UEFA EL']

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


def get_asian_differ(dataframe):
    now = str(datetime.now())
    end = datetime.now() - timedelta(minutes=15)

    length = len(dataframe.loc[dataframe.dt_utc08 <= str(end)[:16]])
    if length > 0 :
        print("有",length,"场比赛已经开始， 将被筛除")
    else:
        print(now[:16], ' start parsing match...')
    dataframe = dataframe.loc[dataframe.dt_utc08 > str(end)[:16]]

    odds_table = []
    for ref in list(dataframe['href_nsc']):
        odds_url = 'http://www.nowgoal.com/1x2/' + str(ref) + '.htm'
        soup = get_soup(odds_url)
        tb = soup.find('table', {'id': 'oddsList_tab'})

        # if len(tb) > 0:
        if tb is not None:

            oddstr_list = [tr['id'] for tr in tb.find_all('tr')]
            if ('oddstr_80' in oddstr_list) & ('oddstr_432' in oddstr_list) & ('oddstr_649' in oddstr_list):
                print(ref, ",该比赛包含香港-澳门赔率，继续分析....")
                odd_list = [ref]

                mac = tb.find('tr', {'id': 'oddstr_80'})
                hk = tb.find('tr', {'id': 'oddstr_432'})
                kbb_kelly = tb.find('tr', {'id': 'oddstr_499'})
                ibcbet_kelly = tb.find('tr', {'id': 'oddstr_649'})

                for td in mac.find_all('td')[2:5]:
                    odd_list.append((td.get_text()))
                for td in hk.find_all('td')[2:5]:
                    odd_list.append((td.get_text()))
                for td in kbb_kelly.find_all('td')[9:12]:
                    odd_list.append((td.get_text()))
                for td in ibcbet_kelly.find_all('td')[9:12]:
                    odd_list.append((td.get_text()))

                odds_table.append(odd_list)

    if len(odds_table) > 0:

        df_trend = pd.DataFrame(odds_table, columns=['href_nsc', 'hw1', 'dw1', 'aw1',
                                                     'hw2', 'dw2', 'aw2', 'kly_h1',
                                                     'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2'])

        df_trend.iloc[:,1:]=df_trend.iloc[:,1:].astype(float)

        df_trend['differ_hw'] = df_trend['hw2'] - df_trend['hw1']
        df_trend['differ_dw'] = df_trend['dw2'] - df_trend['dw1']
        df_trend['differ_aw'] = df_trend['aw2'] - df_trend['aw1']
        df_trend['trend'] = 'NA'
        df_trend['asian_hdp'] = 'NA'
        for i in range(len(df_trend)):

            # if (df_trend.loc[i, 'hw1'] <= 1.45) | (df_trend.loc[i, 'aw1'] < 1.5):
            #     df_trend.loc[i, 'asian_hdp'] = 'Deep'
            # elif (df_trend.loc[i, 'hw1'] < 3.0) & (df_trend.loc[i, 'aw1'] < 3.0):
            #     df_trend.loc[i, 'asian_hdp'] = 'Shallow'
            # else:
            #     df_trend.loc[i, 'asian_hdp'] = 'Balanced'
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

        # df_table  = df_trend.drop(['differ_hw', 'differ_dw', 'differ_aw'],
        #                      axis=1).merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'away']], on='href_nsc', how='left')
        df_table  = df_trend.merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'away']], on='href_nsc', how='left')
        df_table = df_table[['dt_utc08', 'mtype', 'home', 'away', 'trend', 'updated', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
        'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw']]
        df_table = df_table.loc[(df_table.trend!='None')].reset_index(drop=True)





    else:
        print('No match found')
        df_table = pd.DataFrame(columns=['dt_utc08', 'mtype', 'home', 'away', 'trend', 'updated', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
        'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw'])

    return df_table


cur_path = os.getcwd()
os.chdir('..')
cur_path = os.getcwd()

my_path =cur_path + '/data/'
match_pth = my_path + '/match_data/'
differ_path = my_path + '/differ_data/'

match_file = today_utc0[:10] + '.txt'
match_file_en = today_utc0[:10] + '_en.txt'


def get_nowscore_asian_differ(hours=1):
    match_nsc = pd.read_csv(match_pth + match_file_en)
    match_nsc = match_nsc.loc[match_nsc.mtype.isin(df_name['league'])].reset_index(drop=True)
    now_to_hours = str(datetime.today() + timedelta(hours=hours, minutes=10))
    match_nsc = match_nsc.loc[(match_nsc.dt_utc08>=today[:16]) & (match_nsc.dt_utc08 < now_to_hours)].reset_index(drop=True)
    df_differ = get_asian_differ(match_nsc)
    return df_differ

differ = get_nowscore_asian_differ()
if len(differ >0):
    print("Now updated: ", today[:16])
    with open(differ_path + match_file, 'a+') as f:
        differ.to_csv(f, header=False, index=False)
    print("write files: ", differ.shape)
else:
    print("no result writen")
globals()