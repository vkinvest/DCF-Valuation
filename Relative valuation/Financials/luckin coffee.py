import pandas as pd
import matplotlib.pyplot as plt
import chart_studio.plotly as py
import plotly.graph_objs as go
import seaborn as sns
import numpy as np
import chart_studio.plotly as py
import FundamentalAnalysis as fa
import datetime as dt
from datetime import date
import yfinance as yf

num_years = 5
cyclical = 'yes'
ticker = 'LKNCY'
tickers = ['LKNCY', 'SBUX', '^IXIC', 'XLY']


def get_data():
    api_key = 'e95137f175e3fba84a1220c74e5ecd2a'
    quarters = num_years * 4 + 1
    income = pd.DataFrame(((fa.income_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    balance = pd.DataFrame(((fa.balance_sheet_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    cashflow = pd.DataFrame(((fa.cash_flow_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    quotes = pd.DataFrame((fa.quote(ticker, api_key)).T.sort_index())
    snapshot = income.filter(
        regex=r'fillingDate|revenue|costOfRevenue|^EBIT|^operatingIncome$|grossProfit$|^netIncome$|operatingExpenses')
    key_items = income[1:].filter(
        regex=r'fillingDate|operatingExpenses|sellingGeneralAndAdministrativeExpenses|researchAndDevelopmentExpenses|'
              r'Marketing|^operatingIncome|costAndExpenses|^netIncome$')

    quote = pd.DataFrame()
    vol = pd.DataFrame()
    for t in tickers:
        quote[t] = yf.download(t, start="2019-05-17", end=None)['Adj Close']
        vol[t] = yf.download(t, start="2019-05-17")['Volume']

    return income, balance, cashflow, snapshot, key_items, quote, vol


def clean_data():
    def margin():
        key_item['revenue'] = snapshot['revenue'] / snapshot['revenue']
        key_item['costOfRevenue'] = snapshot['costOfRevenue'] / snapshot['revenue']
        key_item['SG&A margin'] = (key_item['sellingGeneralAndAdministrativeExpenses'] / snapshot['revenue'])
        key_item['R&D margin'] = (key_item['researchAndDevelopmentExpenses'] / snapshot['revenue'])
        key_item['OperatingIncome margin'] = (key_item['operatingIncome'] / snapshot['revenue'])
        key_item['OperatingExpense margin'] = (key_item['operatingExpenses'] / snapshot['revenue'])
        key_item['TotalExpenses margin'] = key_item['costAndExpenses'] / snapshot['revenue']
        key_item['NetIncome margin'] = key_item['netIncome'] / snapshot['revenue']

        margin = key_item.filter(regex=r'fillingDate|margin|revenue|costOfRevenue')
        return margin

    def growth():
        operating_growth = pd.DataFrame()
        column = 'revenue', 'grossProfit', 'operatingIncome', 'netIncome'
        operating_growth['fillingDate'] = snapshot['fillingDate']

        for col in column:
            for n in range(len(snapshot['revenue'])):
                if cyclical == 'yes':
                    operating_growth[col] = (snapshot[col][n] - snapshot[col][n - 4]) / snapshot['revenue'][n - 4]
                    if snapshot[col][n] > snapshot[col][n - 4]:
                        operating_growth[col] = (snapshot[col][n] - snapshot[col][n - 4]) / abs(
                            snapshot['revenue'][n - 4])

                else:
                    operating_growth[col] = (snapshot[col][n] - snapshot[col][n - 1]) / snapshot['revenue'][n - 1]
                    if snapshot[col][n] > snapshot[col][n - 1]:
                        operating_growth[col] = snapshot[col].diff() / abs(snapshot['revenue'][n - 1])

        return operating_growth

    def comparison():
        compare_day1 = (quote / quote.iloc[0] * 100)
        return compare_day1

    def risk():
        mean = quote.mean()
        variance = (quote - mean)**2 / (len(quote)-1)
        risk = variance ** 0.5
        return risk

    margin = margin()
    growth = growth()
    compare_day1 = comparison()
    risk = risk()
    return margin, growth, compare_day1, risk


def charts():
    def fin_snapshot():
        list = []

        for col in snapshot.columns[1:]:
            bar = go.Scatter(
                name=col,
                x=snapshot['fillingDate'],
                y=snapshot[col]
            )
            list.append(bar)
        fig = go.Figure(data=list)
        fig.update_layout(title=f'{ticker} Financial Snapshot')
        py.plot(fig)

    def key_margin():
        list = []

        for col in margin.columns[1:]:
            bar = go.Scatter(
                name=col,
                x=margin['fillingDate'],
                y=margin[col]
            )
            list.append(bar)
        fig = go.Figure(data=list)
        fig.update_layout(title=f'{ticker} Key Margins')
        py.plot(fig)

    def growth_rate():
        list = []

        for col in growth.columns[1:]:
            bar = go.Scatter(
                name=col,
                x=growth['fillingDate'],
                y=growth[col]
            )

            list.append(bar)

        if cyclical == 'yes':
            period = 'YoY'
        else:
            period = 'QoQ'

        fig = go.Figure(data=list)
        fig.update_layout(title=f'{ticker} {period} Growth Rates')
        py.plot(fig)

    def price_movement():
        list = []

        for col in quote.columns:
            bar = go.Scatter(
                name=col,
                x=quote.index,
                y=quote[col]
            )
            list.append(bar)
        fig = go.Figure(data=list)
        fig.update_layout(title='Risk Movement Compared to Day1')
        py.plot(fig)

    def risk_movement():
        list = []

        for col in risk.columns:
            bar = go.Scatter(
                name=col,
                x=compare_day1.index,
                y=compare_day1[col]
            )
            list.append(bar)
        fig = go.Figure(data=list)
        fig.update_layout(title='Price Movement Compared to Day1')
        py.plot(fig)

    def volumes():
        list = []

        for col in vol.columns:
            bar = go.Scatter(
                name=col,
                x=vol.index,
                y=vol[col]
            )
            list.append(bar)
        fig = go.Figure(data=list)
        fig.update_layout(title='Daily Volumes')
        py.plot(fig)

    fin_snapshot()
    key_margin()
    growth_rate()
    price_movement()
    volumes()


income, balance, cashflow, snapshot, key_item, quote, vol = get_data()
margin, growth, compare_day1, risk = clean_data()
charts()



# def financial_snapshot():
#     snapshot_list = []
#
#     for col in snapshot.columns:
#         snapshot_bar = go.Scatter(
#             name=col,
#             x=snapshot.index,
#             y=snapshot[col]
#         )
#         snapshot_list.append(snapshot_bar)
#     fig_is = go.Figure(data=snapshot_list)
#     py.plot(fig_is, filename=f'{ticker} financial outlook')
#
#
# def expense_margin():
#     margin_list = []
#
#     for col in margin.columns[1:]:
#         margin_bar = go.Scatter(
#             name=col,
#             x=margin['name'],
#             y=margin[col]
#         )
#         margin_list.append(margin_bar)
#     fig_is = go.Figure(data=margin_list)
#     py.plot(fig_is, filename=f'{ticker} margin')
#
#
# def growth_scatter():
#     growth_list = []
#
#     for col in growth.columns[1:]:
#         growth_bar = go.Scatter(
#             name=col,
#             x=growth['name'],
#             y=growth[col]
#         )
#
#         growth_list.append(growth_bar)
#     fig_is = go.Figure(data=growth_list)
#     py.plot(fig_is, filename=f'{ticker} growth')
#
# financial_snapshot()
# expense_margin()
# growth_scatter()
#
# ticker = 'TSLA'
#
#
#
# income, balance, cashflow, snapshot, expense = get_data()
# margin, growth = clean_data()
# charts()
#
# financials = pd.read_excel(f'/Users/vl/Desktop/DataBase/Columbia/ESR/HW/Group 2/financials/LKNCY_quarterly_financials.xlsx').T
# financials.columns = financials.iloc[0]
# financials = financials[1:].sort_index()
#
# snapshot = financials[1:].filter(
#     regex=r'Date|Total net revenues|Cost of materials|^Sales and marketing expenses$|General and administrative expenses'
#           r'|Total operating expenses$|Operating loss/income')

# operating = financials[1:].filter(regex=r'name|TotalRevenue|GrossProfit|OperatingExpense|^OperatingIncome$')
# operating['Revenue growth'] = (operating['TotalRevenue'] - operating['TotalRevenue'].shift(1)) / operating['TotalRevenue'].shift(1)
# operating['GrossProfit growth'] = (operating['GrossProfit'] - operating['GrossProfit'].shift(1)) / operating['GrossProfit'].shift(1)
# operating['OperatingExpense growth'] = (operating['OperatingExpense'] - operating['OperatingExpense'].shift(1)) / operating['OperatingExpense'].shift(1)
# operating['OperatingIncome growth'] = (operating['OperatingIncome'] - operating['OperatingIncome'].shift(1)) / operating['OperatingIncome'].shift(1)
# growth = operating.filter(regex=r'name|growth')
#
#
# expense = financials[1:].filter(regex=r'name|OperatingExpense|Administration|Research|Marketing|^OperatingIncome|TotalExpenses')
# expense['OperatingExpense margin'] = (expense['OperatingExpense'] / operating['TotalRevenue'])
# expense['SG&A margin'] = (expense['SellingGeneralAndAdministration'] / operating['TotalRevenue'])
# expense['R&D margin'] = (expense['ResearchAndDevelopment'] / operating['TotalRevenue'])
#
# expense['OperatingIncome margin'] = (expense['OperatingIncome'] / operating['TotalRevenue'])
# expense['TotalExpenses margin'] = (expense['TotalExpenses'] / operating['TotalRevenue'])
# margin = expense.filter(regex=r'name|margin')

#
# growth_scatter()
# expense_margin()
# financial_snapshot()
