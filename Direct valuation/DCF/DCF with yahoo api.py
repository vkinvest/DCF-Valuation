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

    @staticmethod
    def revenue():
        def growth_rate():
            growth_rate = statistics.mean((revenue.diff() / revenue.shift(1)).dropna())
            print(f'Revenue Growth Rate:', round(growth_rate, 2))
            return growth_rate

        growth_rate = growth_rate()
        rev_5 = int(revenue[-1] * (1 + growth_rate))
        rev_6 = int(rev_5 * (1 + growth_rate))
        rev_7 = int(rev_6 * (1 + growth_rate))
        rev_8 = int(rev_7 * (1 + growth_rate))
        rev_9 = int(rev_8 * (1 + growth_rate))

        df['Revenue'] = [revenue[0], revenue[1], revenue[2], revenue[3], rev_5, rev_6, rev_7, rev_8, rev_9, 'nan']
        return df['Revenue']

    @staticmethod
    def free_cashflow_firm():
        def fcff():
            EBIT = income['ebit']
            NCC = cashflow.filter(regex=r'depreciation').iloc[:, 0]

            wc_inv = balance['totalcurrentassets'] - balance['totalcurrentliabilities']
            fc_inv = cashflow['capitalexpenditures']
            change_wc = wc_inv - wc_inv.shift(1).fillna(0)
            change_fc = fc_inv - fc_inv.shift(1).fillna(0)
            tax = income.filter(regex=r'taxexpense').iloc[:, 0]

            FCFF = EBIT + NCC - change_wc - change_fc - tax
            return FCFF

        fcff = fcff()

        def fcff_margin():
            margin = statistics.mean(fcff / income['totalrevenue'])
            print(f'Free cash flow margin', round(margin, 2))
            return margin

        margin = fcff_margin()
        fcff_5 = int(rev_df[4] * margin)
        fcff_6 = int(rev_df[5] * margin)
        fcff_7 = int(rev_df[6] * margin)
        fcff_8 = int(rev_df[7] * margin)
        fcff_9 = int(rev_df[8] * margin)

        df['FCFF'] = (fcff[0], fcff[1], fcff[2], fcff[3], fcff_5, fcff_6, fcff_7, fcff_8, fcff_9, 'nan')
        return df['FCFF']

    @staticmethod
    def wacc():
        # required return: WACC =  We *Ke + Wd *Kd *(1-t)
        def cost_of_equity():
            market_return = 0.10
            beta = stock_info.get('Beta (5Y Monthly)')
            rf_rate = dr.DataReader('^TNX', 'yahoo', past_date, today)['Adj Close'][0]/100
            print('RF rate:', round(rf_rate, 2), '  Beta:', beta)

            ke = round(rf_rate + beta * (market_return - rf_rate), 2)
            print('Cost of equity', ke)
            return ke

        ke = cost_of_equity()
        total_debt = balance['shortlongtermdebt'] + balance['longtermdebt'] # todo data of dete is incomplete from yahoo

        def cost_of_debt():
            interest_exp = income['interestexpense']
            kd = (-interest_exp / total_debt).dropna()[-1]

            tax_rate = income['incometaxexpense'] / income['incomebeforetax']
            tax_adj_kd = round(kd * (1 - tax_rate[-1]), 2)
            print('Cost of debt', tax_adj_kd)
            return tax_adj_kd

        tax_adj_kd = cost_of_debt()

        def weights():
            market_cap = stock_info.get("Market Cap")
            if market_cap[-1] == 'T':
                market_cap = float(market_cap.replace('T', '0')) * 1000000
            if market_cap[-1] == 'B':
                market_cap = float(market_cap.replace('B', '0')) * 1000
            elif market_cap[-1] == 'M':
                market_cap = float(market_cap.replace('M', ''))
            print(f'Market cap: {market_cap:} millions')

            total_capital = total_debt[-1] + market_cap
            weight_debt = round(total_debt[-1] / total_capital, 2)
            weight_equity = round(market_cap / total_capital, 2)
            return weight_debt, weight_equity

        weight_debt, weight_equity = weights()
        wacc = round((weight_equity * ke + weight_debt * tax_adj_kd), 2)

        print('Weight of Equity', round(weight_equity, 2), '   Weight of Equity', round(weight_debt, 2))
        print(f'Required return wacc: {round(wacc, 3):}')
        return wacc


ticker = 'tsla'
balance = (si.get_balance_sheet(ticker) / 1000000).T.sort_index()
income = (si.get_income_statement(ticker) / 1000000).T.sort_index()
cashflow = (si.get_cash_flow(ticker) / 1000000).T.sort_index()
income.columns = income.columns.str.lower()
balance.columns = balance.columns.str.lower()
cashflow.columns = cashflow.columns.str.lower()

df = pd.DataFrame()

revenue = income['totalrevenue']
net_income = income['netincome']

stock_info = si.get_quote_table(ticker, dict_result=True)
today = dt.date.today()
past_date = today - dt.timedelta(days=225)

dcf = DCF(ticker)
rev_df = dcf.revenue()
# net_df = dcf.net_income()
dcf.free_cashflow_firm()
wacc = dcf.wacc()






# analysts_est = si.get_analysts_info(ticker)
# current = int(date.today().year)
# username = 'COLUMBIA_STU-1357760'
# api_key = 'jzqGQu3weBamDkwsGdBfj2Dpqto7B6Ll925QpvNX'
# 'interests': income.filter(regex=r'interestexpense')
# past_date = current_date - dt.timedelta(days=225)

# @staticmethod
# def net_income():
#     def net_margin():
#         margin = statistics.mean((income['netincome'] / income['totalrevenue']))
#         if margin < 0:
#             margin = max((income['netincome'] / income['totalrevenue']))
#             print(f'Max net margin (average net income margin is negative):', round(margin, 2))
#         else:
#             print(f'Net income margin:', round(margin, 2))
#         return margin
#
#     margin = net_margin()
#     net_5 = int(rev_df[4] * margin)
#     net_6 = int(rev_df[5] * margin)
#     net_7 = int(rev_df[6] * margin)
#     net_8 = int(rev_df[7] * margin)
#     net_9 = int(rev_df[8] * margin)
#
#     df['Net Income'] = (net_income[0], net_income[1], net_income[2], net_income[3], net_5, net_6, net_7, net_8, net_9, 'nan')
#     return df['Net Income']