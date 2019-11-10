#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools as tools
from datetime import datetime, timedelta
import pandas as pd
import os


df_name = pd.read_csv('league_name_ml.txt', encoding='utf8')
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=8))


ytd = str(datetime.now() - timedelta(hours=24))
ks_sum = 1.98

# Special settings
match_file = 'kelly_' + ytd[:10] + '.txt'
his_file = 'nsc_his_' + ytd[:10] + '.txt'


def get_asian_differ(dataframe):
    now = str(datetime.now())

    odds_table = []
    for ref in list(dataframe['href_nsc']):
        odds_url = 'http://score.nowscore.com/1x2/' + str(ref) + '.htm'
        soup = tools.get_soup(odds_url)
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
                df_trend.loc[i, 'differ_aw'] < 0) & (df_trend.loc[i, 'kly_a2'] + df_trend.loc[i, 'kly_a1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'A'
                df_trend.loc[i, 'kelly_sum'] = df_trend.loc[i, 'kly_a2'] + df_trend.loc[i, 'kly_a1']

            elif (df_trend.loc[i, 'differ_dw'] > 0) & (df_trend.loc[i, 'differ_aw'] > 0) & (
                df_trend.loc[i, 'differ_hw'] < 0) & (df_trend.loc[i, 'kly_h2'] + df_trend.loc[i, 'kly_h1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'H'
                df_trend.loc[i, 'kelly_sum'] = df_trend.loc[i, 'kly_h2'] + df_trend.loc[i, 'kly_h1']

            elif (df_trend.loc[i, 'differ_hw'] > 0) & (df_trend.loc[i, 'differ_aw'] > 0) & (
                df_trend.loc[i, 'differ_dw'] < 0) & (df_trend.loc[i, 'kly_d2'] + df_trend.loc[i, 'kly_d1'] < kelly_sum):
                df_trend.loc[i, 'trend'] = 'D'
                df_trend.loc[i, 'kelly_sum'] = df_trend.loc[i, 'kly_d2'] + df_trend.loc[i, 'kly_d1']

            else:
                df_trend.loc[i, 'trend'] = 'None'
                #         print(df_trend.head())
        df_trend['updated'] = now[11:16]
        # df_trend = df_trend.loc[(df_trend.hw1 >= 1.3) & (df_trend.aw1 >= 1.3)].reset_index(drop=True)

        df_table = df_trend.merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'result', 'away']], on='href_nsc', how='left')
        df_table = df_table[['dt_utc08', 'mtype', 'home', 'result', 'away', 'trend', 'href_nsc', 'asian_hdp','hw1', 'dw1', 'aw1',
                            'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3',  'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2',
                             'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]
        # df_table = df_table.loc[df_table.trend!='None']

    else:
        print('No match found')
        df_table = pd.DataFrame(columns=['dt_utc08', 'mtype', 'home', 'result', 'away', 'trend', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
                                         'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3',  'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2', 'kly_a2',
                                         'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum'])

    return df_table

def get_nowscore_asian_differ():
    match_nsc = pd.read_csv(tools.path_parms['his_path'] + his_file)
    match_nsc = match_nsc.loc[match_nsc.mtype.isin(df_name['league_007'])].reset_index(drop=True)
    print(match_nsc.shape)
    if len(match_nsc) > 0:
        df_differ = tools.get_asian_differ(match_nsc, kelly_sum=ks_sum)
        return df_differ
    else:
        return None

if not os.path.exists(tools.path_parms['kelly_path'] + match_file):
    print("Start working at {}".format(today[:16]))
    differ = get_nowscore_asian_differ()

    if len(differ) > 0:
        print("UTC0:", today_utc0[:16])
        print("write files, {}".format(today[:16]), match_file)
        with open(tools.path_parms['kelly_path'] + match_file, 'a+') as f:
            differ.to_csv(f, index=False)
    else:
        print("no result found, {}".format(today[:16]))
    print("****Finished {}****".format(str(datetime.now())[:16]))
    print(' ')
