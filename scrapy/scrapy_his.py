#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools as tools
import os
from datetime import datetime, timedelta
import pandas as pd

# Global settings
df_name = pd.read_csv('league_name.txt', encoding='utf8')
today = str(datetime.now())

today_utc0 = str(datetime.now() - timedelta(hours=10))
now = today[:16]


# Special settings
his_file = 'nsc_his_' + today_utc0[:10] + '.txt'
# hisfile_en = 'en_his_' + today_utc0[:10] + '.txt'
# match_file_td = 'td_his_' + today_utc0[:10]  + '.txt'

if not os.path.exists(tools.path_parms['his_path'] + his_file):
    print("UTC-2: ", today_utc0[:16])

    df = tools.get_his_007(tools.path_parms['base_url_007'])
    df['lang'] = 'zh_cn'
    df.to_csv(tools.path_parms['his_path'] + his_file, index=False, encoding='utf-8')
    print(df.shape)
    print("generated file: ", his_file)
    print("****Finished {}****".format(str(datetime.now())[:16]))
    print(' ')

