import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import os
# from pyvirtualdisplay import Display
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_path = '/home/centos/football/chromedriver'
# chrome_path = '/Users/weizheng/PycharmProjects/tickets/chromedriver'

df_name = pd.read_csv('league_name.txt', encoding='utf8')
base_url = 'http://score.nowscore.com/index.aspx'
base_url_007 = 'http://live.win007.com/'
base_url_en = 'http://www.nowgoal.com/'
today = str(datetime.now())
today_utc0 = str(datetime.now() - timedelta(hours=8))

def get_soup(url):
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    driver.quit()
    display.stop()
    return soup


def get_match_007(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'id': (lambda value: value and value.startswith("tr1_"))}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(mlist[4])
        match.append(mlist[6])
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype','tm_utc08', 'home', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(tomorrow)[:10] if df['tm_utc08'][i] <= '06:00' else now[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date']  + ' ' + df['tm_utc08']
    df = df[['mtype', 'dt_utc08', 'home', 'away', 'href_nsc']]
    print(df.shape)
    if lty==True:
        df = df.loc[df.mtype.isin(df_name['league_007'])].reset_index(drop=True)
    else:
        df = df
    return df


def get_match_en(url, lty=True):
    soup = get_soup(url)
    match_f = []
    for e in soup.find_all('tr', {'class': ['', 'b2']}):
        mlist = [td.get_text() for td in e.find_all('td')]
        match = []
        match.append(mlist[1])
        match.append(mlist[2])
        match.append(str.lstrip(mlist[4]))
        match.append(str.rstrip(mlist[6]))
        match.append(e['id'].split('_')[-1])
        match_f.append(match)

    now = str(datetime.today())
    tomorrow = pd.to_datetime(now[:10], format='%Y-%m-%d') + timedelta(days=1)
    df = pd.DataFrame(match_f, columns=['mtype','tm_utc08', 'home', 'away', 'href_nsc'])
    df = df.loc[(df.tm_utc08 >= '12:00') | (df.tm_utc08 < '06:00')].reset_index(drop=True)
    df['date'] = [str(tomorrow)[:10] if df['tm_utc08'][i] <= '06:00' else now[:10] for i in range(len(df))]
    #     df['date'] = now[:10]
    df['dt_utc08'] = df['date'] + ' ' + df['tm_utc08']
    df = df[['mtype', 'dt_utc08', 'home', 'away', 'href_nsc']]
    if lty==True:
        df = df.loc[df.mtype.isin(df_name['league'])].reset_index(drop=True)
    else:
        df = df
    return df




def get_trend(ref):
    now = str(datetime.now())
    odd_start = datetime.now() - timedelta(hours=12)
    trend_url = 'http://data.nowgoal.com/3in1odds/14_' + str(ref) +'.html' # nowgoal
    soup = get_soup(trend_url)

    asian = []
    e0 = soup.find_all('table', {'class': 'gts'})[1]
    for tr in e0.find_all('tr')[2:14]: # nowgoal:2, nsc:1
        asian.append([td.get_text() for td in tr.find_all('td')])

    if len(asian) > 0:
        df_asian = pd.DataFrame(asian, columns=['na1', 'na2', 'home',
                                                'pankou', 'away', 'dt', 'others']).loc[:, 'home':]
        df_asian.dt = [(now[:5] + df_asian.loc[i, 'dt'][-11:]) for i in range(len(df_asian))]
        df_asian = df_asian.sort_values(by='dt').reset_index(drop=True)
        df_asian = df_asian.loc[df_asian.dt >= str(odd_start)[:16]]
        df_asian.dt = pd.to_datetime(df_asian.dt, format='%Y-%m-%d %H:%M')
    else:
        df_asian = pd.DataFrame(asian, columns=['home', 'pankou', 'away', 'dt', 'others'])


    odds = []
    e2 = soup.find_all('table', {'class': 'gts'})[0] # nowgoal
    for tr in e2.find_all('tr')[2:14]: # nsc
        odds.append([td.get_text() for td in tr.find_all('td')])
    if len(odds) > 0:
        df_odds = pd.DataFrame(odds, columns=['na1', 'na2', 'home',
                                              'draw', 'away', 'dt', 'others']).loc[:, 'home':]
        df_odds.dt = [(now[:5] + df_odds.loc[i, 'dt'][-11:] ) for i in range(len(df_odds))]
        df_odds = df_odds.loc[df_odds.dt >= str(odd_start)[:16]]
        df_odds.dt = pd.to_datetime(df_odds.dt, format='%Y-%m-%d %H:%M')
        df_odds = df_odds.sort_values(by='dt').reset_index(drop=True)
        # df_odds['title'] = title
    else:
        df_odds = pd.DataFrame(columns=['home','draw', 'away', 'dt', 'others'])

    return df_odds, df_asian



cur_path = os.getcwd()
os.chdir('..')
cur_path = os.getcwd()
my_path = cur_path + '/data/'
match_pth = my_path + '/match_data/'
odds_path = my_path + '/odds_data/'
match_file = today_utc0[:10] + '.txt'
match_file_en = today_utc0[:10]  + '_en.txt'

if not os.path.exists(match_pth + match_file_en):
    df = get_match_007(base_url_007)
    df['lang'] = 'zh_cn'
    df.to_csv(match_pth + match_file, index=False, encoding='utf-8')
    print("generated file: " ,match_file )
    df_en = get_match_en(base_url_en)
    df_en['lang'] = 'en'
    df_en.to_csv(match_pth + match_file_en, index=False)
    print("generated file: " ,match_file_en )

else:
    df = pd.read_csv(match_pth + match_file)
    df_en = pd.read_csv(match_pth + match_file_en)

today_utc0_path = odds_path+ today_utc0[:10]
if not os.path.exists(today_utc0_path):
    os.makedirs(today_utc0_path)
    print("makedirs for today's odds")


now = today[:16]
print("Start Time is ",str(now)[:16])
for i in range(len(df)):
    if df.loc[i, 'dt_utc08'] >= now:
        href = df.loc[i, 'href_nsc']
        print("odds of ", href)
        df_eu, df_asia =  get_trend(href)
        df_eu.to_csv(today_utc0_path + '/' + str(href) + '_eu.txt', index=False, encoding='utf-8')
        df_asia.to_csv(today_utc0_path+ '/' + str(href) + '_asia.txt', index=False, encoding='utf-8')
        time.sleep(0.8)

end = str(datetime.now())[:16]
print("End Time is ", end)
