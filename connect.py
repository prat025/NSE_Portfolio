from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from pyotp import TOTP
import pandas as pd
import datetime as dt

cwd = os.chdir("C:\\Users\\Pratyush\\nse_portfolio")

def autologin():
    token_path = "authentication.txt"
    key_secret = open(token_path,'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options = options.to_capabilities()
    driver = webdriver.Remote(service.service_url, options)
    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    username = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
    time.sleep(10);
    pin = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    totp = TOTP(key_secret[4])
    token = totp.now()
    print(token)
    pin.send_keys(token)
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
    time.sleep(10);
    print(driver.current_url)
    request_token=driver.current_url.split('request_token=')[1][:32]
    with open('request_token.txt', 'w') as the_file:
        the_file.write(request_token)
    driver.quit()

autologin()
#container > div > div > div.login-form > form > div.su-input-group.su-static-label.su-has-icon.twofa-value.digits > input[type=text]


request_token = open("request_token.txt",'r').read()
print(request_token)
key_secret = open("authentication.txt",'r').read().split()
print(key_secret[1])
kite = KiteConnect(api_key=key_secret[0])
data = kite.generate_session(request_token, api_secret=key_secret[1])
print(data)
with open('access_token.txt', 'w') as file:
        file.write(data["access_token"])

instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1

def fetchOHLCExtended(ticker,inception_date, interval):
    """extracts historical data and outputs in the form of dataframe
       inception date string format - dd-mm-yyyy"""
    instrument = instrumentLookup(instrument_df,ticker)
    from_date = dt.datetime.strptime(inception_date, '%d-%m-%Y')
    to_date = dt.date.today()
    data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    while True:
        if from_date.date() >= (dt.date.today() - dt.timedelta(100)):
            data = data.append(pd.DataFrame(kite.historical_data(instrument,from_date,dt.date.today(),interval)),ignore_index=True)
            break
        else:
            to_date = from_date + dt.timedelta(100)
            data = data.append(pd.DataFrame(kite.historical_data(instrument,from_date,to_date,interval)),ignore_index=True)
            from_date = to_date
    data.set_index("date",inplace=True)
    return data


ohlc = fetchOHLCExtended("INFY","01-02-2023","day")
print(ohlc)



