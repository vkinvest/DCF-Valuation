import numpy as np
import datetime as dt
from datetime import date
import pandas_datareader as dr
import yahoo_fin.stock_info as si
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
import seaborn as sn


class Items:

    def __init__(self, ticker):
        self.ticker = ticker

        self.balance = pd.read_excel(f'{ticker}_annual_balance-sheet.xlsx')[:-1].fillna(0).set_index('Date')
        self.cashflow = pd.read_excel(f'{ticker}_annual_cash-flow.xlsx')[:-1].fillna(0).set_index('Date')
        self.regressor = LinearRegression()

    def regressor():
        element = income.filter(regex=r'TotalRevenue|^CostOfRevenue|TotalExpenses|GrossProfit')
        corr = (element / 1000000).corr()
        max_corr = corr['TotalRevenue'].nlargest(2).nsmallest(1)
        regressor = max_corr.index.values[0]
        selected = income.filter(regex=f'TotalRevenue|^{regressor}')
        selected.plot(x=f'{regressor}', y='TotalRevenue', style='o')
        plt.xlabel('CostOfRevenues') and plt.ylabel('TotalRevenue')
        plt.title('Expenses vs Revenue') and plt.show()
        return regressor

    def regression(self):
        revenue = (income['TotalRevenue']/1000000).values.reshape(-1, 1)
        regressor1 = (income[f'{regressor()}'] / 1000000).values.reshape(-1, 1)
        x_train, x_test, y_train, y_test = train_test_split(regressor1, revenue, test_size=0.10, random_state=0)
        self.regressor.fit(x_train, y_train)
        print(f'Intercept:{self.regressor.intercept_}', f'Coefficient: {self.regressor.coef_}')

        y_pred = self.regressor.predict(x_test)
        result_accuracy = pd.DataFrame({'Actual': y_test.tolist(), 'Predicted': y_pred.tolist()}, index=range(len(y_test)))
        print(result_accuracy)  # how to remove [] signs from the list
        print('Mean Absolute Error:', int(metrics.mean_absolute_error(y_test, y_pred)))
        print('Mean Squared Error:', int(metrics.mean_squared_error(y_test, y_pred)))
        print('Root Mean Squared Error:', int(np.sqrt(metrics.mean_squared_error(y_test, y_pred))))
        co_efficient = self.regressor.coef_
        return co_efficient

    # def free_cashflow(self):
    #     inflows = {
    #         'EBIT': self.income['EBIT'],
    #         'NCC': self.income['ReconciledDepreciation'],
    #         'new_borrowing': self.cashflow['FinancingCashFlow']
    #     }
    #
    #     wc_inv = self.balance['CurrentAssets'] - self.balance['CurrentLiabilities']
    #     fc_inv = self.cashflow['CapitalExpenditure']
    #
    #     outflows = {
    #         'tax': self.income['PretaxIncome'] - self.income['NetIncome'],
    #         'change_wc': wc_inv.shift(1) - wc_inv,
    #         'change_fc': fc_inv.shift(1) - fc_inv,
    #         'interests': self.income['InterestExpense'],
    #     }
    #
    #     fcff = inflows['EBIT'] + outflows['tax'] + inflows['NCC'] + outflows['change_wc'] + outflows['change_fc']
    #     return fcff


ticker = 'TSLA'
income = pd.read_excel(f'{ticker}_annual_financials.xlsx')[:-1].fillna(0).set_index('Date')
get = Items(ticker)
co_efficient = get.regression()

# fcff = get.free_cashflow()
#
#
# original
# import pandas as pd
# import numpy as np
# import datetime as dt
# from datetime import date
# import pandas_datareader as dr
# import yahoo_fin.stock_info as si
# import matplotlib.pyplot as plt
#
#
# class DCF:
#     def __init__(self, ticker):
#         self.ticker = ticker
#         self.balance = si.get_balance_sheet(ticker).transpose()
#         self.income = si.get_income_statement(ticker).transpose()
#         self.cashflow = si.get_cash_flow(ticker).transpose()
#         self.analysts_est = si.get_analysts_info(ticker)
#         self.price = int(date.today().year)
#         self.revenue = self.income['totalRevenue'] / 1000000000
#         self.net_income = self.income['netIncome'] / 1000000000
#         operating_cashflow = self.cashflow['totalCashFromOperatingActivities'] / 1000000000
#         capital_expenditures = self.cashflow['capitalExpenditures'] / 1000000000
#         self.fcf = operating_cashflow + capital_expenditures
#         self.stock_info = si.get_quote_table(ticker, dict_result=True)
#         self.data = si.get_quote_data(ticker)
#         self.current = int(date.today().year)
#         self.shares_outstanding = self.data.get('sharesOutstanding') / 1000000000
#         self.index_year = (self.current-4, self.current-3, self.current-2, self.current-1,
#                            self.current, self.current+1, self.current+2, self.current+3, self.current+4)
#
#     # projections to get free cash flow
#     def growth_rate(self):
#         growth1 = (self.revenue[2] - self.revenue[3]) / self.revenue[3]  # 3 historical growth rates
#         growth2 = (self.revenue[1] - self.revenue[2]) / self.revenue[2]
#         growth3 = (self.revenue[0] - self.revenue[1]) / self.revenue[1]
#
#         growth_est = self.analysts_est['Growth Estimates'].transpose().iloc[1]  # 2 analysts projections
#         growth_4 = float(growth_est[2].replace('%', '0')) / 100
#         growth_5 = float(growth_est[3].replace('%', '0')) / 100
#         growth_rate = (growth1 + growth2 + growth3 + growth_4 + growth_5) / 5
#         return growth_rate
#
#     def revenue_est(self):
#         rev_est = self.analysts_est['Revenue Estimate'].iloc[1].filter(regex=r'Year')
#         current_est = float(rev_est[-1].replace('B', '0'))  # 2 analyst projections
#         next1_est = float(rev_est[-2].replace('B', '0'))
#         next2_est = next1_est * (1 + growth_rate)  # 3 projections, based on avg. growth rate
#         next3_est = next2_est * (1 + growth_rate)
#         revenue_est = (self.revenue[3], self.revenue[2], self.revenue[1], self.revenue[0],
#                        current_est, next1_est, next2_est, next3_est, 'nan')
#         return revenue_est
#
#     def net_income_est(self):
#         net_income_margin = max(self.net_income / self.revenue) # or avg. / len(self.revenue)
#         net_income_5 = revenue_est[4] * net_income_margin  # current year, based on net income margin
#         net_income_6 = revenue_est[5] * net_income_margin
#         net_income_7 = revenue_est[6] * net_income_margin
#         net_income_8 = revenue_est[7] * net_income_margin
#         net_income_est = (self.net_income[3], self.net_income[2], self.net_income[1], self.net_income[0],
#                           net_income_5, net_income_6, net_income_7, net_income_8, 'nan')
#         return net_income_est
#
#     def free_cashflow(self):
#         cf = self.fcf[1:]
#         fcf_margin = sum(cf / self.net_income[1:]) / 3
#         print(f'Free Cashflow Margin: {round(fcf_margin, 3)}')
#
#         fcf_4 = net_income_est[3] * fcf_margin
#         fcf_5 = net_income_est[4] * fcf_margin
#         fcf_6 = net_income_est[5] * fcf_margin
#         fcf_7 = net_income_est[6] * fcf_margin
#         fcf_8 = net_income_est[7] * fcf_margin
#         fcf_est = (self.fcf[3], self.fcf[2], self.fcf[1], fcf_4, fcf_5, fcf_6, fcf_7, fcf_8, 'nan')
#         plt.plot(fcf_est[:-1]) and plt.show()
#         return fcf_est
#
#     # required return: WACC =  We *Ke + Wd *Kd *(1-t)
#     def required_return(self):
#         # 1 cost of equity: Ke = CAPM = Rf + beta * (Rm - Rf)
#         beta = self.stock_info.get('Beta (5Y Monthly)')
#         print('Beta:', beta)
#         current_date = dt.date.today()
#         past_date = current_date - dt.timedelta(days=225)
#         risk_free_rate_df = dr.DataReader('^TNX', 'yahoo', past_date, current_date)
#         risk_free_rate_float = (risk_free_rate_df.iloc[len(risk_free_rate_df) - 1, 5]) / 100
#         print('RF rate:', round(risk_free_rate_float, 3))
#         market_return = 0.10
#         cost_of_equity = risk_free_rate_float + beta * (market_return - risk_free_rate_float)
#
#         # 2 cost of debt Kd *(1-t)
#         interest_exp = self.income['interestExpense'] / 1000000000
#         short_term_debt = self.balance['shortLongTermDebt'] / 1000000000
#         long_team_debt = self.balance['longTermDebt'] / 1000000000
#         cost_of_debt = interest_exp / (short_term_debt + long_team_debt)
#         income_b4tax = self.income['incomeBeforeTax'] / 1000000000
#         tax_exp = self.income['incomeTaxExpense'] / 1000000000
#         tax_rate = tax_exp / income_b4tax
#         tax_adj_cod = cost_of_debt * (1 - tax_rate)
#
#         # 3 weights of debt and equity
#         market_cap = self.stock_info.get("Market Cap")
#         if market_cap[-1] == 'T':
#             market_cap = float(market_cap.replace('T', '0')) * 1000  # 2 analyst projections
#         elif market_cap[-1] == 'B':
#             market_cap = float(market_cap.replace('B', '0'))  # 2 analyst projections
#         print(f'Market cap: {market_cap:} billions')
#
#         total_debt = short_term_debt + long_team_debt  # not very precise
#         total_capital = total_debt + market_cap
#         weight_debt = total_debt / total_capital
#         weight_equity = market_cap / total_capital
#
#         wacc = weight_equity * cost_of_equity + weight_debt * tax_adj_cod
#         required_return = sum(wacc)/len(wacc)
#
#         print('Weight of Equity', round(weight_equity[0],4))
#         print(f'Required return wacc: {round(required_return,3):}')
#         print('Weighted Avg. Cost of Capital:', round(required_return, 3))
#         print('S&P500 Avg. Yearly Market Return:', market_return)
#         return required_return
#
#     # perpetual growth and terminal value
#     def terminal_value(self):
#         perpetual_growth = 0.15
#         print('Assumption: perpetual growth', perpetual_growth), print('\n')
#         terminal_value = (fcf_est[7] * (1 + perpetual_growth)) / (required_return - perpetual_growth)
#         return terminal_value
#
#     def dataframe(self):
#         print('Discounted value:')
#
#         df = pd.DataFrame()
#         df.index = self.index_year
#         df['Year'] = ['past4','past3','past2','past1',
#                       'current','next1','next2','next3','terminal']
#         df['FreeCashflow'] = (fcf_est[0], fcf_est[1], fcf_est[2], fcf_est[3], fcf_est[4],
#                      fcf_est[5], fcf_est[6], fcf_est[7], terminal_value)
#
#         df['Revenue'] = revenue_est
#         df['Income'] = net_income_est
#         df['Period t'] = [0, 0, 0, 0, 0, 1, 2, 3, 3]
#         df['Discount r'] = (1 + required_return) ** df['Period t']
#         df['PresentValue'] = df['FreeCashflow'][4:] / df['Discount r'][4:]
#         print(f'Free Cash Flow Projections since {self.current}')
#         print('(in billions)')
#         print(df)
#         return df
#
#     def intrinsic_value(self):
#         current_price = si.get_live_price(ticker)
#         present_value = sum(dataframe['PresentValue'][4:])
#         intrinsic_value = present_value / self.shares_outstanding
#
#         print('Total Shares (in billions):', round(self.shares_outstanding,3))
#         print('Present Value (in billions):', round(present_value,3)), print('\n')
#         print('Intrinsic Value:  $', round(intrinsic_value, 2))
#         print('Current Price: $', round(current_price, 2))
#         return present_value
#
#
# ticker = 'tsla'
# print(f'{ticker} discounted cashflow modeling...', '\n')
#
# dcf = DCF(ticker)
# growth_rate = dcf.growth_rate()
# revenue_est = dcf.revenue_est()
# net_income_est = dcf.net_income_est()
# fcf_est = dcf.free_cashflow()
#
# required_return = dcf.required_return()
# terminal_value = dcf.terminal_value()
# dataframe = dcf.dataframe()
# intrinsic_value = dcf.intrinsic_value()