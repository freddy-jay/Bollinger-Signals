import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from termcolor import colored as cl 

def get_sma(prices, rate=20):
    return prices.rolling(rate).mean()

def get_bollinger_bands(prices, rate=20):
    sma = get_sma(prices, rate) 
    std = prices.rolling(rate).std() 
    bollinger_up = sma + std * 2 # Calculate top band
    bollinger_down = sma - std * 2 # Calculate bottom band
    return bollinger_up, bollinger_down

def plot_bollinger_bands(price, rate =20):
    up, down = get_bollinger_bands(price, rate)
    plt.plot(price, label = 'price')
    plt.plot(up, label = 'upper band')
    plt.plot(down, label = 'lower band')
    plt.plot(get_sma(price, rate), label = 'sma')
    

def bb_strategy(data, upper_bb, lower_bb):
    buy_price = []
    sell_price = []
    bb_signal = []
    signal = 0
    
    for i in range(len(data)):
        if data[i-1] > lower_bb[i-1] and data[i] < lower_bb[i]:
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        elif data[i-1] < upper_bb[i-1] and data[i] > upper_bb[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_signal.append(0)
            
    return buy_price, sell_price, bb_signal

def plot_bb_strategy(data, upper, lower, figsize=(8,4), dpi = 300):
    plt.figure(figsize=figsize, dpi=dpi)
    plt.grid(True)
    buy_price, sell_price, bb_signal = bb_strategy(data, upper, lower)
    plt.plot(data, label = 'CLOSE PRICES', alpha = 0.3)
    plt.plot(upper, label = 'UPPER BB', linestyle = '--', linewidth = 1, color = 'black')
    plt.plot(lower, label = 'LOWER BB', linestyle = '--', linewidth = 1, color = 'black')
    
    plt.scatter(data.index, buy_price, marker = '^', color = 'green', label = 'BUY', s = 25)
    plt.scatter(data.index, sell_price, marker = 'v', color = 'red', label = 'SELL', s = 25)
    plt.title('BB STRATEGY TRADING SIGNALS')
    plt.legend(loc = 'upper left')
    
def return_strategy(data, upper, lower):
    buy_price, sell_price, bb_signal = bb_strategy(data, upper, lower)
    position = []
    for i in range(len(bb_signal)):
        if bb_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)

    for i in range(len(data)):
        if bb_signal[i] == 1:
            position[i] = 1
        elif bb_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]

    upper_bb = upper
    lower_bb = lower
    close_price = data
    bb_signal = pd.DataFrame(bb_signal).rename(columns = {0:'bb_signal'}).set_index(data.index)
    position = pd.DataFrame(position).rename(columns = {0:'bb_position'}).set_index(data.index)

    frames = [close_price, upper_bb, lower_bb, bb_signal, position]
    frames = [frame.reset_index() for frame in frames]
    strategy = pd.concat(frames, join = 'inner', axis = 1)
    strategy = strategy.reset_index()
    
    return strategy

def backtest_strategy(data, upper, lower, invest_value = 100000):
    strategy = return_strategy(data, upper, lower)
    
    ret = pd.DataFrame(np.diff(data)).rename(columns = {0:'returns'})
    bb_strategy_ret = []

    for i in range(len(ret)):
        try:
            returns = ret['returns'][i]*strategy['bb_position'][i]
            bb_strategy_ret.append(returns)
        except:
            pass
    
    bb_strategy_ret_df = pd.DataFrame(bb_strategy_ret).rename(columns = {0:'bb_returns'})

    investment_value = invest_value
    number_of_stocks = math.floor(investment_value/data[-1])
    bb_investment_ret = []

    for i in range(len(bb_strategy_ret_df['bb_returns'])):
        returns = number_of_stocks*bb_strategy_ret_df['bb_returns'][i]
        bb_investment_ret.append(returns)

    bb_investment_ret_df = pd.DataFrame(bb_investment_ret).rename(columns = {0:'investment_returns'})
    total_investment_ret = round(sum(bb_investment_ret_df['investment_returns']), 2)
    profit_percentage = math.floor((total_investment_ret/investment_value)*100)
    print(cl('Profit gained from the BB strategy by investing $100k: {}'.format(total_investment_ret), attrs = ['bold']))
    print(cl('Profit percentage of the BB strategy : {}%'.format(profit_percentage), attrs = ['bold']))
