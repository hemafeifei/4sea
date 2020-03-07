#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
import os

PARAM_DICT = {
    # token
    'tu_share_pro': 'af3dc83d1b4698c744b6bdd352829e23f4c5f0a413475cd489100b72',
    # path
    'path_sec': '../../database/finance/sec/'
}

before_1y = datetime.now() - timedelta(days=365)
dt_start = str(datetime.now() - timedelta(days=2920))[:10]
dt_today = str(datetime.now())[:10]
before_1y_str = datetime.strftime(before_1y, format='%Y%m%d')
today_str = datetime.strftime(datetime.now(), format='%Y%m%d')
print("Start = {}, \nEnd = {}".format(dt_start, dt_today))
print("Today is         ", today_str)
print("Before 1 year is ", before_1y_str)


# Part I get data
def get_stock_list():
    '''
    :return: stock info with code, name, area, industry, list_date
    '''
    # config
    token = PARAM_DICT['tu_share_pro']
    ts.set_token(token)
    pro = ts.pro_api()

    # length of stock list
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    print("Original stocks # is ", len(df))
    # filtering with list date, meaning list at least 1 year on the market
    df = df.loc[df['list_date'].apply(int).values <= int(before_1y_str)].reset_index(drop=True)
    print("Stock Listing after 1 year, # is ", len(df))
    # filtering with province and cities
    # df = df.loc[df['area'].isin(['浙江', '江苏', '北京', '广东', '深圳', '上海', '山东', '福建', '湖北', '湖南', '安徽', '重庆', '天津'])].reset_index(drop=True)
    # print("After area filtering, # Stock is ", len(df))

    df_kept = df.rename(columns={'symbol': 'code'})
    df_kept.to_csv(os.path.join(PARAM_DICT['path_sec'], 'rps_stock_info.csv'), index=False)
    print("Updated stock info")
    return df_kept


def get_his_data(code,start='20180101', end='20190319', ktype='W'):
    '''
    :param code: stock code
    :param start: start date 格式YYYY-MM-DD
    :param end: end date 格式YYYY-MM-DD
    :param ktype: 数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
    :return: stock's close price
    '''
    df=ts.get_hist_data(code=code,
                        start=start,
                        end=end,ktype=ktype)
    # return close price
    return df.close


def weekly_price_update(stock_info):
    print("*** Start at ", str(datetime.now())[:16])
    data = pd.DataFrame()
    for i, row in stock_info.iterrows():
        name = row['name']
        code = row['code']
        if i % 500 == 0:
            print("Loops of {}".format(i))
            print(name, code)
        data[name] = get_his_data(code, start=dt_start, end=dt_today, ktype='W')
    print(data.shape)
    print("**** Finished at ", str(datetime.now())[:16])
    data.to_csv(os.path.join(PARAM_DICT['path_sec'], 'rps_stock_price.csv')) # keep date as index
    print("Write Price data, maximal date is {}".format(data.index.max()))
    return data


# Part II Manipulate data
def cal_ret(df, w=1):
    '''w:周5;月20;半年：120; 一年250
    return stock return rate in terms of period, default 1 means weekly
    '''
    df = df / df.shift(-w) - 1
    return df.iloc[:-w, :].fillna(0)


def get_rps_median(ret, df_info):
    tbl = []
    for dt in ret.index:
        effect_dt = datetime.strftime(pd.to_datetime(dt) - timedelta(days=365), format='%Y%m%d')
        effect_name = list(df_info.loc[df_info.list_date.apply(int).values<=int(effect_dt)]['name'])
        rps_med = ret.loc[dt, effect_name].median()
        result = [dt, rps_med]
        tbl.append(result)
    df = pd.DataFrame(tbl, columns=['date','rps_median'])
    return df.sort_values('date').set_index('date')


def weekly_rps_update(price_data, stock_info):
    return_60 = cal_ret(price_data, w=12)
    return_120 = cal_ret(price_data, w=24)
    return_250 = cal_ret(price_data, w=50)
    return_120.to_csv(os.path.join(PARAM_DICT['path_sec'], 'rps_stock_return.txt')) # index=date

    rps_med_60 = get_rps_median(return_60, stock_info).rename(columns={'rps_median': 'return_med_60d'})
    rps_med_120 = get_rps_median(return_120, stock_info).rename(columns={'rps_median': 'return_med_120d'})
    rps_med_250 = get_rps_median(return_250, stock_info).rename(columns={'rps_median': 'return_med_250d'})
    print(rps_med_60.shape)
    print(rps_med_120.shape)
    print(rps_med_250.shape)
    # filtering to ensure they have some date periods
    rps_med_60 = rps_med_60.loc[rps_med_60.index.isin(rps_med_250.index)]
    rps_med_120 = rps_med_120.loc[rps_med_120.index.isin(rps_med_250.index)]

    rps_final = pd.concat([rps_med_60, rps_med_120, rps_med_250], axis=1) # concatat along the columns
    print(rps_final.shape)
    rps_final.to_csv(os.path.join(PARAM_DICT['path_sec'], 'rps_stock_chg_median.txt'))
    print("Wtire Return rate median data.")


if __name__ == '__main__':
    stock_info = get_stock_list()
    print(' ')
    stock_price = weekly_price_update(stock_info) # main function of Part I
    print(' ')
    weekly_rps_update(stock_price, stock_info)

