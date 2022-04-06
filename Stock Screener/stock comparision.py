import pandas as pd
import datetime as dt
import pandas_datareader as dr
import yahoo_fin.stock_info as si
import statistics
import FundamentalAnalysis as fa
import time
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import plotly.offline as ply
import plotly.graph_objs as go
import chart_studio.plotly as py


tickers = ['FSLY', 'TSLA', 'NIO', 'RUN', 'PARA', 'QS', 'FSLY', 'JMIA', 'BARK', 'SUNW']
period = 'annual'
api_key = 'e95137f175e3fba84a1220c74e5ecd2a'

begin = "2022-01-01"
end = dt.date.today()

statements = {}
revenue = pd.DataFrame()
growth = pd.DataFrame()
price = pd.DataFrame()
volume = pd.DataFrame()
volume_mean = {}
volume_trend = pd.DataFrame()
volume_attention = pd.DataFrame()

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

    volume[ticker] = fa.stock_data_detailed(ticker, api_key, begin=begin, end=end)['volume'].sort_index()
    volume_mean[ticker] = statistics.mean(volume[ticker])
    volume_trend[ticker] = volume[ticker] / volume_mean[ticker]
    volume_attention[ticker] = volume_trend[ticker].loc[volume_trend[ticker] > 1]

volume_list = []
for col in volume_attention.columns:
    plot_trend = go.Scatter(
        name=col,
        x=volume_attention.index,
        y=volume_attention[col]
    )
    volume_list.append(plot_trend)

volume_fig = go.Figure(data=volume_list)
volume_fig.update_layout(title='Volume Above Average')
py.plot(volume_fig)


growth.plot(figsize=(12, 6), title='Revenue growth trend')
plt.show()

price_change = price / price.iloc[0] * 100
price_change.plot(figsize=(12, 6), title='Price trend since {begin}')
plt.show()
