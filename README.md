# Setup
To setup this project for running, you want to rename resources/config-samples.json 
resources/config.json and fill in your login credentials for IG trading platform.

# Usage
Running the main file will scan the UK shares market, create a list of potential shares
to trade, then attempt to make a buy or sell on these stocks based on the MAD of the 
low and highs of the stock.

Running the market_exploration file will populate the list of potential markets without 
executing any trades

Running the trading file will create a list of potential trades from the markets in the
potential trades list and print them to the console

# Packages
The project relies on the following packages
 - numpy
 - statsmodels
 - scipy
 - requests