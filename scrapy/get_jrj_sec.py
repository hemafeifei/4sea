#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _settings import *
import pandas as pd
from datetime import datetime, timedelta
import time
import os

PARAM_DICT = {
    'url_jrj_1': 'http://summary.jrj.com.cn/scfl/index.shtml?q=cn|s|sa&c=m&n=hqa&o=tm,d&p=1050',
    'url_jrj_2': 'http://summary.jrj.com.cn/scfl/index.shtml?q=cn|s|sa&c=m&n=hqa&o=tm,d&p=2050',
    'url_jrj_etf': 'http://summary.jrj.com.cn/fund/etfhq.shtml?q=cn|f|etf&n=fundClose&c=code,' +
                   'name,np,pl,ta,tm,hp,lp,op,lcp&o=tm,d&p=1050',
    'url_jrj_smry': 'http://summary.jrj.com.cn/',
    'url_sohu': 'http://q.stock.sohu.com/?spm=smpc.ch15.top-subnav.3.1572700064202fgd1zoZ',

    # path
    'path_sec': '../../database/finance/sec/'
}


def get_jrj_etf_info(url):
    soup = get_soup(url)
    market_dt = soup.find("span", {'id': "hqTime_d"}).get_text()
    table = soup.find('div', {'class': 'bd bd1'}).find("tbody")

    result = []
    for tr in table.find_all("tr"):
        row = []
        for td in tr.find_all("td"):
            row.append(td.get_text())
        result.append(row)
    df = pd.DataFrame(result, columns=['code', 'name', 'close', 'change', 'txn_vol', 'txn_amt',
                                       'high', 'low', 'open', 'last_close', 'drop1'])
    df['txn_amt'] = df['txn_amt'].astype(float)
    return df.drop('drop1', axis=1), market_dt


def get_jrj_txn_info(url):
    soup = get_soup(url)
    table = soup.find('div', {'class': 'bd'}).find("tbody")

    result = []
    for tr in table.find_all("tr"):
        row = []
        for td in tr.find_all("td"):
            row.append(td.get_text())
        result.append(row)
    df = pd.DataFrame(result, columns=['code', 'name', 'close', 'change', 'drop1', 'txn_vol', 'txn_amt',
                                       'high_low', 'drop2', 'pe', 'views', 'drop3'])
    df['views'] = [i.split('次')[0] for i in df['views'].values]
    df['code'] = ['SH' + i if i.startswith('6') else 'SZ' + i for i in df['code'].values]
    df['txn_amt'] = df['txn_amt'].astype(float)
    return df.drop(['drop1', 'drop2', 'drop3'], axis=1)


def get_jrj_summary(url):
    soup = get_soup(url)
    result = []
    for row in soup.find("div", {"class": "zoom jrj-fl scgl_s1_scgl"}).find_all("div", {
        "class": (lambda x: "jrj-accordion-trigger" in x)}):
        result.append(row.get_text().split('\n'))
    df = pd.DataFrame(result, columns=['drop1', 'name', 'close', 'change_pt', 'change', 'txn_amt', 'drop2'])
    df['txn_amt'] = [i.split('亿')[0] for i in df['txn_amt'].values]
    df_raw = df.drop(['drop1', 'drop2'], axis=1)
    df_smry = pd.DataFrame({'txn_amt_sh': [int(df_raw['txn_amt'][0])],
                            'txn_amt_sz': [int(df_raw['txn_amt'][1])],
                            'txn_amt_hs300': [int(df_raw['txn_amt'][2])],
                            'txn_amt_zz500': [int(df_raw['txn_amt'][5])],
                            'txn_amt_cyb': [int(df_raw['txn_amt'][3])],
                            })
    df_smry['txn_amt_all'] = df_smry['txn_amt_sh'] + df_smry['txn_amt_sz']
    return df_smry


def get_sohu_summary(url):
    soup = get_soup(url)

    row2 = soup.find("div", {"class": "panzhong_info"})
    table = row2.find("tbody")
    result = []
    for tr in table.find_all("tr"):
        result.append([i for i in tr.get_text().strip().split('\n') if i != ''][1:])

    cleaned_result = []
    for i in [0, 2, 3, 4]:
        cleaned_result.extend(result[i])
    cleaned_result.append(result[1][0])
    cleaned_result.append(result[1][1][1])
    cleaned_result.append(result[1][2])
    cleaned_result.append(result[1][3])
    cleaned_result.append(result[1][4][1])
    cleaned_result.append(result[1][5])

    df = pd.DataFrame([cleaned_result],
                      columns=['num_sh', 'num_sz', 'mv_sh', 'mv_sz', 'amount_sh', 'amount_sz', 'pe_sh', 'pe_sz',
                               'incr_sh', 'draw_sh', 'decr_sh', 'incr_sz', 'draw_sz', 'decr_sz', ])
    return df


def main_func():
    # today = datetime.today() - timedelta(days=2)
    today = datetime.today()
    fn_eft_txn_top50 = 'etf_txn_top50_' + str(today)[:10] + '.txt'
    fn_sec_txn_top100 = 'sec_txn_top100_' + str(today)[:10] + '.txt'
    fn_smry_sec = 'sec_txn_summary.txt'
    if (not os.path.exists(PARAM_DICT['path_sec'] + fn_sec_txn_top100)) or (
    not os.path.exists(PARAM_DICT['path_sec'] + fn_eft_txn_top50)):
        print("---Start Time: {}----".format(str(datetime.now())[:16]))
        txn_etf, mkt_dt = get_jrj_etf_info(PARAM_DICT['url_jrj_etf'])
        print("Market date is", mkt_dt)

        assert pd.to_datetime(mkt_dt, format='%m月%d日 %H:%M:%S').day == today.day
        txn_etf.to_csv((PARAM_DICT['path_sec'] + fn_eft_txn_top50), index=False)
        print("write csv: {}".format(fn_eft_txn_top50))

        txn_top50 = get_jrj_txn_info(PARAM_DICT['url_jrj_1'])
        txn_50_100 = get_jrj_txn_info(PARAM_DICT['url_jrj_2'])
        txn_top100 = pd.concat([txn_top50, txn_50_100], ignore_index=True)
        txn_top100.to_csv((PARAM_DICT['path_sec'] + fn_sec_txn_top100), index=False)
        print("write csv: {}".format(fn_sec_txn_top100))

        jrj_smry = get_jrj_summary(PARAM_DICT['url_jrj_smry'])
        jrj_smry['txn_sec_top50'] = int(txn_top100['txn_amt'][:50].sum())
        jrj_smry['txn_sec_top100'] = int(txn_top100['txn_amt'].sum())
        jrj_smry['txn_etf_top50'] = int(txn_etf['txn_amt'].sum())
        jrj_smry['date'] = str(today)[:10]

        if len(jrj_smry) > 0:
            if not os.path.exists(PARAM_DICT['path_sec'] + fn_smry_sec):
                jrj_smry.to_csv((PARAM_DICT['path_sec'] + fn_smry_sec), index=False)
                print("Gernerate file {}".format(fn_smry_sec))
                print("---End Time: {}----".format(str(datetime.now())[:16]))
            else:
                with open((PARAM_DICT['path_sec'] + fn_smry_sec), 'a+') as f:
                    jrj_smry.to_csv(f, header=False, index=False)
                    print("Update file {} As of {}".format(fn_smry_sec, str(today)[:16]))
                    print("---End Time: {}----".format(str(datetime.now())[:16]))

    else:
        print("---Break cauz {} exist---".format(fn_sec_txn_top100))


if __name__ == '__main__':
    main_func()
