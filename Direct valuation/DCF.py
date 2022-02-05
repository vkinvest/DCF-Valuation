import pandas as pd
import numpy as np
import datetime as dt
from datetime import date
import pandas_datareader as dr
import yahoo_fin.stock_info as si
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
import seaborn as sn
import statistics

class DCF:
    def __init__(self, ticker):
        self.ticker = ticker
        self.analysts_est = si.get_analysts_info(ticker)
        self.price = int(date.today().year)
        self.revenue = income['TotalRevenue'] / 1000
        self.net_income = income['NetIncome'] / 1000
        operating_cashflow = cashflow['CashFlowFromContinuingOperatingActivities'] / 1000
        capital_expenditures = cashflow['CapitalExpenditure'] / 1000
        self.fcf = operating_cashflow + capital_expenditures
        self.stock_info = si.get_quote_table(ticker, dict_result=True)
        self.data = si.get_quote_data(ticker)
        self.current = int(date.today().year)
        self.shares_outstanding = self.data.get('sharesOutstanding') / 1000000
        self.index_year = (self.current-4, self.current-3, self.current-2, self.current-1,
                           self.current, self.current+1, self.current+2, self.current+3, self.current+4)

    # projections to get free cash flow
    def growth_rate(self):
        rate = statistics.mean((self.revenue.diff()/self.revenue).dropna())
        return rate

    def revenue_est(self):
        current_est = self.revenue[-1] * (1 + growth_rate) # 2 analyst projections
        next1_est = current_est * (1 + growth_rate)
        next2_est = next1_est * (1 + growth_rate)  # 3 projections, based on avg. growth rate
        next3_est = next2_est * (1 + growth_rate)
        revenue_est = (int(self.revenue[3]), int(self.revenue[2]), int(self.revenue[1]), int(self.revenue[0]),
                       int(current_est), int(next1_est), int(next2_est), int(next3_est), 'nan')
        return revenue_est

    def net_income_est(self):
        def run_regression():
            regression = LinearRegression()
            revenue = (income['TotalRevenue'] / 1000).values.reshape(-1, 1)
            regressor = (income['NetIncome'] / 1000).values.reshape(-1, 1)
            x_train, x_test, y_train, y_test = train_test_split(regressor, revenue, test_size=0.10, random_state=0)
            regression.fit(x_train, y_train)

            co_efficient = float(regression.coef_)
            if co_efficient < 0:
                plt.figure(figsize=(12, 6)) and plt.plot(self.net_income[1:]) and plt.show()
                co_efficient = max(self.net_income / self.revenue) # or avg. / len(self.revenue)

            def result_accuracy():
                y_pred = regression.predict(x_test)
                accuracy = pd.DataFrame({'Actual': y_test.tolist(), 'Predicted': y_pred.tolist()},
                                        index=range(len(y_test)))
                print(accuracy)  # how to remove [] signs from the list
                print('Mean Absolute Error:', int(metrics.mean_absolute_error(y_test, y_pred)))
                print('Mean Squared Error:', int(metrics.mean_squared_error(y_test, y_pred)))
                print('Root Mean Squared Error:', int(np.sqrt(metrics.mean_squared_error(y_test, y_pred))))

            result_accuracy()
            return co_efficient

        net_income_margin = run_regression()
        net_income_5 = revenue_est[4] * net_income_margin  # current year, based on net income margin
        net_income_6 = revenue_est[5] * net_income_margin
        net_income_7 = revenue_est[6] * net_income_margin
        net_income_8 = revenue_est[7] * net_income_margin
        net_income_est = (int(self.net_income[3]), int(self.net_income[2]), int(self.net_income[1]), int(self.net_income[0]),
                          int(net_income_5), int(net_income_6), int(net_income_7), int(net_income_8), 'nan')
        return net_income_est

    def free_cashflow(self):
        operating_cashflow = cashflow['CashFlowFromContinuingOperatingActivities'] / 1000
        capital_expenditures = cashflow['CapitalExpenditure'] / 1000
        fcf = operating_cashflow + capital_expenditures
        fcf_margin = sum(fcf / self.net_income) / len(self.net_income)
        print('\n', f'Free Cashflow Margin: {round(fcf_margin, 3)}')

        fcf_4 = net_income_est[3] * fcf_margin
        fcf_5 = net_income_est[4] * fcf_margin
        fcf_6 = net_income_est[5] * fcf_margin
        fcf_7 = net_income_est[6] * fcf_margin
        fcf_8 = net_income_est[7] * fcf_margin
        fcf_est = [self.fcf[3], self.fcf[2], self.fcf[1], fcf_4, fcf_5, fcf_6, fcf_7, fcf_8, 'nan']
        return fcf_est

    # required return: WACC =  We *Ke + Wd *Kd *(1-t)
    def required_return(self):
        # 1 cost of equity: Ke = CAPM = Rf + beta * (Rm - Rf)
        beta = self.stock_info.get('Beta (5Y Monthly)')
        print('Beta:', beta)
        current_date = dt.date.today()
        past_date = current_date - dt.timedelta(days=225)
        risk_free_rate_df = dr.DataReader('^TNX', 'yahoo', past_date, current_date)
        risk_free_rate_float = (risk_free_rate_df.iloc[len(risk_free_rate_df) - 1, 5]) / 100
        print('RF rate:', round(risk_free_rate_float, 3))
        market_return = 0.10
        cost_of_equity = risk_free_rate_float + beta * (market_return - risk_free_rate_float)

        # 2 cost of debt Kd *(1-t)
        interest_exp = income['InterestExpense'] / 1000
        long_team_debt = balance['LongTermDebt'] / 1000
        short_term_debt = (balance['TotalDebt'] - long_team_debt) / 1000
        cost_of_debt = interest_exp / (short_term_debt + long_team_debt)
        ebt = (income['EBIT'] - interest_exp) / 1000
        tax_exp = (income['PretaxIncome'] - income['NetIncome']) / 1000
        tax_rate = tax_exp / ebt
        tax_adj_cod = cost_of_debt * (1 - tax_rate)

        # 3 weights of debt and equity
        market_cap = self.stock_info.get("Market Cap")
        if market_cap[-1] == 'T':
            market_cap = float(market_cap.replace('T', '0')) * 1000  # 2 analyst projections
        elif market_cap[-1] == 'B':
            market_cap = float(market_cap.replace('B', '0'))  # 2 analyst projections
        print(f'Market cap: {market_cap:} millions')

        total_debt = short_term_debt + long_team_debt  # not very precise
        total_capital = total_debt + market_cap
        weight_debt = total_debt / total_capital
        weight_equity = market_cap / total_capital

        wacc = (weight_equity * cost_of_equity + weight_debt * tax_adj_cod).dropna()
        required_return = sum(wacc)/len(wacc) #todo check wacc

        print('Weight of Equity', round(weight_equity[0],4))
        print(f'Required return wacc: {round(required_return,3):}')
        print('Weighted Avg. Cost of Capital:', round(required_return, 3))
        print('S&P500 Avg. Yearly Market Return:', market_return)
        return required_return

    # perpetual growth and terminal value
    def terminal_value(self):
        perpetual_growth = 0.05
        print('Assumption: perpetual growth', perpetual_growth), print('\n')
        terminal_value = (fcf_est[7] * (1 + perpetual_growth)) / (required_return - perpetual_growth)
        return terminal_value

    def dataframe(self):
        print('Discounted value:')

        df = pd.DataFrame()
        df.index = self.index_year
        df['Year'] = ['past4', 'past3', 'past2', 'past1',
                      'current', 'next1', 'next2', 'next3', 'terminal']
        df['FCFF'] = (int(fcf_est[0]), int(fcf_est[1]), int(fcf_est[2]), int(fcf_est[3]), int(fcf_est[4]),
                     int(fcf_est[5]), int(fcf_est[6]), int(fcf_est[7]), terminal_value)

        df['Revenue'] = revenue_est
        df['Income'] = net_income_est
        df['Period t'] = [0, 0, 0, 0, 0, 1, 2, 3, 3]
        df['Discount r'] = round((1 + required_return) ** df['Period t'], 2)
        df['PresentValue'] = round(df['FCFF'][4:] / df['Discount r'][4:], 2)
        print(f'Free Cash Flow Projections since {self.current}')
        print('(in millions)')
        print(df)
        return df

    def intrinsic_value(self):
        current_price = si.get_live_price(ticker)
        present_value = sum(dataframe['PresentValue'][4:])
        intrinsic_value = present_value / self.shares_outstanding

        print('Total Shares (in millions):', int(self.shares_outstanding))
        print('Present Value (in millions):', round(present_value, 3)), print('\n')
        print('Intrinsic Value:  $', round(intrinsic_value, 2))
        print('Current Price: $', round(current_price, 2))
        return present_value


ticker = 'tsla'
income = pd.read_excel(f'{ticker}_annual_financials.xlsx')[:-1].fillna(0).set_index('Date')
balance = pd.read_excel(f'{ticker}_annual_balance-sheet.xlsx')[:-1].fillna(0).set_index('Date')
cashflow = pd.read_excel(f'{ticker}_annual_cash-flow.xlsx')[:-1].fillna(0).set_index('Date')
print(f'{ticker} discounted cashflow modeling...', '\n')

dcf = DCF(ticker)
growth_rate = dcf.growth_rate()

revenue_est = dcf.revenue_est()
net_income_est = dcf.net_income_est()
fcf_est = dcf.free_cashflow()

required_return = dcf.required_return()
terminal_value = dcf.terminal_value()
dataframe = dcf.dataframe()
intrinsic_value = dcf.intrinsic_value()


