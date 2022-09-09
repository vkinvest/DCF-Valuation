import yahoo_fin.stock_info as si
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
    py.plot(fig_is, filename=f'{ticker} growth')


ticker = 'TSLA'
api_key = 'e95137f175e3fba84a1220c74e5ecd2a'

income = pd.DataFrame(((fa.income_statement(ticker, api_key, period='quarter')).T.sort_index())[-21:])
balance = pd.DataFrame(((fa.balance_sheet_statement(ticker, api_key, period='quarter')).T.sort_index())[-21:])
cashflow = pd.DataFrame(((fa.cash_flow_statement(ticker, api_key, period='quarter')).T.sort_index())[-21:])

snapshot = income.filter(
    regex=r'fillingDate|revenue|costOfRevenue|^EBIT|^operatingIncome$|grossProfit|^netIncome$|operatingExpenses|costAndExpenses')

expense = income[1:].filter(
    regex=r'fillingDate|operatingExpenses|sellingGeneralAndAdministrativeExpenses|researchAndDevelopmentExpenses|Marketing|^operatingIncome|costAndExpenses')

expense['revenue'] = snapshot['revenue'] / snapshot['revenue']
expense['SG&A margin'] = (expense['sellingGeneralAndAdministrativeExpenses'] / snapshot['revenue'])
expense['R&D margin'] = (expense['researchAndDevelopmentExpenses'] / snapshot['revenue'])

expense['OperatingIncome margin'] = (expense['operatingIncome'] / snapshot['revenue'])
expense['OperatingExpense margin'] = (expense['operatingExpenses'] / snapshot['revenue'])
expense['TotalExpenses margin'] = expense['costAndExpenses'] / snapshot['revenue']
margin = expense.filter(regex=r'fillingDate|margin|revenue')

operating = pd.DataFrame()
operating['fillingDate'] = snapshot['fillingDate']
operating['Revenue growth'] = snapshot['netIncome'].diff() / snapshot['netIncome'].shift(1)
operating['GrossProfit growth'] = snapshot['grossProfit'].diff() / snapshot['grossProfit'].shift(1)
operating['EBIT growth'] = snapshot['operatingIncome'].diff() / snapshot['operatingIncome'].shift(1)
operating['Net income growth'] = expense['operatingExpenses'].diff() / expense['operatingExpenses'].shift(1)
growth = operating.filter(regex=r'fillingDate|growth')

fin_snapshot()
expense_margin()
growth_scatter()