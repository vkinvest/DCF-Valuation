import pandas as pd
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

    @staticmethod
    def revenue_est():
        revenue = income['TotalRevenue'] / 1000
        growth_rate = statistics.mean((revenue.diff() / revenue.shift(1)).dropna())
        current_est = int(revenue[-1] * (1 + growth_rate))  # 2 analyst projections
        next1_est = int(current_est * (1 + growth_rate))
        next2_est = int(next1_est * (1 + growth_rate))  # 3 projections, based on avg. growth rate
        next3_est = int(next2_est * (1 + growth_rate))
        df['Revenue'] = [revenue[3], revenue[2], revenue[1], revenue[0], current_est, next1_est, next2_est, next3_est, 'nan']
        return df['Revenue']

    @staticmethod
    def free_cashflow(): # todo which formular is best
        def net_income_est():
            revenue_est = dcf.revenue_est()
            net_income = income['NetIncome'] / 1000

            income_item = income.filter(regex=r'^NetIncome$|^TotalRevenue$')
            net_income_margin = statistics.mean((income['NetIncome'] / income['TotalRevenue']))
            if net_income_margin < 0:  # todo what if many years of negative net income
                # print(f'Net income to revenue margin: {net_income_margin}')
                negative_income = income_item[income_item['NetIncome'] < 0].index
                income_item = income_item.drop(negative_income)  # assuming enter stable business stage
                net_income_margin = statistics.mean((income_item['NetIncome'] / income_item['TotalRevenue']))
                print(f'Negative net income margin replaced by: {net_income_margin}')

            current_net_income = int(revenue_est[4] * net_income_margin)
            net_income_6 = int(revenue_est[5] * net_income_margin)
            net_income_7 = int(revenue_est[6] * net_income_margin)
            net_income_8 = int(revenue_est[7] * net_income_margin)
            df['NetIncome'] = (net_income[3], net_income[2], net_income[1], net_income[0],
                                current_net_income, net_income_6, net_income_7, net_income_8, 'nan')
            return df['NetIncome']

        def calculate_fcff():
            wc_inv = balance['CurrentAssets'] - balance['CurrentLiabilities']
            fc_inv = cashflow['CapitalExpenditure']
            inflows = {
                'EBIT': income['EBIT'],
                'NCC': income['ReconciledDepreciation'],
                'new_borrowing': cashflow['FinancingCashFlow']
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

        net_income_est = net_income_est()
        fcff_margin = fcff_margin()
        fcf_4 = int(net_income_est[3] * fcff_margin)
        fcf_5 = int(net_income_est[4] * fcff_margin)
        fcf_6 = int(net_income_est[5] * fcff_margin)
        fcf_7 = int(net_income_est[6] * fcff_margin)
        fcf_8 = int(net_income_est[7] * fcff_margin)

        operating_cashflow = cashflow['CashFlowFromContinuingOperatingActivities'] / 1000
        capital_expenditures = cashflow['CapitalExpenditure'] / 1000
        fcf = operating_cashflow + capital_expenditures
        df['FCFF'] = [fcf[3], fcf[2], fcf[1], fcf_4, fcf_5, fcf_6, fcf_7, fcf_8, 'nan']

        return df['FCFF']

    def discount_factor(self):
        # required return: WACC =  We *Ke + Wd *Kd *(1-t)
        # 1 cost of equity: Ke = CAPM = Rf + beta * (Rm - Rf)
        stock_info = si.get_quote_table(ticker, dict_result=True)
        beta = stock_info.get('Beta (5Y Monthly)')
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
        market_cap = stock_info.get("Market Cap")
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
        required_return = sum(wacc) / len(wacc)  # todo check wacc

        print('Weight of Equity', round(weight_equity[0], 4))
        print(f'Required return wacc: {round(required_return, 3):}')
        print('Weighted Avg. Cost of Capital:', round(required_return, 3))
        print('S&P500 Avg. Yearly Market Return:', market_return)
        return required_return

    # perpetual growth and terminal value
    def intrinsic_value(self):
        required_return = dcf.discount_factor()

        def terminal_value():
            perpetual_growth = 0.035
            print('Assumption: perpetual growth', perpetual_growth), print('\n')
            value = (df['FCFF'][7] * (1 + perpetual_growth)) / (required_return - perpetual_growth)
            df['FCFF'].iloc[-1] = value
            return value

        def present_value():
            terminal_value()

            df.index = (current - 4, current - 3, current - 2, current - 1, current, current + 1, current + 2, current + 3, current + 4)
            df['Period t'] = [0, 0, 0, 0, 0, 1, 2, 3, 3]
            df['Discount r'] = (1 + required_return) ** df['Period t']
            df['PresentValue'] = df['FCFF'][4:] / df['Discount r'][4:]
            df['Year'] = ['past4', 'past3', 'past2', 'past1', 'current', 'next1', 'next2', 'next3', 'terminal']
            print('(in millions)')
            print(df)
            return df

        present_value()
        current_price = si.get_live_price(ticker)
        present_value = sum(df['PresentValue'][4:])

        quote = si.get_quote_data(ticker)
        shares_outstanding = quote.get('sharesOutstanding') / 1000000
        intrinsic_value = present_value / shares_outstanding

        print('Total Shares (in millions):', int(shares_outstanding))
        print('Present Value (in millions):', round(present_value, 3)), print('\n')
        print('Intrinsic Value:  $', round(intrinsic_value, 2))
        print('Current Price: $', round(current_price, 2))
        return present_value


ticker = 'tsla'
df = pd.DataFrame()
current = int(date.today().year)
print(f'Free Cash Flow Projections Since Year{current}')

income = pd.read_excel(f'{ticker}_annual_financials.xlsx')[:-1].fillna(0).set_index('Date')
balance = pd.read_excel(f'{ticker}_annual_balance-sheet.xlsx')[:-1].fillna(0).set_index('Date')
cashflow = pd.read_excel(f'{ticker}_annual_cash-flow.xlsx')[:-1].fillna(0).set_index('Date')

dcf = DCF(ticker)
dcf.free_cashflow()
dcf.intrinsic_value()
