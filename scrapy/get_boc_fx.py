from settings import *
import pandas as pd
from datetime import datetime, timedelta
import os


url = 'http://www.boc.cn/sourcedb/whpj/index.html'
today = str(datetime.now())[:10]
fx_path = '/home/centos/PythonApp/database/finance/fx/'
fx_fn = 'fx_' + today + '.txt'

def get_fx(url):
    soup = get_soup(url)
    odd_table = soup.find_all('table')[-3]
    table = []
    for tr in odd_table.find_all('tr')[1:]:
        row = tr.get_text().split('\n')
        table.append(row)

    df = pd.DataFrame(table, columns=['N0', 'name', 'current_buy', 'cash_buy', 'current_sell', 'cash_sell',
                                'boc_price', 'date', 'time', 'N99'])
    df = df.drop(['N0', 'N99'], axis=1)
    df = df.loc[df.name.isin(['澳大利亚元', '加拿大元', '瑞士法郎', '欧元', '英镑', '港币', '日元', '韩国元',
                              '新加坡元', '泰国铢', '土耳其里拉', '美元', '南非兰特'])].reset_index(drop=True)
    return df


fx_data = get_fx(url)
if fx_data['date'][0] == today:
    if not os.path.exists(os.path.join(fx_path, fx_fn)):
        print(today, "Update")
        print("****"*5)
        fx_data.to_csv(os.path.join(fx_path, fx_fn), index=False, encoding='utf8')
    else:
        print('Breake - file existes')
        print("====" * 5)
else:
    print('Break - not today')
    print(today)
    print(fx_data.shape)
    print(fx_data['date'][0])
    print("====" * 5)
