import config
import session_manager

import json
import os
import requests

tradeable_epics = {}

def exploreNode(nodeID):
    global tradeable_epics
    base_url = config.igEnpoint() + '/marketnavigation/' + str(nodeID)
    r = requests.get(base_url, headers=session_manager.getHeaders(1))

    if r.status_code == 200:
        if isinstance(r.json()['nodes'], list):
            a = 0
            for node in r.json()['nodes']:
                print("Exploring: "+str(node['name'] + ", " + str(a) + " out of "+str(len(r.json()['nodes']))))
                exploreNode(node['id'])
                a += 1
        if isinstance(r.json()['markets'], list):
            for market in r.json()['markets']:
                # print("Checking market: "+str(market['instrumentName']))

                DFB_TODAY_DAILY_CHECK = [
                    "DFB" in str(market['epic']),
                    "TODAY" in str(market['epic']),
                    "DAILY" in str(market['epic'])]

                if any(DFB_TODAY_DAILY_CHECK):
                    trade, times = tradeable_epic(market['epic'])
                    if trade:
                        print("trading.... " + str(market['epic']))
                        tradeable_epics[str(market['epic'])] = times
                        print(tradeable_epics)
    else:
        raise Exception(r.text)

def tradeable_epic(epic_id):
    try:
        base_url = config.igEnpoint() + '/markets/' + epic_id
        auth_r = requests.get(
            base_url, headers=session_manager.getHeaders(1))
        d = json.loads(auth_r.text)
        current_bid = d['snapshot']['bid']
        ask_price = d['snapshot']['offer']
        spread = float(current_bid) - float(ask_price)
        if float(spread) >= config.spreadCheck():
            print(
                "!!INFO!!...FOUND GOOD EPIC..., passing to trade function ..." +
                str(epic_id))
            return True, d['instrument']['openingHours']['marketTimes'][0]
        else:
            print(
                "!!INFO!!...skipping, NO GOOD EPIC....Checking next epic spreads...")
            pass
        return False, None
    except Exception as e:
        print("Error for epic: "+str(epic_id))
        print(e)
        pass

if __name__ == "__main__":
    try:
        session_manager.login()
        exploreNode(180500)
    except Exception as e:
        print(e)
    with open(os.path.join(os.path.dirname(__file__), "data/tradeable_epics.json"), "w") as stream:
        json.dump(tradeable_epics, stream)
    session_manager.logout()
else:
    with open(os.path.join(os.path.dirname(__file__), "data/tradeable_epics.json")) as stream:
        tradeable_epics = json.load(stream)