#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools as tools
import os
from datetime import datetime, timedelta
import time
import pandas as pd

df_name = pd.read_csv('league_name.txt', encoding='utf8')
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=8))
now = today[:16]

# file name settings
match_file = today_utc0[:10] + '.txt'
match_file_en = today_utc0[:10] + '_en.txt'


def daily_scrapy_match_and_odds():
    if not os.path.exists(tools.path_parms['match_path'] + match_file):
        df = tools.get_match_007(tools.path_parms['base_url_007'])
        df['lang'] = 'zh_cn'
        df.to_csv(tools.path_parms['match_path'] + match_file, index=False, encoding='utf-8')
        print("generated file: ", match_file)
        df_en = tools.get_match_en(tools.path_parms['base_url_en'])
        df_en['lang'] = 'en'
        df_en.to_csv(tools.path_parms['match_path'] + match_file_en, index=False)
        print("generated file: ", match_file_en)

    else:
        df = pd.read_csv(tools.path_parms['match_path'] + match_file)
        # df_en = pd.read_csv(tools.path_parms['match_path'] + match_file_en)

    today_utc0_path = tools.path_parms['odds_path'] + today_utc0[:10]
    if not os.path.exists(today_utc0_path):
        os.makedirs(today_utc0_path)
        print("make dirs for today's odds")

    print("Start Time is ", str(now)[:16])
    for i in range(len(df)):
        if df.loc[i, 'dt_utc08'] >= now:
            href = df.loc[i, 'href_nsc']
            print("odds of ", href)
            df_eu, df_asia = tools.get_trend_en(href)
            df_eu.to_csv(today_utc0_path + '/' + str(href) + '_eu.txt', index=False, encoding='utf-8')
            df_asia.to_csv(today_utc0_path + '/' + str(href) + '_asia.txt', index=False, encoding='utf-8')
            # time.sleep(1.1)

    end = str(datetime.now())[:16]
    print("End Time is ", end)


if __name__ == '__main__':
    daily_scrapy_match_and_odds()
