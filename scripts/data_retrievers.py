import datetime
import json
import os
import time

import pandas as pd
import pandas_datareader as web_data_reader

import requests


from bs4 import BeautifulSoup



def download_stocks_to_files(stocks, start_date, end_date, folder=None, number_of_attempts=None):
    if not number_of_attempts:
        number_of_attempts = 3
    if not folder:
        folder = r'../data/stock'

    for s in stocks:
        for attempt in range(number_of_attempts):
            try:
                df = web_data_reader.DataReader(s, 'yahoo', start_date, end_date)
                df.to_hdf(os.path.join(folder,
                                       '{}_{}_{}.h5'.format(s, start_date.strftime('%Y-%m-%d'),
                                                            end_date.strftime('%Y-%m-%d'))),
                          'key_to_store', table=True, mode='w')
                print('Attempt {} was successful for {}.'.format(attempt, s))
            except:
                time.sleep(10)
                print('Attempt {} was failed for {}. Retrying...'.format(attempt, s))
                continue

            break


def load_stock_to_data_frame(stock, start_date, end_date, folder=None):
    if not folder:
        folder = r'../data/stock'

    try:
        df = pd.read_hdf(os.path.join(r'../data/stock',
                                      '{}_{}_{}.h5'.format(stock, start_date.strftime('%Y-%m-%d'),
                                                           end_date.strftime('%Y-%m-%d'))),
                         'key_to_store')
    except:
        # later add stuff for missing file, download etc...
        pass

    return df


def download_crypto_currency_list(url="https://www.cryptocompare.com/api/data/coinlist/"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    downloaded_data = json.loads(soup.prettify())

    return downloaded_data['Data']


def download_crypto_currency_market_data(url="https://api.coinmarketcap.com/v1/ticker/"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    list_of_dict = json.loads(soup.prettify())

    df = pd.DataFrame([[r[c] for c in ['symbol', 'market_cap_usd', 'price_usd']] for r in list_of_dict],
                      columns=['Ticker', 'MarketCap', 'Price'])

    # for i in range(len(list_of_dict)):
    #     df.loc[len(df)] = [list_of_dict[i]['symbol'], list_of_dict[i]['market_cap_usd']]

    df.sort_values(by=['MarketCap'])
    # apply conversion to numeric as 'df' contains lots of 'None' string as values
    df.MarketCap = pd.to_numeric(df.MarketCap)

    return df


def timestamp2date(timestamp):
    # function converts a Unix timestamp into Gregorian date
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')


def date2timestamp(date):
    # function coverts Gregorian date in a given format to timestamp
    return datetime.datetime.strptime(date_today, '%Y-%m-%d').timestamp()


def fetchCryptoOHLC(fsym, tsym):
    import numpy as np
    # function fetches a crypto price-series for fsym/tsym and stores
    # it in pandas DataFrame

    cols = ['date', 'timestamp', 'Open', 'High', 'Low', 'Close']
    lst = ['time', 'open', 'high', 'low', 'close']

    timestamp_today = datetime.datetime.today().timestamp()
    curr_timestamp = timestamp_today

    for j in range(2):
        df = pd.DataFrame(columns=cols)
        url = "https://min-api.cryptocompare.com/data/histoday?fsym=" + fsym + "&tsym=" + tsym + "&toTs=" + str(int(curr_timestamp)) + "&limit=2000"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        dic = json.loads(soup.prettify())
        for i in range(1, 2001):
            tmp = []
            for e in enumerate(lst):
                x = e[0]
                y = dic['Data'][i][e[1]]
                if (x == 0):
                    tmp.append(str(timestamp2date(y)))
                tmp.append(y)
            if (np.sum(tmp[-4::]) > 0):
                df.loc[len(df)] = np.array(tmp)
        df.index = pd.to_datetime(df.date)
        df.drop('date', axis=1, inplace=True)
        curr_timestamp = int(df.ix[0][0])
        if (j == 0):
            df0 = df.copy()
        else:
            data = pd.concat([df, df0], axis=0)

    return data

