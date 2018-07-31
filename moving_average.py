import pandas as pd
import numpy as np
import backtest

"""
Author: Rafał Zaręba

Strategy based on 2 moving averages MA: shorter ma_s and longer ma_l
Signals:
Short position: ma_s crossover ma_l, previous value of ma_s is higher than ma_l
Close Short position: ma_s crossover ma_l, previous value of ma_s is lower than ma_l
Long position: ma_s crossover ma_l, previous value of ma_s is lower than ma_l
Close Long position: ma_s crossover ma_l, previous value of ma_s is higher than ma_l
"""

path = '/home/jessie/Desktop/notowaniaM1/edekmaj.csv'
data = pd.read_csv(path, index_col='Date', parse_dates=True)
data = data.resample('15T').bfill()

# Set strategy parameters and creating moving averages
s_period = 9
l_period = 18

start_hour = 8
end_hour = 18

ma_type = 'simple'

if ma_type == 'simple':
    ma_s = backtest.sma(data=data['Close'], period=s_period)
    ma_l = backtest.sma(data=data['Close'], period=l_period)
elif ma_type == 'exponential':
    ma_s = backtest.ema(data=data['Close'], period=s_period)
    ma_l = backtest.ema(data=data['Close'], period=l_period)
else:
    print('Wrong type o moving averages passed!\n'
          'Try: "simple" or "exponential"')

# Creating column with hour
data['Hour'] = data.index.strftime('%H')
data['Hour'] = data.index.hour

# Creating columns with positions signals
# These columns are filled with True and False values
data['Short signal'] = (ma_s < ma_l) & (ma_s.shift(1) > ma_l.shift(1)) & \
                       (data['Hour'] >= start_hour) & (data['Hour'] <= end_hour)
data['Short exit'] = (ma_s > ma_l) & (ma_s.shift(1) < ma_l.shift(1))
data['Long signal'] = (ma_s > ma_l) & (ma_s.shift(1) < ma_l.shift(1)) & \
                       (data['Hour'] >= start_hour) & (data['Hour'] <= end_hour)
data['Long exit'] = (ma_s < ma_l) & (ma_s.shift(1) > ma_l.shift(1))

# Creating columns for transactions based on signals
# Short transactions: -1, Long transactions: 1, No transactions: 0
data['Short'] = np.nan
data.loc[(data['Short signal']), 'Short'] = -1
data.loc[(data['Short exit']), 'Short'] = 0

data['Long'] = np.nan
data.loc[(data['Long signal']), 'Long'] = 1
data.loc[(data['Long exit']), 'Long'] = 0

# Set 0 (no transaction) at beginning
data.iloc[0, data.columns.get_loc('Short')] = 0
data.iloc[0, data.columns.get_loc('Long')] = 0

# Fill NaN values by method forward fill
data['Long'] = data['Long'].fillna(method='ffill')
data['Short'] = data['Short'].fillna(method='ffill')

# Final Position column is sum of Long and Short column
data['Position'] = data['Long'] + data['Short']

# Market and strategy returns
data['Market Return'] = np.log(data['Close']).diff()
data['Strategy'] = data['Market Return'] * data['Position']

# Market and strategy equity
data['Market Equity'] = data['Market Return'].cumsum() + 1
data['Strategy Equity'] = data['Strategy'].cumsum() + 1

backtest.calculate_ratios(data, print_ratios=True)

# asd asd asd
