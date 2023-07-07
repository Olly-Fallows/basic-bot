import config
import session_manager

import json
import requests

def getPositionsSummary():
    r = requests.get(
        config.igEnpoint() + "/positions", headers=session_manager.getHeaders())
    print(r.status_code)
    if r.status_code == 200:
        print("Got positions: "+str(r.text))
        position_json = json.loads(r.text)

        positionMap = {}

        for item in position_json['positions']:
            direction = item['position']['direction']
            print(direction)
            dealSize = float(item['position']['size'])
            print(dealSize)
            ccypair = item['market']['epic']
            print(ccypair)
            key = ccypair + '-' + direction
            if (key in positionMap):
                positionMap[key] = dealSize + positionMap[key]
            else:
                positionMap[key] = dealSize
        print('current position summary:')
        print(positionMap)
        return positionMap
    else:
        print("Error with getting positions: "+str(r.status_code))
        raise Exception(r.text)

if __name__ == "__main__":
    try:
        session_manager.login()
        getPositionsSummary()
    except Exception as e:
        print(e)
    # session_manager.logout()