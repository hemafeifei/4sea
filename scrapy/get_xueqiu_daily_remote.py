#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _settings import *
import pandas as pd
from datetime import datetime, timedelta
import os

url = 'https://danjuanapp.com/djmodule/value-center?channel=1300100141'
today = str(datetime.now())[:10]
etf_path = '../../database/finance/etf/'
etf_fn = 'xq_' + today + '.txt'

url_jsl = 'https://www.jisilu.cn/data/cbnew/#cb'
cb_path = '../../database/finance/cb/'
cb_fn = 'cb_jisilu.txt'
if not os.path.exists(cb_path):
    os.makedirs(cb_path)
    print("make dir for {}".format(cb_path))

soup_xq = get_soup(url)
soup_jsl = get_soup(url_jsl)

def parse_etf_data(soup):
    """

    :param soup: Beatifulsoup result of xueqiu's daily result
    :return: result_table
    """
    soup = soup_xq
    table = soup.find("div", {'class': 'out-row'})  # updated on 2019-12-27
    name = table.find_all('div', {'class': (lambda value: value.startswith('name'))})
    print("Name length", len(name))
    dinfo = table.find_all('div', {'class': (lambda value: value.startswith('row'))})
    print("data length", len(dinfo))

    if len(name) == len(dinfo):
        name_table = []
        for row in name:
            name_list = []
            name_cn = row.find('h1').get_text()
            name_code = row.find('small').get_text()
            name_list = [name_cn, name_code]
            name_table.append(name_list)

        info_table = []
        for row in dinfo:
            info_list = []
            pe = row.find('div', {'class': 'pe'}).get_text()
            pe_pct = row.find('div', {'class': "pe-per"}).get_text()
            pb = row.find('div', {'class': 'pb'}).get_text()
            pb_pct = row.find('div', {'class': 'pb-per'}).get_text()
            dyr = row.find('div', {'class': 'dyr'}).get_text()
            roe = row.find('div', {'class': 'roe'}).get_text()
            since = row.find('div', {'class': 'begin'}).get_text()
            info_list = [pe, pe_pct, pb, pb_pct, dyr, roe, since]
            info_table.append(info_list)

        df_name = pd.DataFrame(name_table, columns=['name', 'code_xq'])
        df_info = pd.DataFrame(info_table, columns=['pe', 'pe_pct', 'pb', 'pb_pct',
                                                    'dyr', 'roe', 'since'])
        if df_name.shape[0] == df_info.shape[0]:
            df_final = pd.concat([df_name, df_info], axis=1)
            df_final['dt'] = today
            print(df_final.shape)
            print(today, "Update")
            df_final.to_csv(os.path.join(etf_path, etf_fn), index=False)
            with open(etf_path + 'ETF_his_xq.txt', 'a+') as f:
                df_final.to_csv(f, header=False, index=False)
            print("write ETF files append")
            print("****" * 5)


def parse_cb_data(soup):
    table = []
    for tr in soup.find_all('tr')[2:]:
        lst = []
        for td in tr.find_all("td"):
            lst.append(td.get_text())
        table.append(lst)
    cols_name = ['code_cb',
                     'name_cb',
                     'price_cb',
                     'price_cb_chg',
                     'name_sec',
                     'price_sec',
                     'price_sec_chg',
                     'pb_sec',
                     'price_converted',
                     'value_converted',
                     'premium_rate',
                     'value_bond',
                     'risk_lvl',
                     'value_qq',
                     'price_backsell',
                     'price_redemption',
                     'pct_cb',
                     'hld_by_instit',
                     'mature_dt',
                     'left_year',
                     'left_amount',
                     'ytm_pre_tax',
                     'ytm_after_tax',
                     'ytm_backsell',
                     'amount',
                     'low_low',
                     'other']
    df = pd.DataFrame(table, columns=cols_name).drop(['value_bond', 'value_qq', 'other',
                                                          'hld_by_instit', 'ytm_backsell'], axis=1)
    df['image_dt'] = str(datetime.now())[:11]
    print(df.shape)
    with open(os.path.join(cb_path, cb_fn), 'a+') as f:
        df.to_csv(f, header=True, index=False)
    print("write CB files append")
    print("****" * 5)


if today in soup_xq.find("title").get_text():
    print("----"*5)
    parse_etf_data(soup_xq)

    print("----"*5)
    parse_cb_data(soup_jsl)
else:
    print("No updates found on {}".format(today))




