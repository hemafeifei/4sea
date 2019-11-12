# -*- coding: utf-8 -*-

from _settings import *
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import re

bloombg_dict = {
    # function 1
    'url_dax30': 'https://www.investing.com/indices/germany-30-historical-data',
    'url_sp500': 'https://www.investing.com/indices/us-spx-500-historical-data',
    'url_hsi': 'https://www.investing.com/indices/hang-sen-40-historical-data',
    'url_shanghai': 'https://www.investing.com/indices/shanghai-composite-historical-data',
    'url_gold': 'https://www.investing.com/commodities/gold-historical-data',
    # function 2
    'url_oil': 'https://www.investing.com/commodities/brent-oil-historical-data',
    # function 3
    'url_fx_usd_jpy': 'https://cn.investing.com/currencies/usd-jpy-historical-data',
    'url_fx_gbp_jpy': 'https://cn.investing.com/currencies/gbp-jpy-historical-data',
    # path
    'path_idx': '../../database/finance/idx/',
    'path_fx': '../../database/finance/fx/',
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
    try:
        df['date'] = pd.to_datetime(df['date'], format="%b%d%Y")
    except:
        df['date'] = pd.to_datetime(df['date'], format="%Y年%m月%d日") # As my server locates in CN, if not, use %Y-%m-%d
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
    try:
        df['date'] = pd.to_datetime(df['date'], format="%b%d%Y")
    except:
        df['date'] = pd.to_datetime(df['date'], format="%Y年%m月%d日") # As my server locates in CN, if not, use %Y-%m-%d
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
    try:
        df['date'] = pd.to_datetime(df['date'], format="%b%d%Y")
    except:
        df['date'] = pd.to_datetime(df['date'], format="%Y年%m月%d日") # As my server locates in CN, if not, use %Y-%m-%d
    print("Max date:", df['date'].max())
    return df


# Function of updating and merging data
def update_and_concat_data(his_data, new_data, out_path, out_file):
    '''
    :param his_data: historical data
    :param new_data: newly updated data
    :param out_file: output file name
    :return: None
    '''
    to_update = new_data.loc[new_data.date > his_data['date'].max()]
    if len(to_update) > 0:
        print("Update {}".format(out_file))
        df_concat = pd.concat([his_data, to_update], ignore_index=True)
        df_concat = df_concat.sort_values('date').reset_index(drop=True)
        print(df_concat.tail(2))

        out_file_path = os.path.join(out_path, out_file)
        df_concat.to_csv(out_file_path, index=False)
        print(' ')


def main_control():
    # Part 0: Path check
    # print first 5 file under the path
    print("****Start {}****".format(str(datetime.now())[:16]))
    print(os.listdir(bloombg_dict['path_idx'])[:5])
    # print(os.listdir(bloombg_dict['path_fx'])[:5])

    # Part 1: Parse data
    upd_dax30 = parse_index_data_1(bloombg_dict['url_dax30'])
    upd_sp500 = parse_index_data_1(bloombg_dict['url_sp500'])
    upd_hsi = parse_index_data_1(bloombg_dict['url_hsi'])
    upd_shanghai = parse_index_data_1(bloombg_dict['url_shanghai'])
    upd_gold = parse_index_data_1(bloombg_dict['url_gold'])
    upd_oil = parse_index_data_2(bloombg_dict['url_oil'])
    upd_fx_usd_jpy = parse_index_data_3(bloombg_dict['url_fx_usd_jpy'])
    upd_fx_gbp_jpy = parse_index_data_3(bloombg_dict['url_fx_gbp_jpy'])

    # Part 2: Check historical data
    # check Global Index
    his_dax30 = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_dax30_his.txt'), parse_dates=[0],
                            index_col=False)
    his_sp500 = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_sp500_his.txt'), parse_dates=[0],
                            index_col=False)
    his_hsi = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_hsi_his.txt'), parse_dates=[0], index_col=False)
    his_shanghai = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_shanghai_his.txt'), parse_dates=[0],
                               index_col=False)
    his_gold = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_gold_his.txt'), parse_dates=[0], index_col=False)
    his_oil = pd.read_csv(os.path.join(bloombg_dict['path_idx'], 'idx_oil_his.txt'), parse_dates=[0], index_col=False)
    # Check fx
    his_fx_usd_jpy = pd.read_csv(os.path.join(bloombg_dict['path_fx'], 'fx_usd_jpy.txt'), parse_dates=[0],
                                 index_col=False)
    his_fx_gbp_jpy = pd.read_csv(os.path.join(bloombg_dict['path_fx'], 'fx_gbp_jpy.txt'), parse_dates=[0],
                                 index_col=False)

    # Part 3: Check and concat newly updated data
    update_and_concat_data(his_dax30, upd_dax30, bloombg_dict['path_idx'], 'idx_dax30_his.txt')
    update_and_concat_data(his_sp500, upd_sp500, bloombg_dict['path_idx'], 'idx_sp500_his.txt')
    update_and_concat_data(his_hsi, upd_hsi, bloombg_dict['path_idx'], 'idx_hsi_his.txt')
    update_and_concat_data(his_shanghai, upd_shanghai, bloombg_dict['path_idx'], 'idx_shanghai_his.txt')
    update_and_concat_data(his_gold, upd_gold, bloombg_dict['path_idx'], 'idx_gold_his.txt')
    update_and_concat_data(his_oil, upd_oil, bloombg_dict['path_idx'], 'idx_oil_his.txt')
    update_and_concat_data(his_fx_usd_jpy, upd_fx_usd_jpy, bloombg_dict['path_fx'], 'fx_usd_jpy.txt')
    update_and_concat_data(his_fx_gbp_jpy, upd_fx_gbp_jpy, bloombg_dict['path_fx'], 'fx_gbp_jpy.txt')

    print("****Finished {}****".format(str(datetime.now())[:16]))


if __name__ == '__main__':
    main_control()
