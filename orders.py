import config
import session_manager
import positions
import market_exploration
import trading

import json
import requests
import time

# Constants
orderType_value = "MARKET"
expiry_value = "DFB"
currencyCode_value = "GBP"

def percentage(part, whole):
    return 100 * float(part) / float(whole)

def idTooMuchPositions(key, positionMap):
    if((key in positionMap) and (int(positionMap[key]) >= int(config.maxTrades()))):
        return True
    else:
        return False

def no_trade_window():
    try:
        base_url = config.igEnpoint() + "/accounts"
        r = requests.get(base_url, headers=session_manager.getHeaders(1))

        if r.status_code != 200:
            print("Failed to get account details: "+str(r.status_code))
            raise Exception(r.text)

        d = json.loads(r.text)

        for i in d['accounts']:
            if str(i['accountType']) == "SPREADBET":
                balance = i['balance']['balance']
                deposit = i['balance']['deposit']

        percent_used = percentage(deposit, balance)
        neg_bal_protect = i['balance']['available']

        print("!!INFO!!...Percent of account used ..." + str(percent_used))

        neg_balance_checks = [
            float(percent_used) > float(config.accountMaxUsage()),
            float(neg_bal_protect) < config.lowNegativeMargin()]

        if any(neg_balance_checks):
            print("!!INFO!!...Don't trade, Too much margin used up already")
            return False
        else:
            print("!!INFO!!...OK to trade...")
            return True

    except Exception as e:
        print("!!ERROR!!...No trade window error!!")
        print(e)
        return False

def try_market_order(epic_id, trade_direction, limit, stop_pips, positionMap):

    if trade_direction == "NONE":
        return None

    key = epic_id + '-' + trade_direction
    if idTooMuchPositions(key, positionMap):
        print(str(key) +
              " has position of " +
              str(positionMap[key]) +
              ", hence should not trade")
        return None

    if not no_trade_window():
        return None

    limitDistance_value = str(limit)  # Limit
    stopDistance_value = str(stop_pips)  # Stop

    ##########################################################################
    print(
        "Order will be a " +
        str(trade_direction) +
        " Order, With a limit of: " +
        str(limitDistance_value))
    print(
        "stopDistance_value for " +
        str(epic_id) +
        " will bet set at " +
        str(stopDistance_value))
    ##########################################################################

    # MAKE AN ORDER
    base_url = config.igEnpoint() + '/positions/otc'
    data = {
        "direction": trade_direction,
        "epic": epic_id,
        "limitDistance": limitDistance_value,
        "orderType": orderType_value,
        "size": config.tradeSize(),
        "expiry": expiry_value,
        "guaranteedStop": True,
        "currencyCode": currencyCode_value,
        "forceOpen": True,
        "stopDistance": stopDistance_value}
    r = requests.post(
        base_url,
        data=json.dumps(data),
        headers=session_manager.getHeaders())

    if r.status_code != 200:
        print("Failed to place order: "+str(r.status_code))
        raise Exception(r.text)

    d = json.loads(r.text)
    deal_ref = d['dealReference']
    time.sleep(1)
    # CONFIRM MARKET ORDER
    base_url = config.igEnpoint() + '/confirms/' + deal_ref
    r = requests.get(base_url, headers=session_manager.getHeaders(1))

    if r.status_code != 200:
        print("Failed to confirm order: "+str(r.status_code))
        raise Exception(r.text)

    d = json.loads(r.text)
    print("DEAL ID : " + str(d['dealId']))
    print(d['dealStatus'])
    print(d['reason'])

    if str(d['reason']) != "SUCCESS":
        print("some thing occurred ERROR!!")
        print("!!!INFO!!!...Order failed, Check IG Status, Resuming...")
    else:
        print("!!INFO!!...Yay, ORDER OPEN")

if __name__ == "__main__":
    try:
        session_manager.login()
        pMap = positions.getPositionsSummary()
        for e in market_exploration.tradeable_epics.keys():
            epic, direction, limit, stop = trading.getTradeSignal(e)
            print(str(epic) + " : " + str(direction) + " : " + str(limit) + " : " + str(stop))
            if direction != "NONE":
                if try_market_order(epic, direction, limit, stop, pMap):
                    break
    except Exception as e:
        print(e)