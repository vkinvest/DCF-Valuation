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


ticker = 'RUN'
num_years = 5
cyclical = 'yes'


def get_data():
    api_key = 'e95137f175e3fba84a1220c74e5ecd2a'
    quarters = num_years * 4 + 1
    income = pd.DataFrame(((fa.income_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    balance = pd.DataFrame(((fa.balance_sheet_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    cashflow = pd.DataFrame(((fa.cash_flow_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    snapshot = income.filter(
        regex=r'fillingDate|revenue|costOfRevenue|^EBIT|^operatingIncome$|grossProfit$|^netIncome$|operatingExpenses')
    key_items = income[1:].filter(
        regex=r'fillingDate|operatingExpenses|sellingGeneralAndAdministrativeExpenses|researchAndDevelopmentExpenses|'
              r'Marketing|^operatingIncome|costAndExpenses|^netIncome$')
    return income, balance, cashflow, snapshot, key_items


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
                    operating_growth[col] = (snapshot[col][n] - snapshot[col][n-4]) / snapshot['revenue'][n-4]
                    if snapshot[col][n] > snapshot[col][n-4]:
                        operating_growth[col] = (snapshot[col][n] - snapshot[col][n-4]) / abs(snapshot['revenue'][n-4])

                else:
                    operating_growth[col] = (snapshot[col][n] - snapshot[col][n-1]) / snapshot['revenue'][n-1]
                    if snapshot[col][n] > snapshot[col][n-1]:
                        operating_growth[col] = snapshot[col].diff() / abs(snapshot['revenue'][n-1])

        return operating_growth

    margin = margin()
    growth = growth()
    return margin, growth


def charts():
    def fin_snapshot():
        snapshot_list = []

        for col in snapshot.columns[1:]:
            snapshot_bar = go.Scatter(
                name=col,
                x=snapshot['fillingDate'],
                y=snapshot[col]
            )
            snapshot_list.append(snapshot_bar)
        fig_is = go.Figure(data=snapshot_list)
        fig_is.update_layout(title=f'{ticker} Financial Snapshot')
        py.plot(fig_is)

    def key_margin():
        margin_list = []

        for col in margin.columns[1:]:
            margin_bar = go.Scatter(
                name=col,
                x=margin['fillingDate'],
                y=margin[col]
            )
            margin_list.append(margin_bar)
        fig_is = go.Figure(data=margin_list)
        fig_is.update_layout(title=f'{ticker} Key Margins')
        py.plot(fig_is)

    def growth_rate():
        growth_list = []

        for col in growth.columns[1:]:
            growth_bar = go.Scatter(
                name=col,
                x=growth['fillingDate'],
                y=growth[col]
            )

            growth_list.append(growth_bar)

        if cyclical == 'yes':
            period = 'YoY'
        else:
            period = 'QoQ'

        fig_is = go.Figure(data=growth_list)
        fig_is.update_layout(title=f'{ticker} {period} Growth Rates')
        py.plot(fig_is)

    fin_snapshot()
    key_margin()
    growth_rate()


income, balance, cashflow, snapshot, key_item = get_data()
margin, growth = clean_data()
charts()

# for n in range(len(snapshot['grossProfit'])):
#     operating['GrossProfit growth'] = snapshot['grossProfit'].diff() / snapshot['grossProfit'].shift(1)
#     if snapshot['grossProfit'][n] > snapshot['grossProfit'][n-4]:
#         operating['grossProfit growth'] = snapshot['grossProfit'].diff() / abs(snapshot['revenue'][n-4])
#
# operating['EBIT growth'] = snapshot['operatingIncome'].diff() / snapshot['operatingIncome'].shift(1)
# for n in range(len(snapshot['netIncome'])):
#     if snapshot['netIncome'][n] > snapshot['netIncome'][n-4]:
#         operating['EBIT growth'] = snapshot['netIncome'].diff() / abs(snapshot['revenue'][n-4])
#
# operating['Net income growth'] = snapshot['netIncome'].diff() / snapshot['netIncome'].shift(1)
# for n in range(len(snapshot['netIncome'])):
#     if snapshot['netIncome'][n] > snapshot['netIncome'][n-4]:
#         operating['Net income growth'] = snapshot['netIncome'].diff() / abs(snapshot['revenue'][n-4])
# growth = operating.filter(regex=r'fillingDate|growth')


# operating['Revenue growth'] = snapshot['revenue'].diff() / snapshot['revenue'].shift(1)
# for n in range(len(snapshot['revenue'])):
#     if snapshot['revenue'][n] > snapshot['revenue'][n - 1]:
#         operating['Revenue growth'] = snapshot['revenue'].diff() / abs(snapshot['revenue'].shift(1))
#
# operating['GrossProfit growth'] = snapshot['grossProfit'].diff() / snapshot['grossProfit'].shift(1)
# for n in range(len(snapshot['grossProfit'])):
#     if snapshot['grossProfit'][n] > snapshot['grossProfit'][n - 1]:
#         operating['grossProfit growth'] = snapshot['grossProfit'].diff() / abs(snapshot['grossProfit'].shift(1))
#
# operating['EBIT growth'] = snapshot['operatingIncome'].diff() / snapshot['operatingIncome'].shift(1)
# for n in range(len(snapshot['netIncome'])):
#     if snapshot['netIncome'][n] > snapshot['netIncome'][n - 1]:
#         operating['EBIT growth'] = snapshot['netIncome'].diff() / abs(snapshot['netIncome'].shift(1))
#
# operating['Net income growth'] = snapshot['netIncome'].diff() / snapshot['netIncome'].shift(1)
# for n in range(len(snapshot['netIncome'])):
#     if snapshot['netIncome'][n] > snapshot['netIncome'][n - 1]:
#         operating['Net income growth'] = snapshot['netIncome'].diff() / abs(snapshot['netIncome'].shift(1))
# growth = operating.filter(regex=r'fillingDate|growth')