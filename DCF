import yahoo_fin.stock_info as si
import pandas as pd
import datetime as dt
from datetime import date
import pandas_datareader as dr


## initial
ticker = 'viac'
print(ticker)
# input('Enter ticker: ')
print('\n')
print('Start discounted cash flow modeling...')

balance_sheet = si.get_balance_sheet(ticker).transpose()
income_statement = si.get_income_statement(ticker).transpose()
cashflow_statement = si.get_cash_flow(ticker).transpose()
analysts_est = si.get_analysts_info(ticker)
current = int(date.today().year)

#%% projections to get free cash flow
# 1 growth rate
revenue = income_statement['totalRevenue'] / 1000000000
growth3 = (revenue[2] - revenue[3]) / revenue[3]  # 3 historical growth rates
growth2 = (revenue[1] - revenue[2]) / revenue[2]  # todo how to loop growth rates
growth1 = (revenue[0] - revenue[1]) / revenue[1]
growth_est = analysts_est['Growth Estimates'].transpose().iloc[1]  # 2 analysts projections
growth_0 = float(growth_est[2].replace('%', '0')) / 100
growth_1 = float(growth_est[3].replace('%', '0')) / 100
avg_growth_rate = (growth_1 + growth_0 + growth1 + growth2 + growth3) / 5
#all_growth = [avg_growth_rate, avg_growth_rate, avg_growth_rate, growth_1, growth_0, growth1, growth2, growth3]
#get_fcf['Growth Rates'] = all_growth

# 2 revenues
rev_est = analysts_est['Revenue Estimate'].iloc[1]
rev_0 = float(rev_est[-1].replace('B', '0'))  # 2 analyst projections
rev_1 = float(rev_est[-2].replace('B', '0'))
rev_2 = rev_0 * (1 + avg_growth_rate)  # 3 projections, based on avg. growth rate
rev_3 = rev_1 * (1 + avg_growth_rate)
all_rev = (rev_3, rev_2, rev_1, rev_0, revenue[0], revenue[1], revenue[2], revenue[3])

# 3 net income
income = income_statement['netIncome'] / 1000000000
income_margin = min(income / revenue)
income_0 = rev_0 * income_margin  # based on net income margin
income_1 = rev_1 * income_margin
income_2 = rev_2 * income_margin
income_3 = rev_3 * income_margin
all_income = (income_3, income_2, income_1, income_0, income[0], income[1], income[2], income[3])

# 4 free cash flow
operating_cashflow = cashflow_statement['totalCashFromOperatingActivities'] / 1000000000
capital_expenditures = cashflow_statement['capitalExpenditures'] / 1000000000
fcf = operating_cashflow + capital_expenditures
fcf_margin = min(fcf / income)  # based on fcf/netIncome margin
print(f'Free Cashflow Margin: {round(fcf_margin,3)}')

fcf_0 = income_0 * fcf_margin
fcf_1 = income_1 * fcf_margin
fcf_2 = income_2 * fcf_margin
fcf_3 = income_3 * fcf_margin
all_fcf = (fcf_3, fcf_2, fcf_1, fcf_0, fcf[0], fcf[1], fcf[2], fcf[3])

# all projections dataframe
get_fcf = pd.DataFrame()
get_fcf['Year'] = [current + 3, current + 2, current + 1, current, current-1, current-2, current-3, current-4]
get_fcf['Revenue'] = all_rev
get_fcf['Income'] = all_income
get_fcf['Free Cashflow'] = all_fcf
print('Projections: next 4 years free cash flow')
print('(in billions)')
print(get_fcf), print('\n')

#%% required return: WACC =  We *Ke + Wd *Kd *(1-t)
# 1 cost of equity: Ke = CAPM = Rf + beta * (Rm - Rf)
# beta
stock_info = si.get_quote_table(ticker, dict_result=True)
beta = stock_info.get('Beta (5Y Monthly)')
print('Beta:', beta)

# risk free rate
current_date = dt.date.today()
past_date = current_date - dt.timedelta(days=225)
risk_free_rate_df = dr.DataReader('^TNX', 'yahoo', past_date, current_date)
risk_free_rate_float = (risk_free_rate_df.iloc[len(risk_free_rate_df) - 1, 5]) / 100
print('RF rate:', round(risk_free_rate_float, 3))
# avg_return of the market
market_return = 0.10

# costs
cost_of_equity = risk_free_rate_float + beta * (market_return - risk_free_rate_float)
interest_exp = income_statement['interestExpense'] / 1000000000
short_term_debt = balance_sheet['shortLongTermDebt'] / 1000000000
long_team_debt = balance_sheet['longTermDebt'] / 1000000000
cost_of_debt = interest_exp / (short_term_debt + long_team_debt)
income_b4tax = income_statement['incomeBeforeTax'] / 1000000000
tax_exp = income_statement['incomeTaxExpense'] / 1000000000
tax_rate = tax_exp / income_b4tax
tax_adj_cod = cost_of_debt * (1 - tax_rate)

# 3 weights
market_cap = stock_info.get("Market Cap")
if market_cap[-1] == 'T':
    market_cap = float(market_cap.replace('T', '0')) * 1000  # 2 analyst projections
elif market_cap[-1] == 'B':
    market_cap = float(market_cap.replace('B', '0'))  # 2 analyst projections
print(f'Market Cap: {market_cap:,}')  # todo this is useful

total_debt = short_term_debt + long_team_debt  # not very precise
total_capital = total_debt + market_cap
weight_debt = total_debt / total_capital
weight_equity = market_cap / total_capital
#%%
wacc = weight_debt * cost_of_debt * (1 - tax_rate) + weight_equity * cost_of_equity
#print(wacc)
required_return = wacc[0]  # +wacc[1]+wacc[2]+wacc[3]+wacc[4]+wacc[5])/5
#%%
## perpetual growth and terminal value
data = si.get_quote_data(ticker)
shares_outstanding = data.get('sharesOutstanding') / 1000000000
print('Total Shares:', round(shares_outstanding,3))
perpetual_growth = 0.05

# print('Cost of Equity:', round(cost_of_equity, 4))
# print('Cost of Debt:', round(-cost_of_debt[0], 4))
print('Weight of Debt:', round(weight_debt[0], 3))
# print('Weight of Equity', round(weight_equity[0],4))
print('Weighted Avg. Cost of Capital:', round(required_return,3))
print('S&P500 Avg. Yearly Market Return:', market_return)
print('Assumption: perpetual growth rate:', perpetual_growth), print('\n')

terminal_value = (fcf[0] * (1 + perpetual_growth)) / (required_return - perpetual_growth)  # @end of 4th year

#%% dataframe
print('Discounted value:')
df = pd.DataFrame()
df.index = [current + 3, current + 3, current + 2, current + 1, current]
df['time'] = [4, 4, 3, 2, 1]
fcf_est = (terminal_value, fcf_3, fcf_2, fcf_1, fcf_0)
df['Free Cashflow'] = fcf_est
df['Discount Factor'] = (1 + required_return) ** df['time']
df['Present Value'] = df['Free Cashflow'] / df['Discount Factor']
# df[' '] = ['Terminal value', ' ', ' ', ' ', '']
print(df)
#%%
present_value = sum(df['Present Value'])
intrinsic_value = present_value / shares_outstanding
current_price = si.get_live_price(ticker)


print('Present Value:', round(present_value,3)), print('\n')
print('Intrinsic Value:  $', round(intrinsic_value, 2))
print('Current Price: $', round(current_price, 2))
