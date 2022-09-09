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


ticker = 'AAPL'
num_years = 10


def get_data():
    api_key = 'e95137f175e3fba84a1220c74e5ecd2a'
    quarters = num_years * 4 + 1
    income = pd.DataFrame(((fa.income_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    balance = pd.DataFrame(((fa.balance_sheet_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    cashflow = pd.DataFrame(((fa.cash_flow_statement(ticker, api_key, period='quarter')).T.sort_index())[-quarters:])
    snapshot = income.filter(
        regex=r'fillingDate|revenue|costOfRevenue|^EBIT|^operatingIncome$|grossProfit$|^netIncome$|operatingExpenses')
    expense = income[1:].filter(
        regex=r'fillingDate|operatingExpenses|sellingGeneralAndAdministrativeExpenses|researchAndDevelopmentExpenses|'
              r'Marketing|^operatingIncome|costAndExpenses')
    return income, balance, cashflow, snapshot, expense


def clean_data():
    def margin():
        expense['revenue'] = snapshot['revenue'] / snapshot['revenue']
        expense['costOfRevenue'] = snapshot['costOfRevenue'] / snapshot['revenue']
        expense['SG&A margin'] = (expense['sellingGeneralAndAdministrativeExpenses'] / snapshot['revenue'])
        expense['R&D margin'] = (expense['researchAndDevelopmentExpenses'] / snapshot['revenue'])
        expense['OperatingIncome margin'] = (expense['operatingIncome'] / snapshot['revenue'])
        expense['OperatingExpense margin'] = (expense['operatingExpenses'] / snapshot['revenue'])
        expense['TotalExpenses margin'] = expense['costAndExpenses'] / snapshot['revenue']

        margin = expense.filter(regex=r'fillingDate|margin|revenue|costOfRevenue')
        return margin

    def growth():
        operating = pd.DataFrame()
        operating['fillingDate'] = snapshot['fillingDate']
        operating['Revenue growth'] = snapshot['revenue'].diff() / snapshot['revenue'].shift(1)
        for n in range(len(snapshot['revenue'])):
            if snapshot['revenue'][n] > snapshot['revenue'][n - 1]:
                operating['Revenue growth'] = snapshot['revenue'].diff() / abs(snapshot['revenue'].shift(1))

        operating['GrossProfit growth'] = snapshot['grossProfit'].diff() / snapshot['grossProfit'].shift(1)
        for n in range(len(snapshot['grossProfit'])):
            if snapshot['grossProfit'][n] > snapshot['grossProfit'][n - 1]:
                operating['grossProfit growth'] = snapshot['grossProfit'].diff() / abs(snapshot['grossProfit'].shift(1))

        operating['EBIT growth'] = snapshot['operatingIncome'].diff() / snapshot['operatingIncome'].shift(1)
        for n in range(len(snapshot['netIncome'])):
            if snapshot['netIncome'][n] > snapshot['netIncome'][n - 1]:
                operating['EBIT growth'] = snapshot['netIncome'].diff() / abs(snapshot['netIncome'].shift(1))

        operating['Net income growth'] = snapshot['netIncome'].diff() / snapshot['netIncome'].shift(1)
        for n in range(len(snapshot['netIncome'])):
            if snapshot['netIncome'][n] > snapshot['netIncome'][n - 1]:
                operating['Net income growth'] = snapshot['netIncome'].diff() / abs(snapshot['netIncome'].shift(1))
        growth = operating.filter(regex=r'fillingDate|growth')
        return growth

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
        py.plot(fig_is, filename=f'{ticker} financial outlook')

    def expense_margin():
        margin_list = []

        for col in margin.columns[1:]:
            margin_bar = go.Scatter(
                name=col,
                x=margin['fillingDate'],
                y=margin[col]
            )
            margin_list.append(margin_bar)
        fig_is = go.Figure(data=margin_list)
        py.plot(fig_is, filename=f'{ticker} margin')

    def growth_scatter():
        growth_list = []

        for col in growth.columns[1:]:
            growth_bar = go.Scatter(
                name=col,
                x=growth['fillingDate'],
                y=growth[col]
            )

            growth_list.append(growth_bar)
        fig_is = go.Figure(data=growth_list)
        py.plot(fig_is, filename=f'{ticker} QoQ growth')

    fin_snapshot()
    expense_margin()
    growth_scatter()


income, balance, cashflow, snapshot, expense = get_data()
margin, growth = clean_data()
charts()
