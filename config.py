import json
import os

config = None

with open(os.path.join(os.path.dirname(__file__), "resources/config.json")) as stream:
    config = json.load(stream)

def avKey():
    return config["alpha_vantage"]["key"]

def igDemo():
    return config["ig"]["is_demo"]
def igKey():
    if igDemo():
        return config["ig"]["demo"]["key"]
    else:
        return config["ig"]["live"]["key"]
def igUname():
    if igDemo():
        return config["ig"]["demo"]["uname"]
    else:
        return config["ig"]["live"]["uname"]
def igPword():
    if igDemo():
        return config["ig"]["demo"]["pword"]
    else:
        return config["ig"]["live"]["pword"]
def igAccount():
    if igDemo():
        return config["ig"]["demo"]["account_id"]
    else:
        return config["ig"]["live"]["account_id"]

def igEnpoint():
    if igDemo():
        return "https://demo-api.ig.com/gateway/deal"
    else:
        return "https://api.ig.com/gateway/deal"


def spreadCheck():
    return config["algorithm"]["spread_check"]
def ceMultiplier():
    return config["algorithm"]["chandelier_exit_multiplier"]
def profitIndicatorMultiplier():
    return config["algorithm"]["profit_multiplier"]
def esnaMargin():
    return config["algorithm"]["ESNA_new_margin"]
def tooHighMargin():
    return config["algorithm"]["too_high_margin"]
def greedIndicator():
    return config["algorithm"]["greed_indicator"]
def maxTrades():
    return config["algorithm"]["max_trades"]
def accountMaxUsage():
    return config["algorithm"]["account_max_usage"]
def lowNegativeMargin():
    return config["algorithm"]["neg_margin"]
def tradeSize():
    return config["algorithm"]["trade_size"]