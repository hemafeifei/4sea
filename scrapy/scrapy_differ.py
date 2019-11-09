#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools as tools
from datetime import datetime, timedelta
import pandas as pd

df_name = pd.read_csv('league_name_ml.txt', encoding='utf8')
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=8))

match_file = today_utc0[:10] + '.txt'
match_file_en = today_utc0[:10] + '_en.txt'
ks_sum = 1.98


def get_nowscore_asian_differ(hours=0):
    match_nsc = pd.read_csv(tools.path_parms['match_path'] + match_file)
    print(match_nsc.shape)
    match_nsc = match_nsc.loc[match_nsc.mtype.isin(df_name['league_007'])].reset_index(drop=True)

    now_to_hours = str(datetime.today() + timedelta(hours=hours, minutes=50)) # depends on server performance
    match_nsc = match_nsc.loc[(match_nsc.dt_utc08 >= today[:16]) &
                              (match_nsc.dt_utc08 < now_to_hours)].reset_index(drop=True)
    print(match_nsc.shape)
    df_differ = tools.get_odds_differ(match_nsc, kelly_sum=ks_sum)
    return df_differ


def main_control():
    differ = get_nowscore_asian_differ()
    if len(differ) > 0:
        with open(tools.path_parms['differ_path'] + match_file, 'a+') as f:
            differ.to_csv(f, header=False, index=False)
        print("write files: ", differ.shape)
        print("Updated at: ", str(datetime.now())[:16])
        print(' ')
    else:
        print("no result writen")
    print("****Finished****")
    print(' ')


if __name__ == '__main__':
    main_control()
