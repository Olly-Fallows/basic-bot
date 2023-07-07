import config
import session_manager
import market_exploration

import json
import requests
import numpy
from scipy import stats
from statsmodels import robust

def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)

def percentage_of(percent, whole):
    # percent should always be 20 for stocks
    # ESMA regulations calculating min stop loss (20% for stocks)
    return (percent * whole) / 100.0

def calculate_stop_loss(d):
    price_ranges = []
    closing_prices = []
    first_time_round_loop = True
    TR_prices = []
    price_compare = "bid"

    for i in d['prices']:
        if first_time_round_loop:
            ###########################################
            # First time round loop cannot get previous
            ###########################################
            closePrice = i['closePrice'][price_compare]
            closing_prices.append(closePrice)
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            price_range = float(high_price - closePrice)
            price_ranges.append(price_range)
            first_time_round_loop = False
        else:
            prev_close = closing_prices[-1]
            ###########################################
            closePrice = i['closePrice'][price_compare]
            closing_prices.append(closePrice)
            high_price = i['highPrice'][price_compare]
            low_price = i['lowPrice'][price_compare]
            price_range = float(high_price - closePrice)
            price_ranges.append(price_range)
            TR = max(high_price - low_price,
                     abs(high_price - prev_close),
                     abs(low_price - prev_close))
            TR_prices.append(TR)

    return str(int(float(max(TR_prices))))

def Chandelier_Exit_formula(TRADE_DIR, ATR, Price):
    # Chandelier Exit (long) = 22-day High - ATR(22) x 3
    # Chandelier Exit (short) = 22-day Low + ATR(22) x 3
    if TRADE_DIR == "BUY":
        return float(Price) - float(ATR) * int(config.ceMultiplier())
    elif TRADE_DIR == "SELL":
        return float(Price) + float(ATR) * int(config.ceMultiplier())


def getTradeSignal(epic_id):
    try:
        base_url = config.igEnpoint() + '/markets/' + epic_id
        r = requests.get(
            base_url, headers=session_manager.getHeaders())

        if r.status_code != 200:
            print("Failed ot get market info: "+r.status_code)
            raise Exception(r.text)

        d = json.loads(r.text)

        if d['snapshot']['marketStatus'] != "TRADEABLE":
            print(epic_id + " Currently not tradeable")
            return epic_id, "NONE", 0, 0

        current_bid = d['snapshot']['bid']

        base_url = config.igEnpoint() + "/prices/" + epic_id + "/WEEK/18"
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5,
        # MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3,
        # HOUR_4, DAY, WEEK, MONTH)
        r = requests.get(base_url, headers=session_manager.getHeaders())

        if r.status_code != 200:
            print("Failed get prices with: "+str(r.status_code))
            raise Exception(r.text)

        d = json.loads(r.text)

        remaining_allowance = d['allowance']['remainingAllowance']
        reset_time = humanize_time(
            int(d['allowance']['allowanceExpiry']))
        print("Remaining API Calls left: " + str(remaining_allowance))
        print("Time to API Key reset: " + str(reset_time))

        ATR = calculate_stop_loss(d)
        high_prices = []
        low_prices = []

        for i in d['prices']:

            if i['highPrice']['bid'] is not None:
                highPrice = i['highPrice']['bid']
                high_prices.append(highPrice)
            ########################################
            if i['lowPrice']['bid'] is not None:
                lowPrice = i['lowPrice']['bid']
                low_prices.append(lowPrice)

        low_prices = numpy.ma.asarray(low_prices)
        high_prices = numpy.ma.asarray(high_prices)

        xi = numpy.arange(0, len(low_prices))

        low_prices_slope, low_prices_intercept, low_prices_lo_slope, low_prices_hi_slope = stats.mstats.theilslopes(
            low_prices, xi, 0.99)
        high_prices_slope, high_prices_intercept, high_prices_lo_slope, high_prices_hi_slope = stats.mstats.theilslopes(
            high_prices, xi, 0.99)

        # # HIGH (IQR)
        # var_upper = float(high_prices_intercept +
        # (abs(stats.iqr(high_prices, nan_policy='omit') * 2)))
        # # LOW (IQR)
        # var_lower = float(low_prices_intercept -
        # (abs(stats.iqr(low_prices, nan_policy='omit') * 2)))

        # HIGH (MAD)
        var_upper = float(
            high_prices_intercept + (abs(robust.mad(high_prices) * 3)))
        # LOW (MAD)
        var_lower = float(low_prices_intercept -
                          (abs(robust.mad(low_prices) * 3)))

        if float(current_bid) > float(var_upper):
            trade_direction = "BUY"
        elif float(current_bid) < float(var_lower):
            trade_direction = "SELL"
        else:
            pip_limit = 9999999  # Junk Data
            stop_pips = "999999"  # Junk Data
            trade_direction = "NONE"

        if trade_direction == "BUY":
            pip_limit = int(abs(float(max(high_prices)) -
                                float(current_bid)) * config.profitIndicatorMultiplier())
            ce_stop = Chandelier_Exit_formula(
                trade_direction, ATR, min(low_prices))
            stop_pips = str(int(abs(float(current_bid) - (ce_stop))))
            print("!!INFO!!...BUY!!")
            print(str(epic_id))
            print(
                "!!INFO!!...Take Profit@...." +
                str(pip_limit) +
                " pips")
        elif trade_direction == "SELL":
            pip_limit = int(abs(float(min(low_prices)) -
                                float(current_bid)) * config.profitIndicatorMultiplier())
            ce_stop = Chandelier_Exit_formula(
                trade_direction, ATR, max(high_prices))
            stop_pips = str(int(abs(float(current_bid) - (ce_stop))))
            print("!!INFO!!...SELL!!")
            print(str(epic_id))
            print(
                "!!INFO!!...Take Profit@...." +
                str(pip_limit) +
                " pips")

        esma_new_margin_req = int(
            percentage_of(
                config.esnaMargin(),
                current_bid))

        if int(esma_new_margin_req) > int(stop_pips):
            stop_pips = int(esma_new_margin_req)
        if int(pip_limit) == 0:
            trade_direction = "NONE"
        if int(pip_limit) == 1:
            trade_direction = "NONE"
        if int(pip_limit) >= int(config.greedIndicator()):
            pip_limit = int(config.greedIndicator() - 1)
        if int(stop_pips) > int(config.tooHighMargin()):
            trade_direction = "NONE"

        return epic_id, trade_direction, pip_limit, stop_pips

    except Exception as e:
        print(e)
        return "", "NONE", 0, 0

if __name__ == "__main__":
    session_manager.login()
    if market_exploration.tradeable_epics != {}:
        print(market_exploration.tradeable_epics)
        for e in market_exploration.tradeable_epics.keys():
            print("Checking: "+str(e))
            print(getTradeSignal(e))