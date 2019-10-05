from settings import *
import pandas as pd
from datetime import datetime, timedelta
import os

url = 'https://danjuanapp.com/djmodule/value-center?channel=1300100141'
today = str(datetime.now())[:10]
etf_path = '/home/centos/PythonApp/database/finance/etf/'
etf_fn = 'xq_' + today + '.txt'

soup_xq = get_soup(url)

def parse_etf_data(soup):
    """
    
    :param soup: Beatifulsoup result of xueqiu's daily result
    :return: result_table
    """
    soup = soup_xq
    table = soup.find("div", {'class': 'out-row'})
    name = table.find_all('a', {'class': (lambda value: value.startswith('name'))})
    print("Name length", len(name))
    dinfo = table.find_all('a', {'class': (lambda value: value.startswith('row'))})
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
            print("write files append")
            print("****" * 5)


if today in soup_xq.find("title").get_text():
    parse_etf_data(soup_xq)
else:
    print("No updates found on {}".format(today))




