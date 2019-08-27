#!/usr/bin/python3

from datetime import datetime
import logging
from urllib.request import urlopen
import locale
from bs4 import BeautifulSoup
import pandas as pd

def StockList():
    path='./wilshire5000.txt'
    ticker_list_raw = open(path, 'r')
    ticker_list_lst = ticker_list_raw.readlines()
    ticker_list_raw.close
    final_lst = list(map(str.strip, ticker_list_lst))
    return final_lst

def DeadTickers():
    path='./deadtickers.txt'
    dead_tickers_raw = open(path, 'r')
    dead_tickers_lst = dead_tickers_raw.readlines()
    dead_tickers_raw.close
    dead_tickers_final = list(map(str.strip, dead_tickers_lst))
    return dead_tickers_final

def ReportDeadTicker(ticker):
    path = './deadtickers.txt'
    dead_tickers_raw = open(path, 'a+')
    dead_tickers_raw.write(ticker + '\r\n')
    dead_tickers_raw.close
    logging.info(f"{item} Reported as dead ticker")

def DoSomeSoupage(html):
    soup = BeautifulSoup(html, "html5lib")
    filtered = soup.find('span', {'data-reactid' : '44'})
    try:
        Volume = locale.atoi(filtered.text)
    except:
        Volume = "Error"
    filtered = soup.find('span', {'data-reactid' : '14'})
    try:
        ClosePrice = locale.atof(filtered.text)
    except:
        ClosePrice = "Error"
    return (ClosePrice, Volume)

def UnPickle(ticker):
    return pd.read_pickle('./pickle/' + ticker + '.pkl')

if __name__ == '__main__':
    start_time = datetime.now()
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    logging.basicConfig(level=logging.INFO, filename='LogFile.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
    logging.info('Start Time: ' + start_time.strftime("%m/%d/%Y, %H:%M:%S"))
    curr_date=(datetime.today().date())
    dead_tickers_lst = DeadTickers()
    Stk_Sucess_Cnt = 0
    for item in StockList():
        if item in dead_tickers_lst:
            continue
        try:
            masterdf = UnPickle(item)
            if curr_date in masterdf.index:
                print (f"{item} - Date already in index")
                continue
        except:
            pass

        try:
            url = 'https://finance.yahoo.com/quote/' + item + '?p=' + item
            f = urlopen(url)
            g=f.read()
            CloseVolume = DoSomeSoupage(g)
            Stk_Sucess_Cnt = Stk_Sucess_Cnt + 1
        except:
            print(f"{item} Error")
            continue
        if CloseVolume[0] == "Error" or CloseVolume[1] == "Error":
            ReportDeadTicker(item)
            continue
        df = pd.DataFrame(columns=['Close','Volume'], index=[curr_date])
        df.loc[curr_date] = pd.Series({'Close':CloseVolume[0],
                                       'Volume':CloseVolume[1]})
        try:
            masterdf = UnPickle(item)
            masterdf_new = masterdf.append(df)
            masterdf_new.to_pickle('./pickle/' + item + '.pkl')
        except:
            df.to_pickle('./pickle/' + item + '.pkl')
        print(f"{item}: {CloseVolume[0]}: {CloseVolume[1]}")
#All pulling of stock information is done at this point
    logging.info('Sucessfully Stocks: ' + str(Stk_Sucess_Cnt))
    end_time = datetime.now()
    logging.info('End Time: ' + end_time.strftime("%m/%d/%Y, %H:%M:%S"))

