import yahoo_fin.stock_info as si
import pandas as pd
import chart_studio
import chart_studio.plotly as py
import plotly.graph_objs as go


def pe_ratios():
    pe_ttm = price/eps
    charts['P/E'] = pe_ttm


def scatter():
    is_list = []

    for col in charts.columns[1:]:
        income_bar = go.Scatter(
            name=col,
            x=charts['Date'],
            y=charts[col]
        )
        print(col)
        is_list.append(income_bar)

    fig_is = go.Figure(data=is_list, layout=go.Layout(barmode='stack'))
    py.plot(fig_is, filename='Tesla historical PE ratios')


charts = pd.read_excel('chart_data.xlsx')#.set_index('Date')
columns = charts.columns

financials = pd.read_excel('TSLA_quarterly_financials.xlsx')
balance = pd.read_excel('TSLA_quarterly_balance-sheet.xlsx')
cashflow = pd.read_excel('TSLA_quarterly_cash-flow.xlsx')

price = pd.read_excel('TSLA_price.xlsx')['Adj Close']
eps = financials['DilutedEPS'][-41:-1]
sales = financials['TotalRevenue'][-41:-1]

pe_ratios()
scatter()
