import numpy as np
import pandas
import pandas as pd
import matplotlib.pyplot as plt


class Valuation:

    def __init__(self, ticker):
        self.ticker = ticker
        self.financials = pd.read_excel(f'{ticker}_quarterly_financials.xlsx')[:-1].fillna(0)
        self.balance = pd.read_excel(f'{ticker}_quarterly_balance-sheet.xlsx')[:-1].fillna(0)
        self.cashflow = pd.read_excel(f'{ticker}_quarterly_cash-flow.xlsx')[:-1].fillna(0)

    def debt_structure(self):
        debt_equity = self.balance.filter(regex=r'TotalDebt$|StockholdersEquity|Date')
        debt_to_equity = debt_equity['TotalDebt'] / debt_equity['StockholdersEquity']
        plt.figure(figsize=(12, 6)) and plt.plot(
            debt_to_equity) and plt.show()  # add index = debt_equity['Date'].to_string()

    def free_cashflow(self):
        inflows = {
                'EBIT': self.financials['EBIT'],
                'NCC': self.financials['ReconciledDepreciation'],
                'new_borrowing': self.cashflow['FinancingCashFlow']
                }

        wc_inv = self.balance['CurrentAssets'] - self.balance['CurrentLiabilities']
        fc_inv = self.cashflow['CapitalExpenditure']

        outflows = {
                'tax': self.financials['PretaxIncome'] - self.financials['NetIncome'],
                'change_wc': wc_inv.shift(1) - wc_inv,
                'change_fc': fc_inv.shift(1) - fc_inv,
                'interests': self.financials['InterestExpense'],
                }

        fcff = inflows['EBIT'] + outflows['tax'] + inflows['NCC'] + outflows['change_wc'] + outflows['change_fc']
        fcfe = fcff - outflows['interests'] + inflows['new_borrowing']
        return fcff, fcfe



ticker = 'TSLA'
statements = Valuation(ticker)
statements.debt_structure()
statements.free_cashflow()


# self.expense_revenue = self.financials.filter(regex=r'TotalRevenue$|TotalExpenses').set_index(self.financials['name'])
# self.expense = self.financials['TotalExpenses'].values.reshape(-1, 1)
# self.revenue = self.financials['TotalRevenue'].values.reshape(-1, 1)
# 'WCinv': (self.balance['CurrentAssets'] - self.balance['CashAndCashEquivalents']) -
# (self.balance['CurrentLiabilities'] - self.balance['CurrentDebt']),
