# -*- coding: utf-8 -*-

from _settings import *
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import re

jisilu_dict = {
    # function 1
    'url_list': ['https://www.jisilu.cn/home/explore/category-__sort_type-add_time',
                 'https://www.jisilu.cn/home/explore/sort_type-add_time__category-__day-0__is_recommend-__page-2',
                 'https://www.jisilu.cn/home/explore/sort_type-add_time__category-__day-0__is_recommend-__page-3',
                 'https://www.jisilu.cn/home/explore/sort_type-add_time__category-__day-0__is_recommend-__page-4',
                 'https://www.jisilu.cn/home/explore/sort_type-add_time__category-__day-0__is_recommend-__page-5',
                 ],

    # path
    'path_senti': '../../database/senti/jisilu',
}
today = str(datetime.now() - timedelta(hours=2))[:10]
before_24h = str(datetime.now() - timedelta(hours=25))[:16]
senti = []

def scrapy_page(soup):
    c_list = soup.find("div", {'class': 'aw-question-list'})
    result_table = []
    if c_list is not None:
        for item in c_list.find_all("div", {'class': 'aw-item'}):
            if item is not None:
                cnt_reply = item.find("span", {'class': (lambda value: value.startswith('aw-question-replay-count'))})
                cnt = cnt_reply.find('em').get_text()

                content = item.find("div", {'class': 'aw-questoin-content'})
                title = content.find('a').get_text()
                link = content.find('a')['href']
                category = content.find('span', {'class': "aw-question-tags"})
                if category is not None:
                    ctgy = category.find('a').get_text()
                else:
                    ctgy = 'NA'
                updated = content.find('span', {'class': "aw-text-color-999"}).get_text().split("•")
                last_reply_dt = updated[-2].strip()
                cnt_viewer = updated[-1].strip().split(' ')[0]
                result_lst = [ctgy, title, link, cnt, cnt_viewer, last_reply_dt]
                result_table.append(result_lst)
    return result_table

if __name__ == '__main__':
    for url in jisilu_dict['url_list']:
        soup = get_soup(url)
        table = scrapy_page(soup)
        senti.append(table)
    print(len(senti))
    if len(senti) > 0:
        df = pd.concat([pd.DataFrame(i, columns=['topic', 'title', 'link', 'reply', 'viewers', 'updated']) for i in senti])
        df['updated'] = pd.to_datetime(df['updated'], format="%Y-%m-%d %H:%M")
        df = df.loc[df['updated'] > before_24h].reset_index(drop=True)
        df.to_csv(os.path.join(jisilu_dict['path_senti'], "{}.txt".format(today)))
        print("wtrited file as of {}".format(today))

















