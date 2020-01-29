# -*- coding: utf-8 -*-

from _settings import *
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import re

weibo_dict = {
    # function 1
    'url': 'https://s.weibo.com/top/summary?cate=realtimehot',

    # path
    'path_weibo': '../../database/senti/weibo',
}
today = str(datetime.now())[:10]
before_24h = str(datetime.now() - timedelta(hours=25))[:16]


def request_weibo(url):
    soup = get_soup(url)

    result = []
    table = soup.find('table')
    if table is not None:
        for tr in table.find_all('tr')[2:17]:
            rank = tr.find('td', {'class': 'td-01'}).get_text()
            topic = tr.find('a').get_text()
            internal_link = tr.find('a')['href']
            link = 'https://s.weibo.com/' + internal_link
            heat = tr.find('span').get_text()
            row = [rank, topic, heat, link]
            result.append(row)

    df = pd.DataFrame(result, columns=['rank', 'topic', 'heat', 'link'])
    df['dt'] = today
    return df


if __name__ == '__main__':
    if not os.path.exists(os.path.join(weibo_dict['path_weibo'], "{}.txt".format(today))):
        df = request_weibo(weibo_dict['url'])
        print(df.shape)
        df.to_csv(os.path.join(weibo_dict['path_weibo'], "{}.txt".format(today)), index=False)
        print("wtrited file as of {}".format(str(datetime.now())[:16]))
        print("***Finished***")
    else:
        print("File exists, break")