import pandas as pd
import datetime as dt
from datetime import date
import pandas_datareader as dr
import yahoo_fin.stock_info as si
import matplotlib.pyplot as plt
import seaborn as sn
import statistics


# uses the past 4 years of data from yahoo finance


class DCF:
    def __init__(self, ticker):
        self.ticker = ticker
        income.columns = income.columns.str.lower()
        balance.columns = balance.columns.str.lower()
        cashflow.columns = cashflow.columns.str.lower()

    @staticmethod
    def revenue():
        revenue = income['totalrevenue']

        def growth_rate():
            growth_rate = statistics.mean((revenue.diff() / revenue.shift(1)).dropna())
            print(f'Revenue Growth Rate:', round(growth_rate, 2))
            return growth_rate

        growth_rate = growth_rate()
        current_rev = int(revenue[-1] * (1 + growth_rate))
        next1_rev = int(current_rev * (1 + growth_rate))
        next2_rev = int(next1_rev * (1 + growth_rate))
        next3_rev = int(next2_rev * (1 + growth_rate))
        df['Revenue'] = [revenue[3], revenue[2], revenue[1], revenue[0], current_rev, next1_rev, next2_rev, next3_rev,
                         'nan']
        return df['Revenue']

    @staticmethod
    def net_income():
        def margin():
            margin = statistics.mean((income['netincome'] / income['totalrevenue']))
            if margin < 0:
                margin = max((income['netincome'] / income['totalrevenue']))
                print(f'Max net margin (average net income margin is negative):', round(margin, 2))
            else:
                print(f'Net income margin: {margin}')
            return margin

        margin = margin()
        current_net_income = int(revenue[4] * margin)
        net_income_6 = int(revenue[5] * margin)
        net_income_7 = int(revenue[6] * margin)
        net_income_8 = int(revenue[7] * margin)

        net_income = income['netincome'] / 1000
        df['Net Income'] = (net_income[3], net_income[2], net_income[1], net_income[0],
                            current_net_income, net_income_6, net_income_7, net_income_8, 'nan')
        return df['Net Income']

    @staticmethod
    def free_cashflow():
        def calculate_fcff():
            wc_inv = balance['CurrentAssets'] - balance['CurrentLiabilities']
            fc_inv = cashflow['CapitalExpenditure']
            depreciation = cashflow.filter(regex=r'depreciation')
            new_debt = cashflow.filter(regex=r'debt')
            inflows = {
                'EBIT': income['EBIT'],
                'NCC': depreciation,
                'new_borrowing': cashflow['netborrowings']
            }

            outflows = {
                'tax': income['PretaxIncome'] - income['NetIncome'],
                'change_wc': wc_inv.shift(1) - wc_inv,
                'change_fc': fc_inv.shift(1) - fc_inv,
                'interests': income['InterestExpense'],
            }
            income['FCFF'] = inflows['EBIT'] + outflows['tax'] + inflows['NCC'] + outflows['change_wc'] + outflows[
                'change_fc']
            return income['FCFF']

        def fcff_margin():  # fcff % of net income
            calculate_fcff()
            fcff_item = income.filter(regex=r'^FCFF|^NetIncome$').dropna()
            fcff_margin = statistics.mean((fcff_item['FCFF'] / fcff_item['NetIncome']))
            print(f'Free cash flow to net income margin: {fcff_margin:}')
            return fcff_margin


ticker = 'sunw'
df = pd.DataFrame()
# current = int(date.today().year)
balance = (si.get_balance_sheet(ticker) / 1000).T.sort_index()
income = (si.get_income_statement(ticker) / 1000).T.sort_index()
cashflow = (si.get_cash_flow(ticker) / 1000).T.sort_index()
# analysts_est = si.get_analysts_info(ticker)

dcf = DCF(ticker)
revenue = dcf.revenue()
dcf.net_income()

# username = 'COLUMBIA_STU-1357760'
# api_key = 'jzqGQu3weBamDkwsGdBfj2Dpqto7B6Ll925QpvNX'
