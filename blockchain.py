import datetime
import requests
from dotenv import dotenv_values
config = dotenv_values(".env")


def get_block(date_=""):
    if date_ == "":
        date_ = datetime.date.today()
    url = 'https://deep-index.moralis.io/api/v2/dateToBlock?chain=%s&date=%s' % (config["CHAIN"], date_)

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": config["MORALIS_API_KEY"]
    }
    status_response = requests.request("GET", url, headers=headers)
    data = status_response.json()
    return data['block']


def get_price(address, date_=""):
    if date_ == "":
        latest_block = ""
    else:
        latest_block = "&to_block=%s" % get_block(date_)
    url = 'https://deep-index.moralis.io/api/v2/erc20/%s/price?chain=%s%s' % (address, config["CHAIN"], latest_block)

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": config["MORALIS_API_KEY"]
    }
    status_response = requests.request("GET", url, headers=headers)
    data = status_response.json()
    return data


def native_to_usd_price(native_price, decimals=18, date_=""):
    native_price_request = get_price(config["NATIVE_TOKEN_ADDRESS"], date_=date_)
    native_price_usd = native_price_request["usdPrice"]
    native_price = int(native_price) / (10 ** decimals)
    usd_price = native_price * native_price_usd
    return usd_price


def get_price_x_days_ago(address, days):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    today = datetime.date.today()
    delta = datetime.timedelta(days=days)
    request_date = str(today - delta) + ' ' + now
    return get_price(address, str(request_date))


def get_movement_percent(new_price, old_price):
    return (new_price - old_price) / new_price * 100
