import session_manager
import market_exploration
import trading
import orders
import positions

import os
import json

if __name__ == "__main__":
    session_manager.login()
    if market_exploration.tradeable_epics == {}:
        market_exploration.exploreNode(180500)
        with open(os.path.join(os.path.dirname(__file__), "data/tradeable_epics.json"), "w") as stream:
            json.dump(market_exploration.tradeable_epics, stream)

    pMap = positions.getPositionsSummary()
    for e in market_exploration.tradeable_epics.keys():
        epic, direction, limit, stop = trading.getTradeSignal(e)
        print(str(epic) + " : " + str(direction) + " : " + str(limit) + " : " + str(stop))
        if direction != "NONE":
            if orders.try_market_order(epic, direction, limit, stop, pMap):
                print("Made trade for "+epic+ " in direction of " + direction)