#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import *
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import re

bloombg_dict = {
    # function 1
    'url_dax30': 'https://www.investing.com/indices/germany-30-historical-data',
    'url_sp500': 'https://www.investing.com/indices/us-spx-500-historical-data',
    'url_hsi':  'https://www.investing.com/indices/hang-sen-40-historical-data',
    'url_shanghai': 'https://www.investing.com/indices/shanghai-composite-historical-data',
    'url_gold': 'https://www.investing.com/commodities/gold-historical-data',
    # function 2
    'url_oil': 'https://www.investing.com/commodities/brent-oil-historical-data',
    # function 3
    'url_fx_usd_jpy': 'https://cn.investing.com/currencies/usd-jpy-historical-data',
    'url_fx_gbp_jpy': 'https://cn.investing.com/currencies/gbp-jpy-historical-data',

    # path
    'path_idx': '/home/centos/PythonApp/database/finance/idx/',
    'path_fx': '/home/centos/PythonApp/database/finance/fx/',
}


def parse_index_data_1(url):
    """
    price over 1,000. need to be cleaned.
    """
    soup = get_soup(url)
    table = soup.find('table', {'id': 'curr_table'}).find('tbody')

    result = []
    for tr in table.find_all('tr'):
        line = []
        for td in tr.find_all('td'):
            item = td.get_text()
            line.append(item)
        result.append(line)

    df = pd.DataFrame(result, columns=['date', 'close', 'open', 'high', 'low', 'vol', 'change'])
    df['date'] = pd.to_datetime(df['date'], format='%Y年%m月%d日')
    for col in ['close', 'open', 'high', 'low']:
        df[col] = df[col].apply(lambda x: re.sub(',', '', x))
        df[col] = df[col].astype('float')
    print("Max date:", df['date'].max())
    return df


def parse_index_data_2(url):
    """
    oil price as less than 1,000
    """
    soup = get_soup(url)
    table = soup.find('table', {'id': 'curr_table'}).find('tbody')

    result = []
    for tr in table.find_all('tr'):
        line = []
        for td in tr.find_all('td'):
            item = td.get_text()
            line.append(item)
        result.append(line)

    df = pd.DataFrame(result, columns=['date', 'close', 'open', 'high', 'low', 'vol', 'change'])
    df['date'] = pd.to_datetime(df['date'], format='%Y年%m月%d日')
    print("Max date:", df['date'].max())
    return df


def parse_index_data_3(url):
    """
    without volume
    """
    soup = get_soup(url)
    table = soup.find('table', {'id': 'curr_table'}).find('tbody')

    result = []
    for tr in table.find_all('tr'):
        line = []
        for td in tr.find_all('td'):
            item = td.get_text()
            line.append(item)
        result.append(line)

    df = pd.DataFrame(result, columns=['date', 'close', 'open', 'high', 'low', 'change'])
    df['date'] = pd.to_datetime(df['date'], format='%Y年%m月%d日')
    print("Max date:", df['date'].max())
    return df


# upd_dax30 = parse_index_data_1(bloombg_dict['url_dax30'])
# time.sleep(1.1)
# upd_sp500 = parse_index_data_1(bloombg_dict['url_sp500'])
# time.sleep(1.1)
# upd_hsi = parse_index_data_1(bloombg_dict['url_hsi'])
# time.sleep(1.1)
# upd_shanghai = parse_index_data_1(bloombg_dict['url_shanghai'])
# time.sleep(1.1)
# upd_gold = parse_index_data_1(bloombg_dict['url_gold'])
# time.sleep(1.1)
# upd_oil = parse_index_data_2(bloombg_dict['url_oil'])
#
time.sleep(1.1)
upd_fx_usd_jpy = parse_index_data_3(bloombg_dict['url_fx_usd_jpy'])
time.sleep(1.1)
upd_fx_gbp_jpy = parse_index_data_3(bloombg_dict['url_fx_gbp_jpy'])

# # check Global Index
# his_dax30 = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_dax30_his.txt'), parse_dates=[0], index_col=False)
# his_sp500 = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_sp500_his.txt'), parse_dates=[0], index_col=False)
# his_hsi = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_hsi_his.txt'), parse_dates=[0], index_col=False)
# his_shanghai = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_shanghai_his.txt'), parse_dates=[0], index_col=False)
# his_gold = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_gold_his.txt'), parse_dates=[0], index_col=False)
# his_oil = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_oil_his.txt'), parse_dates=[0], index_col=False)
#
# filter_dax30 = upd_dax30.loc[upd_dax30.date > his_dax30['date'].max()]
# if len(filter_dax30) > 0:
#     print("Update Dax30")
#     his_dax30 = pd.concat([his_dax30, filter_dax30], ignore_index=True)
#     his_dax30 = his_dax30.sort_values('date').reset_index(drop=True)
#     print(his_dax30.tail(2))
#     his_dax30.to_csv(os.path.join(bloombg_dict['path_idx'], 'idx_dax30_his.txt'), index=False)
#     print(' ')
#
# filter_sp500 = upd_sp500.loc[upd_sp500.date > his_sp500['date'].max()]
# if len(filter_sp500) > 0:
#     print("Update SP500")
#     his_sp500 = pd.concat([his_sp500, filter_sp500], ignore_index=True)
#     his_sp500 = his_sp500.sort_values('date').reset_index(drop=True)
#     print(his_sp500.tail(2))
#     his_sp500.to_csv(os.path.join(bloombg_dict['path_idx'], 'idx_sp500_his.txt'), index=False)
#     print(' ')
#
# filter_hsi = upd_hsi.loc[upd_hsi.date > his_hsi['date'].max()]
# if len(filter_hsi) > 0:
#     print("Update HSI^")
#     his_hsi = pd.concat([his_hsi, filter_hsi], ignore_index=True)
#     his_hsi = his_hsi.sort_values('date').reset_index(drop=True)
#     print(his_hsi.tail(2))
#     his_hsi.to_csv(os.path.join(bloombg_dict['path_idx'], 'idx_hsi_his.txt'), index=False)
#     print(' ')
#
# filter_shanghai = upd_shanghai.loc[upd_shanghai.date > his_shanghai['date'].max()]
# if len(filter_shanghai) > 0:
#     print("Update Shanghai")
#     his_shanghai = pd.concat([his_shanghai, filter_shanghai], ignore_index=True)
#     his_shanghai = his_shanghai.sort_values('date').reset_index(drop=True)
#     print(his_shanghai.tail(2))
#     his_shanghai.to_csv(os.path.join(bloombg_dict['path_idx'], 'idx_shanghai_his.txt'), index=False)
#     print(' ')
#
# filter_gold = upd_gold.loc[upd_gold.date > his_gold['date'].max()]
# if len(filter_gold) > 0:
#     print("Update Gold")
#     his_gold = pd.concat([his_gold, filter_gold], ignore_index=True)
#     his_gold = his_gold.sort_values('date').reset_index(drop=True)
#     print(his_gold.tail(2))
#     his_gold.to_csv(os.path.join(bloombg_dict['path_idx'], 'idx_gold_his.txt'), index=False)
#     print(' ')
#
# filter_oil = upd_oil.loc[upd_oil.date > his_oil['date'].max()]
# if len(filter_oil) > 0:
#     print("Update Oil")
#     his_oil = pd.concat([his_oil, filter_oil], ignore_index=True)
#     his_oil = his_oil.sort_values('date').reset_index(drop=True)
#     print(his_oil.tail(2))
#     his_oil.to_csv(os.path.join(bloombg_dict['path_idx'], 'idx_oil_his.txt'), index=False)
#     print(' ')
#
#
# # Check fx
# his_fx_usd_jpy = pd.read_csv(os.path.join(bloombg_dict['path_fx'], 'fx_usd_jpy.txt'), parse_dates=[0], index_col=False)
# filter_fx_usd_jpy = upd_fx_usd_jpy.loc[upd_fx_usd_jpy.date > his_fx_usd_jpy['date'].max()]
# if len(filter_fx_usd_jpy) > 0:
#     print("Update FX USD-JPY")
#     his_fx_usd_jpy = pd.concat([his_fx_usd_jpy, filter_fx_usd_jpy], ignore_index=True)
#     his_fx_usd_jpy = his_fx_usd_jpy.sort_values('date').reset_index(drop=True)
#     print(his_fx_usd_jpy.tail(2))
#     his_fx_usd_jpy.to_csv(os.path.join(bloombg_dict['path_fx'], 'fx_usd_jpy.txt'), index=False)
#     print(' ')


his_fx_gbp_jpy = pd.read_csv(os.path.join(bloombg_dict['path_fx'], 'fx_gbp_jpy.txt'), parse_dates=[0], index_col=False)
filter_fx_gbp_jpy = upd_fx_gbp_jpy.loc[upd_fx_gbp_jpy.date > his_fx_usd_jpy['date'].max()]
if len(filter_fx_usd_jpy) > 0:
    print("Update FX GBP-JPY")
    his_fx_gbp_jpy = pd.concat([his_fx_gbp_jpy, filter_fx_gbp_jpy], ignore_index=True)
    his_fx_gbp_jpy = his_fx_gbp_jpy.sort_values('date').reset_index(drop=True)
    print(his_fx_gbp_jpy.tail(2))
    his_fx_gbp_jpy.to_csv(os.path.join(bloombg_dict['path_fx'], 'fx_gbp_jpy.txt'), index=False)
    print(' ')


print("****Finished {}****".format(str(datetime.now())[:16]))
