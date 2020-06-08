import json
import requests
from datetime import datetime, timedelta
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as account

TOKEN = "b7763654ef81a5fa90c7f1aae2bfcb12-10f24e383660aab1f10696258a9e3d1f"
ACCOUNT_ID = "101-001-15011208-001"

HEADERS = {
    'Authorization' : 'Bearer ' + TOKEN,
}

ENDPOINT = "https://api-fxtrade.oanda.com"
PRICES_URL = ""
ACCOUNT_URL = ENDPOINT + "/v3/accounts/" + ACCOUNT_ID + "/summary"
ORDERS_URL = ENDPOINT + "/v3/accounts/" + ACCOUNT_ID + "/orders"

api = oandapyV20.API(access_token=TOKEN)

# calculates average daily range
# @param time_period: range of time in days
def ADR(base, quote, time_period):
    base = base.upper()
    quote = quote.upper()
    instrumentName = base + "_" + quote
    end = datetime.now()
    start = str((end - timedelta(days=time_period))).replace(" ", "T") + "Z"
    end = str(end).replace(" ", "T") + "Z"
    params = {
        "granularity": "D",
        "from": start,
        "to": end,
        "price": 'M'
    }
    req = instruments.InstrumentsCandles(instrument=instrumentName, params=params)
    data = api.request(req)
    candles = data['candles']
    total_change, high_change, low_change = 0, 0, 0
    today = candles[len(candles)-1]
    todays_open = float(today['mid']['o'])
    for candle in candles:
        high = float(candle['mid']['h'])
        low = float(candle['mid']['l'])
        open = float(candle['mid']['o'])
        total_change += (high-low)/open
        high_change += (high-open)/open
        low_change += (open-low)/open

    avg_daily_range = float(total_change/time_period)
    avg_high_range = float(high_change/time_period)
    avg_low_range = float(low_change/time_period)
    avgs = {
        'avg_daily_range': avg_daily_range,
        'avg_high': avg_high_range,
        'avg_low': avg_low_range,
        'recent_open': todays_open
    }
    return avgs
    # get candlesticks
    # calc daily ranges
    # calc avg daily range


def GET_CURRENT_PRICE(instrument):
    #time = datetime.now()
    #time = str(time).replace(" ", "T") + "Z"
    params = {
        "granularity": "S5",
        #"from": time,
        #"to": time,
        "price": 'M',
        "count": 1
    }
    req = instruments.InstrumentsCandles(instrument=instrument, params=params)
    data = api.request(req)
    price = data['candles'][0]['mid']['o']
    return float(price)


def GET_ACCOUNT_SUMMARY():
    req = account.AccountSummary(accountID=ACCOUNT_ID)
    summary = api.request(req)
    return summary


def CURRENTLY_OWNED(instrument):
    req = account.AccountDetails(accountID=ACCOUNT_ID)
    details = api.request(req)['account']
    for position in details['positions']:
        if position['instrument'] == instrument:
            return True
    return False


# places a market buy order for @units units of @instrument at price @buy
# places a stop loss at price @sell
def PLACE_LIMIT_ORDER(instrument, units, buy, sell):
    params = {
        "order": {
            "type": 'LIMIT',
            "instrument": instrument,
            "units": units,
            "price": str(buy),
            "takeProfitOnFill": {
                "timeInForce": 'GTC',
                "price": str(sell),
            },
            "timeInForce": 'GTC',
            "positionFill": 'DEFAULT',
            "triggerCondition": 'DEFAULT'
        }
     }
    req = orders.OrderCreate(accountID=ACCOUNT_ID, data=params)
    api.request(req)
    print("-----Order placed-----\n" + str(units) + " units of " + str(instrument) + "\n" + "Buy: " + str(buy) + "\n" + "Sell: " + str(sell) + "\n")




