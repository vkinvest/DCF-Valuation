import pandas as pd
import xlsxwriter

ticker = 'TSLA'
xls = pd.ExcelFile(f'{ticker}.xlsx')
income = pd.read_excel(xls, 'income').T
balance = pd.read_excel(xls, 'balance').T
cashflow = pd.read_excel(xls, 'cashflow').T

income.columns = income.iloc[0]
balance.columns = balance.iloc[0]
cashflow.columns = cashflow.iloc[0]

income = income[1:]
balance = balance[1:]
cashflow = cashflow[1:]

writer = pd.ExcelWriter(f'{ticker}_cleaned.xlsx', engine='xlsxwriter')

income.to_excel(writer, sheet_name='income')
balance.to_excel(writer, sheet_name='balance')
cashflow.to_excel(writer, sheet_name='cashflow')

writer.save()

