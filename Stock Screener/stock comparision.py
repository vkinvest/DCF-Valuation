import pandas as pd
import datetime as dt
import pandas_datareader as dr
import yahoo_fin.stock_info as si
import statistics
import FundamentalAnalysis as fa
import time
import matplotlib.pyplot as plt





tickers = ['FSLY', 'TSLA', 'NIO']
period = 'annual'
api_key = 'e95137f175e3fba84a1220c74e5ecd2a'

begin = "2021-08-18"
end = dt.date.today()

statements = {}
revenue = pd.DataFrame()
growth = pd.DataFrame()
price = pd.DataFrame()

for ticker in tickers:
    statements[ticker] = {
        'balance': ((fa.balance_sheet_statement(ticker, api_key, period=period)).T.sort_index()),
        'income': ((fa.income_statement(ticker, api_key, period=period)).T.sort_index()),
        'cashflow': ((fa.cash_flow_statement(ticker, api_key, period=period)).T.sort_index())
    }

    revenue[ticker] = statements[ticker]['income']['revenue']
    revenue = revenue.loc[(revenue != 0).all(axis=1)]
    growth[ticker] = revenue[ticker].diff() / revenue[ticker].shift(1)

    price[ticker] = fa.stock_data_detailed(ticker, api_key, begin=begin, end=end)["adjClose"].sort_index()
    price_change = price / price.iloc[0] * 100

growth.plot(figsize=(12, 6))
plt.title(f'Revenue growth trend')
plt.show()

price_change.plot(figsize=(12, 6))
plt.title(f'Price trend since {begin}')
plt.show()
