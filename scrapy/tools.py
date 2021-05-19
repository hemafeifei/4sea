#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _settings import *
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO

df_name = pd.read_csv('league_name.txt', encoding='utf8')
path_parms = {
    # Main path
    'base_dir': './',
    'data_dir': '../../database/football/',
    'model_dir': '../../model/',
    # Sub Path
    'match_path': '../../database/football/match_data/',
    'odds_path': '../../database/football/odds_data/',
    'differ_path': '../../database/football/differ_data/',
    'his_path': '../../database/football/his_data/',
    'kelly_path': '../../database/football/ml_data/',
    # URL
    'base_url_nsc': 'http://score.nowscore.com/index.aspx',
    'base_url_007': 'http://live.win007.com',  # updated on 2019-08-12
    'base_url_en': 'http://www.nowgoal3.com/', # updated on 2021-01-29

}


# chrome_path = '/Users/weizheng/PycharmProjects/tickets/chromedriver'

def insert_table(df, database, db_table):
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/{}'.format(database))
    conn = engine.raw_connection()

    # Initialize a string buffer
    sio = StringIO()
    sio.write(df.to_csv(index=None, header=None))  # Write the Pandas DataFrame as a csv to the buffer
    sio.seek(0)  # Be sure to reset the position to the start of the stream

    # Copy the string buffer to the database, as if it were an actual file
    with conn.cursor() as c:
        c.copy_from(sio, db_table, columns=df.columns, sep=',')
        conn.commit()
        c.close()

# Get matches
def get_match_007(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'id': (lambda value: value and value.startswith("tr1_"))}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(mlist[4])
        match.append(mlist[6])
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype', 'tm_utc08', 'home', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(tomorrow)[:10] if df['tm_utc08'][i] <= '06:00' else now[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date'] + ' ' + df['tm_utc08']
    df = df[['mtype', 'dt_utc08', 'home', 'away', 'href_nsc']]
    print("Before filtering, ", df.shape)
    if lty == True:
        df = df.loc[df.mtype.isin(df_name['league_007'])].reset_index(drop=True)
    else:
        df = df
    print("After name fiter, ", df.shape)
    return df


def get_match_en(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'class': ['', 'b2']}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(str.lstrip(mlist[4]))
        match.append(str.rstrip(mlist[6]))
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype', 'tm_utc08', 'home', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(tomorrow)[:10] if df['tm_utc08'][i] <= '06:00' else now[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = [row['date'] + ' ' + row['tm_utc08'] for i, row in df.iterrows()]
    df = df[['mtype', 'dt_utc08', 'home', 'away', 'href_nsc']]
    if lty == True:
        df = df.loc[df.mtype.isin(df_name['league'])].reset_index(drop=True)
    else:
        df = df
    return df


# Get trend
def get_trend_en(ref):
    now = str(datetime.now())
    odd_start = datetime.now() - timedelta(hours=12)
    trend_url = 'http://data.nowgoal.com/3in1odds/14_' + str(ref) + '.html'  # nowgoal
    soup = get_soup(trend_url)

    asian = []
    e0 = soup.find_all('table', {'class': 'gts'})[1]
    for tr in e0.find_all('tr')[2:14]:  # nowgoal:2, nsc:1
        asian.append([td.get_text() for td in tr.find_all('td')])

    if len(asian) > 0:
        df_asian = pd.DataFrame(asian, columns=['na1', 'na2', 'home',
                                                'pankou', 'away', 'dt', 'others']).loc[:, 'home':]
        df_asian.dt = [(now[:5] + df_asian.loc[i, 'dt'][-11:]) for i in range(len(df_asian))]
        df_asian = df_asian.sort_values(by='dt').reset_index(drop=True)
        df_asian = df_asian.loc[df_asian.dt >= str(odd_start)[:16]]
        df_asian.dt = pd.to_datetime(df_asian.dt, format='%Y-%m-%d %H:%M')
    else:
        df_asian = pd.DataFrame(asian, columns=['home', 'pankou', 'away', 'dt', 'others'])
    df_asian = df_asian.drop('others', axis=1)

    odds = []
    e2 = soup.find_all('table', {'class': 'gts'})[0]  # nowgoal
    for tr in e2.find_all('tr')[2:14]:  # nsc
        odds.append([td.get_text() for td in tr.find_all('td')])
    if len(odds) > 0:
        df_odds = pd.DataFrame(odds, columns=['na1', 'na2', 'home',
                                              'draw', 'away', 'dt', 'others']).loc[:, 'home':]
        df_odds.dt = [(now[:5] + df_odds.loc[i, 'dt'][-11:]) for i in range(len(df_odds))]
        df_odds = df_odds.loc[df_odds.dt >= str(odd_start)[:16]]
        df_odds.dt = pd.to_datetime(df_odds.dt, format='%Y-%m-%d %H:%M')
        df_odds = df_odds.sort_values(by='dt').reset_index(drop=True)
        # df_odds['title'] = title
    else:
        df_odds = pd.DataFrame(columns=['home', 'draw', 'away', 'dt', 'others'])
    df_odds = df_odds.drop('others', axis=1)

    return df_odds, df_asian


# Get trend
def get_trend_cn(ref):
    now = str(datetime.now())
    odd_start = datetime.now() - timedelta(hours=12)
    trend_url = 'http://score.nowscore.com/odds/3in1Odds.aspx?companyid=14&id=' + str(ref) # nowscore
    soup = get_soup(trend_url)

    asian = []
    e0 = soup.find_all('table', {'class': 'gts'})[1]
    for tr in e0.find_all('tr')[1:14]:  # nowgoal:2, nsc:1
        asian.append([td.get_text() for td in tr.find_all('td')])

    if len(asian) > 0:
        df_asian = pd.DataFrame(asian, columns=['na1', 'na2', 'home',
                                                'pankou', 'away', 'dt', 'others']).loc[:, 'home':]
        df_asian.dt = [(now[:5] + df_asian.loc[i, 'dt'][:5] + ' ' + df_asian.loc[i, 'dt'][5:]) for i in
                       range(len(df_asian))]
        df_asian = df_asian.sort_values(by='dt').reset_index(drop=True)
        df_asian = df_asian.loc[df_asian.dt >= str(odd_start)[:16]]
        df_asian.dt = pd.to_datetime(df_asian.dt, format='%Y-%m-%d %H:%M')
    else:
        df_asian = pd.DataFrame(asian, columns=['home', 'pankou', 'away', 'dt', 'others'])
    df_asian = df_asian.drop('others', axis=1)

    odds = []
    e2 = soup.find_all('table', {'class': 'gts'})[2]  # nowscore
    for tr in e2.find_all('tr')[1:14]:  # nsc
        odds.append([td.get_text() for td in tr.find_all('td')])
    if len(odds) > 0:
        df_odds = pd.DataFrame(odds, columns=['na1', 'na2', 'home',
                                              'draw', 'away', 'dt', 'others']).loc[:, 'home':]
        df_odds.dt = [(now[:5] + df_odds.loc[i, 'dt'][:5] + ' ' + df_odds.loc[i, 'dt'][5:]) for i in
                      range(len(df_odds))]
        df_odds = df_odds.loc[df_odds.dt >= str(odd_start)[:16]]
        df_odds.dt = pd.to_datetime(df_odds.dt, format='%Y-%m-%d %H:%M')
        df_odds = df_odds.sort_values(by='dt').reset_index(drop=True)
        # df_odds['title'] = title
    else:
        df_odds = pd.DataFrame(columns=['home', 'draw', 'away', 'dt', 'others'])
    df_odds = df_odds.drop('others', axis=1)

    return df_odds, df_asian


# Get differ
def get_odds_differ(dataframe, kelly_sum):
    now = str(datetime.now())
    end = datetime.now() - timedelta(minutes=15)

    length = len(dataframe.loc[dataframe.dt_utc08 <= str(end)[:16]])
    if length > 0:
        print("有", length, "场比赛已经开始， 将被筛除")
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
                print(ref, ",Contains Macau and HKJC....")
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

        df_table = df_trend.merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'away']], on='href_nsc',
                                  how='left')
        df_table = df_table[
            ['dt_utc08', 'mtype', 'home', 'away', 'trend', 'updated', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
             'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw',
             'differ_aw', 'kelly_sum']]
        df_table = df_table.loc[(df_table.trend != 'None')].reset_index(drop=True)
    else:
        print('No match found')
        df_table = pd.DataFrame(
            columns=['dt_utc08', 'mtype', 'home', 'away', 'trend', 'updated', 'href_nsc', 'asian_hdp', 'hw1', 'dw1',
                     'aw1',
                     'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw',
                     'differ_dw', 'differ_aw', 'kelly_sum'])

    return df_table


# get differ from nsc
def get_odds_differ_nsc(dataframe, kelly_sum):
    now = str(datetime.now())
    end = datetime.now() - timedelta(minutes=30)

    length = len(dataframe.loc[dataframe.dt_utc08 <= str(end)[:16]])
    if length > 0:
        print("有", length, "场比赛已经开始， 将被筛除")
    else:
        print(now[:16], ' start parsing match...')
    dataframe = dataframe.loc[dataframe.dt_utc08 > str(end)[:16]]

    odds_table = []
    for ref in list(dataframe['href_nsc']):
        odds_url = 'http://score.nowscore.com/1x2/' + str(ref) + '.htm'
        soup = get_soup(odds_url)
        tb = soup.find('table', {'id': 'oddsList_tab'})

        if tb is not None:

            oddstr_list = [tr['id'] for tr in tb.find_all('tr')]
            if ('oddstr_80' in oddstr_list) & ('oddstr_432' in oddstr_list) & ('oddstr_649' in oddstr_list) & (
                    'oddstr_81' in oddstr_list):
                print(ref, ",Contains Macau and HKJC....")
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
                                                     'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2'])

        df_trend.iloc[:, 1:] = df_trend.iloc[:, 1:].astype(float)

        df_trend['differ_hw'] = (df_trend['hw2'] - df_trend['hw1'])
        df_trend['differ_dw'] = (df_trend['dw2'] - df_trend['dw1'])
        df_trend['differ_aw'] = (df_trend['aw2'] - df_trend['aw1'])
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

        df_table = df_trend.merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'away']], on='href_nsc',
                                  how='left')
        df_table = df_table[
            ['dt_utc08', 'mtype', 'home', 'away', 'trend', 'updated', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
             'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw',
             'differ_aw', 'kelly_sum']]
        df_table = df_table.loc[df_table.trend!='None']

    else:
        print('No match found')
        df_table = pd.DataFrame(
            columns=['dt_utc08', 'mtype', 'home', 'away', 'trend', 'updated', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
             'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw',
             'differ_aw', 'kelly_sum'])

    return df_table


# historic differ for kelly_nsc
def get_asian_differ(dataframe, kelly_sum):
    now = str(datetime.now())

    odds_table = []
    for ref in list(dataframe['href_nsc']):
        odds_url = 'http://score.nowscore.com/1x2/' + str(ref) + '.htm'
        soup = get_soup(odds_url)
        tb = soup.find('table', {'id': 'oddsList_tab'})

        if tb is not None:

            oddstr_list = [tr['id'] for tr in tb.find_all('tr')]
            if ('oddstr_80' in oddstr_list) & ('oddstr_432' in oddstr_list) & ('oddstr_649' in oddstr_list) & (
                    'oddstr_81' in oddstr_list):
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
                                                     'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2'])

        df_trend.iloc[:, 1:] = df_trend.iloc[:, 1:].astype(float)

        df_trend['differ_hw'] = (df_trend['hw2'] - df_trend['hw1'])
        df_trend['differ_dw'] = (df_trend['dw2'] - df_trend['dw1'])
        df_trend['differ_aw'] = (df_trend['aw2'] - df_trend['aw1'])
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

        df_table = df_trend.merge(dataframe[['href_nsc', 'dt_utc08', 'mtype', 'home', 'result', 'away']], on='href_nsc',
                                  how='left')
        df_table = df_table[
            ['dt_utc08', 'mtype', 'home', 'result', 'away', 'trend', 'href_nsc', 'asian_hdp', 'hw1', 'dw1', 'aw1',
             'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2',
             'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]
        # df_table = df_table.loc[df_table.trend!='None']

    else:
        print('No match found')
        df_table = pd.DataFrame(
            columns=['dt_utc08', 'mtype', 'home', 'result', 'away', 'trend', 'href_nsc', 'asian_hdp', 'hw1', 'dw1',
                     'aw1',
                     'hw2', 'dw2', 'aw2', 'hw3', 'dw3', 'aw3', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2',
                     'kly_a2', 'kly_a2',
                     'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum'])

    return df_table


# Get History
def get_his_007(url, lty=True):
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

        today = str(datetime.now())
    today_utc0 = str(datetime.now() - timedelta(hours=10))
    # tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype', 'tm_utc08', 'status', 'home', 'result', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(today)[:10] if df['tm_utc08'][i] <= '06:00' else today_utc0[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date'] + ' ' + df['tm_utc08']
    df = df.loc[df.status == '完']
    df = df[['mtype', 'dt_utc08', 'home', 'result', 'away', 'href_nsc']]
    if lty == True:
        df = df.loc[df.mtype.isin(df_name['league_007'])].reset_index(drop=True)
    else:
        df = df
    return df
