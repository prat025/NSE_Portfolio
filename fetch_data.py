from kiteconnect import KiteConnect
import logging
import os
import datetime as dt
import pandas as pd

cwd = os.chdir("C:\\Users\\Pratyush\\nse_portfolio")
access_token = open("access_token.txt",'r').read()
key_secret = open("authentication.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

instrument_dump = kite.instruments("NFO")
instrument_df = pd.DataFrame(instrument_dump)
fut_df=instrument_df[instrument_df.strike==14000]

def instrumentLookup(instrument_df,name):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.name==name].instrument_token.values
    except:
        return -1


def fetchOHLC(name,inception_date,interval):
    """extracts historical data and outputs in the form of dataframe"""
    from_date = dt.datetime.strptime(inception_date, '%d-%m-%Y')
    to_date = dt.date.today()
    data = pd.DataFrame(columns=['date','open', 'high', 'low', 'close', 'volume'])
    instrument = instrumentLookup(instrument_df,name)
    for token in instrument:
        while True:
            if from_date.date() >= (dt.date.today() - dt.timedelta(100)):
                fetched_data=kite.historical_data(token,from_date,dt.date.today(),interval)
                data = data.append((fetched_data),ignore_index=True)
                break
            else:
                to_date = from_date + dt.timedelta(100)
                fetched_data=kite.historical_data(token,from_date,dt.date.today(),interval)
                data = data.append((fetched_data),ignore_index=True)
                from_date = to_date
        data.to_pickle("./options_data"+"/"+str(token)+".pkl")
    data.set_index("date",inplace=True)
    return data

fetchOHLC("NIFTY","10-02-2023","5minute")