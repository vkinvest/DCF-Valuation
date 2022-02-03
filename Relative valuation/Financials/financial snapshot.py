import yahoo_fin.stock_info as si
import pandas as pd
import matplotlib.pyplot as plt
import chart_studio.plotly as py
import plotly.graph_objs as go
import seaborn as sns
import numpy as np


def financial_snapshot():
    snapshot_list = []

    for col in snapshot.columns[1:]:
        snapshot_bar = go.Scatter(
            name=col,
            x=snapshot['name'],
            y=snapshot[col]
        )
        print(col)
        snapshot_list.append(snapshot_bar)
    fig_is = go.Figure(data=snapshot_list, layout=go.Layout(barmode='stack'))
    py.plot(fig_is, filename=f'{ticker} financial outlook')


def expense_margin():
    margin_list = []

    for col in margin.columns[1:]:
        margin_bar = go.Scatter(
            name=col,
            x=margin['name'],
            y=margin[col]
        )
        print(col)
        margin_list.append(margin_bar)
    fig_is = go.Figure(data=margin_list, layout=go.Layout(barmode='stack'))
    py.plot(fig_is, filename=f'{ticker} margin')


def growth_scatter():
    growth_list = []

    for col in growth.columns[1:]:
        growth_bar = go.Scatter(
            name=col,
            x=growth['name'],
            y=growth[col]
        )

        print(col)
        growth_list.append(growth_bar)
    fig_is = go.Figure(data=growth_list, layout=go.Layout(barmode='stack'))
    py.plot(fig_is, filename=f'{ticker} growth')


ticker = 'TSLA'

financials = pd.read_excel(f'{ticker}_quarterly_financials.xlsx')
snapshot = financials[1:].filter(
    regex=r'name|TotalRevenue|CostOfRevenue|^EBIT|^OperatingIncome$|GrossProfit|^NetIncome$|OperatingExpense|TotalExpenses')

operating = financials[1:].filter(regex=r'name|TotalRevenue|GrossProfit|OperatingExpense|^OperatingIncome$')
operating['Revenue growth'] = (operating['TotalRevenue'] - operating['TotalRevenue'].shift(1)) / operating['TotalRevenue'].shift(1)
operating['GrossProfit growth'] = (operating['GrossProfit'] - operating['GrossProfit'].shift(1)) / operating['GrossProfit'].shift(1)
operating['OperatingExpense growth'] = (operating['OperatingExpense'] - operating['OperatingExpense'].shift(1)) / operating['OperatingExpense'].shift(1)
operating['OperatingIncome growth'] = (operating['OperatingIncome'] - operating['OperatingIncome'].shift(1)) / operating['OperatingIncome'].shift(1)
growth = operating.filter(regex=r'name|growth')


expense = financials[1:].filter(regex=r'name|OperatingExpense|Administration|Research|Marketing|^OperatingIncome|TotalExpenses')
expense['OperatingExpense margin'] = (expense['OperatingExpense'] / operating['TotalRevenue'])
expense['SG&A margin'] = (expense['SellingGeneralAndAdministration'] / operating['TotalRevenue'])
expense['R&D margin'] = (expense['ResearchAndDevelopment'] / operating['TotalRevenue'])

expense['OperatingIncome margin'] = (expense['OperatingIncome'] / operating['TotalRevenue'])
expense['TotalExpenses margin'] = (expense['TotalExpenses'] / operating['TotalRevenue'])
margin = expense.filter(regex=r'name|margin')


growth_scatter()
expense_margin()
financial_snapshot()
