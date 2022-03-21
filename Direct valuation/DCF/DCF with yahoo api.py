import pandas as pd
import datetime as dt
import pandas_datareader as dr
import yahoo_fin.stock_info as si
import yfinance as yf
import statistics


# uses the past 4 years of data from yahoo finance
class DCF:
    def __init__(self, ticker):
        self.ticker = ticker

    def revenue():
        def growth_rate():
            growth_rate = statistics.mean((revenue.diff() / revenue.shift(1)).dropna())
            print(f'Revenue Growth Rate:', round(growth_rate, 2))
            return growth_rate

        growth = growth_rate()
        rev_5 = int(revenue[-1] * (1 + growth))
        rev_6 = int(rev_5 * (1 + growth))
        rev_7 = int(rev_6 * (1 + growth))
        rev_8 = int(rev_7 * (1 + growth))
        rev_9 = int(rev_8 * (1 + growth))

        df['Revenue'] = [revenue[0], revenue[1], revenue[2], revenue[3], rev_5, rev_6, rev_7, rev_8, rev_9, 'nan']
        return growth_rate, df['Revenue']

    def free_cashflow_firm():
        def fcff():
            EBIT = income['Operating Income']
            NCC = cashflow['Depreciation']
            wc_inv = balance['Total Current Assets'] - balance['Total Current Liabilities']
            fc_inv = cashflow['Capital Expenditures']
            change_wc = wc_inv - wc_inv.shift(1).fillna(0)
            change_fc = fc_inv - fc_inv.shift(1).fillna(0)
            tax = income['Income Tax Expense']

            FCFF = EBIT + NCC - change_wc - change_fc - tax
            return FCFF

        fcff = fcff()
        def fcff_margin():
            margin = statistics.mean(fcff / income['Total Revenue'])
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

    def wacc():
        # required return: WACC =  We *Ke + Wd *Kd *(1-t)
        def cost_of_equity():
            market_return = 0.10
            beta = stock_info.get('Beta (5Y Monthly)')
            rf_rate = dr.DataReader('^TNX', 'yahoo', past_date, today)['Adj Close'][-1]/100
            print('RF rate:', round(rf_rate, 2), '  Beta:', beta)

            ke = round(rf_rate + beta * (market_return - rf_rate), 2)
            print('Cost of equity', ke)
            return ke

        ke = cost_of_equity()
        total_debt = balance['Long Term Debt'] # todo data is incomplete from yahoo

        def cost_of_debt():
            interest_exp = income['Interest Expense']
            kd = (-interest_exp / total_debt).dropna()[-1]

            tax_rate = income['Interest Expense'] / income['Income Before Tax']
            tax_adj_kd = round(kd * (1 - tax_rate[-1]), 2)
            print('Cost of debt', tax_adj_kd)
            return tax_adj_kd

        tax_adj_kd = cost_of_debt()

        def weights():
            market_cap = (dr.get_quote_yahoo(ticker)['marketCap']/1000000)[0]
            total_capital = total_debt[-1] + market_cap
            w_debt = round(total_debt[-1] / total_capital, 3)
            w_equity = round(market_cap / total_capital, 3)
            return w_debt, w_equity

        w_debt, w_equity = weights()
        wacc = round((w_equity * ke + w_debt * tax_adj_kd), 2)

        print('Weight of Equity', w_equity, '   Weight of Equity', w_debt)
        print(f'Required return wacc: {round(wacc, 3):}')
        return wacc

    def present_value():
        def terminal_value():
            perpetuity_growth = 0.03
            terminal = (fcff[8] * (1 + perpetuity_growth)) / (wacc - perpetuity_growth)
            return terminal

        df['Time'] = (0, 0, 0, 0, 0, 1, 2, 3, 4, 4)
        df['FCFF'].iloc[-1] = terminal_value()
        df['Present Value'] = df['FCFF'][4:]/(1 + df['Time'][4:])
        print('\n', df)

        present_value = sum(df['Present Value'][4:])
        print(f'Present Value:', round(present_value, 2))
        return present_value

    def share_price():
        shares_outstanding = get.info['sharesOutstanding']/1000000
        share_price = round(present_value / shares_outstanding, 2)
        print('\n', f'Intrinsic Value:', share_price)
        return share_price


ticker = 'goog'
get = yf.Ticker(ticker)
balance = (get.balance_sheet / 1000000).T.sort_index()
income = (get.financials / 1000000).T.sort_index()
cashflow = (get.cashflow / 1000000).T.sort_index()


df = pd.DataFrame()
revenue = income['Total Revenue']
net_income = income['Net Income']

today = dt.date.today()
past_date = today - dt.timedelta(days=225)
stock_info = si.get_quote_table(ticker, dict_result=True)

dcf = DCF(ticker)
growth_rate, rev_df = dcf.revenue()
fcff = dcf.free_cashflow_firm()
wacc = dcf.wacc()
present_value = dcf.present_value()
share_price = dcf.share_price()