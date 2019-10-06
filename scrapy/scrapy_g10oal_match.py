#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import *
import tools as tools
import pandas as pd
from datetime import datetime, timedelta
import os
import time


df_name = pd.read_csv('league_name.txt', encoding='utf8')
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=8))
weekday_utc0 = (datetime.now() - timedelta(hours=8)).strftime('%a').upper()
base_url = 'https://g10oal.com/?day=' + weekday_utc0 # replace with g10oal.com

league_mapping = {
    '俄羅斯超級聯賽': 'RUS PR',
    '日本乙組聯賽': 'JPN D2',
    '日本職業聯賽': 'JPN D1',
    '南韓職業聯賽': 'KOR D1',
    '德國乙組聯賽': 'GER D2',
    '英格蘭超級聯賽': 'ENG PR',
    '英格蘭冠軍聯賽': 'ENG LCH',
    '瑞典超級聯賽': 'SWE D1',
    '法國乙組聯賽': 'FRA D2',
    '德國甲組聯賽': 'GER D1',
    '英格蘭甲組聯賽': 'ENG L1',
    '蘇格蘭超級聯賽': 'SCO PR',
    '巴西甲組聯賽': 'BRA D1',
    '西班牙甲組聯賽': 'SPA D1',
    '法國甲組聯賽': 'FRA D1',
    '葡萄牙超級聯賽': 'POR D1',
    '意大利甲組聯賽': 'ITA D1',
    '比利時甲組聯賽': 'BEL D1',
    '挪威超級聯賽': 'NOR D1',
    '阿根廷甲組聯賽': 'ARG D1',
    '荷蘭甲組聯賽': 'HOL D1',
    '智利甲組聯賽': 'CHI D1',
    '荷蘭乙組聯賽': 'HOL D2'
}


def get_g10oal_match(url, lty=True):
    soup = get_soup(url)
    result_tbl = []
    weekday = datetime.now().strftime("%a")
    for card in soup.find_all('div', {'class': 'card-body'}):
        result = []
        header = card.find('h6').get_text().split(' ')[:5]
        home = card.find('a').get_text().strip().split(' ')[0]
        away = card.find('a').get_text().strip().split(' ')[-1]
        link = card.find('a')['href']

        result.extend(header)
        result.append(home)
        result.append(away)
        result.append(link)
        result[0] = weekday + result[0]
#         result[3] = result[3].strip()
        result_tbl.append(result)
    df = pd.DataFrame(result_tbl, columns=['href_goal', 'league_goal', 'null1', 'date', 'time', 'home', 'away', 'link'])
    df = df.drop('null1', axis=1)
    df['time'] = [i.strip() for i in df['time'].values]
    today_utc0 = str(datetime.now() - timedelta(hours=8))
    df['dt_utc08'] = today_utc0[:5] + df['date'] + ' ' + df['time']
    df = df.loc[(df['time'] > '12:00') | (df['time'] < '05:00')].reset_index(drop=True)
    df['league'] = df['league_goal'].map(league_mapping)
    if lty:
        df = df.loc[df.league.isin(df_name['league'])].reset_index(drop=True)
    print(df.shape)
    return df


def get_trend_begin(dataframe, kelly_sum):
    import time

    now = str(datetime.now())
    differ_table = []

    for link in list(dataframe['link']):
        url = 'https://g10oal.com' + link + '/odds'
        print(url)
        soup = get_soup(url)
        time.sleep(1.1)
        differ_lst = []
        result_tbl = []
        for tr in soup.find_all('tr', {'class': 'table-warning'}):
            result = []
            result.extend(tr.get_text().strip().split('\n'))
            result_tbl.append(result)

        df = pd.DataFrame(result_tbl, columns=['company', 'hw', 'dw', 'aw', 'back_rate', 'kly_h', 'kly_d', 'kly_a'])
        df_begin = df.drop_duplicates(subset='company', keep='last')

        check_mac = '澳彩*' in df_begin['company'].values
        check_365 = 'bet365*' in df_begin['company'].values
        check_william = 'William Hill*' in df_begin['company'].values

        if check_mac and check_365 and check_william:
            mac_odd = df_begin.loc[df_begin.company.isin(['澳彩*'])][['hw', 'dw', 'aw']]
            mac_odd = mac_odd.iloc[0, :]
            hk_odd = df_begin.loc[df_begin.company.isin(['馬會*'])][['hw', 'dw', 'aw']]
            hk_odd = hk_odd.iloc[0, :]
            kly_365 = df_begin.loc[df_begin.company.isin(['bet365*'])][['kly_h', 'kly_d', 'kly_a']]
            kly_365 = kly_365.iloc[0, :]
            kly_william = df_begin.loc[df_begin.company.isin(['William Hill*'])][['kly_h', 'kly_d', 'kly_a']]
            kly_william = kly_william.iloc[0, :]

            differ_lst.append(link)
            differ_lst.extend(mac_odd)
            differ_lst.extend(hk_odd)
            differ_lst.extend(kly_365)
            differ_lst.extend(kly_william)

            differ_table.append(differ_lst)

    if len(differ_table) > 0:
        print("match shape, ", len(differ_table))
        df_trend = pd.DataFrame(differ_table, columns=['link', 'hw1', 'dw1', 'aw1',
                                                       'hw2', 'dw2', 'aw2', 'kly_h1',
                                                       'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2'])
        df_trend.iloc[:, 1:] = df_trend.iloc[:, 1:].astype(float)

        df_trend['differ_hw'] = df_trend['hw2'] - df_trend['hw1']
        df_trend['differ_dw'] = df_trend['dw2'] - df_trend['dw1']
        df_trend['differ_aw'] = df_trend['aw2'] - df_trend['aw1']
        df_trend['trend'] = 'NA'
        df_trend['asian_hdp'] = 'NA'
        df_trend['kelly_sum'] = 2.00
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
                        df_trend.loc[i, 'differ_aw'] < 0) & (
                    df_trend.loc[i, 'kly_a2'] + df_trend.loc[i, 'kly_a1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'A'
                df_trend.loc[i, 'kelly_sum'] = df_trend.loc[i, 'kly_a2'] + df_trend.loc[i, 'kly_a1']

            elif (df_trend.loc[i, 'differ_dw'] > 0) & (df_trend.loc[i, 'differ_aw'] > 0) & (
                        df_trend.loc[i, 'differ_hw'] < 0) & (
                    df_trend.loc[i, 'kly_h2'] + df_trend.loc[i, 'kly_h1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'H'
                df_trend.loc[i, 'kelly_sum'] = df_trend.loc[i, 'kly_h2'] + df_trend.loc[i, 'kly_h1']

            elif (df_trend.loc[i, 'differ_hw'] > 0) & (df_trend.loc[i, 'differ_aw'] > 0) & (
                        df_trend.loc[i, 'differ_dw'] < 0) & (
                    df_trend.loc[i, 'kly_d2'] + df_trend.loc[i, 'kly_d1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'D'
                df_trend.loc[i, 'kelly_sum'] = df_trend.loc[i, 'kly_d2'] + df_trend.loc[i, 'kly_d1']

            else:
                df_trend.loc[i, 'trend'] = 'None'
                #         print(df_trend.head())
        df_trend['updated'] = now[11:16]
        # df_trend = df_trend.loc[(df_trend.hw1 >= 1.3) & (df_trend.aw1 >= 1.3)].reset_index(drop=True)

        df_table = df_trend.merge(dataframe[['dt_utc08', 'league', 'home', 'away', 'link']], on='link', how='left')
        df_table = df_table[
            ['dt_utc08', 'league', 'home', 'away', 'trend', 'updated', 'link', 'asian_hdp', 'hw1', 'dw1', 'aw1',
             'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw',
             'differ_aw', 'kelly_sum']]
        df_table = df_table.loc[(df_table.trend != 'None')].reset_index(drop=True)
    else:
        print('No match found')
        df_table = pd.DataFrame(
            columns=['dt_utc08', 'league', 'home', 'away', 'trend', 'updated', 'link', 'asian_hdp', 'hw1', 'dw1', 'aw1',
                     'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw',
                     'differ_dw', 'differ_aw', 'kelly_sum'])

    return df_table


# get match
my_path = tools.path_parms['match_path']
match_file_gl = today[:10] + '_gl.txt'

if not os.path.exists(my_path + match_file_gl):
    df_gl = get_g10oal_match(base_url)
    df_gl.to_csv(my_path + match_file_gl, index=False, encoding='utf-8')
    print("generated file: ", match_file_gl)
else:
    print("Match file existed.")


# get begin trend
def get_gl_differ():
    df_gl = pd.read_csv(my_path + match_file_gl)
    print("Match Shape", df_gl.shape)

    df_differ = get_trend_begin(df_gl, kelly_sum=1.98)
    print("Trend Shape", df_differ.shape)
    return df_differ

differ_path = tools.path_parms['differ_path']
if not os.path.exists(differ_path + match_file_gl):
    differ = get_gl_differ()
    if len(differ >0):
        print("Now updated: ", today[:16])
        differ.to_csv(differ_path + match_file_gl, index=False)
    else:
        print("no result writen")
else:
    print("Trend begin exsited")
