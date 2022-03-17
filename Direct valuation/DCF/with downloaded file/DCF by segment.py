import pandas as pd
import statistics

ticker = 'TSLA'
xls = pd.ExcelFile(f'{ticker}_cleaned.xlsx')

index = 'Unnamed: 0'
income = (pd.read_excel(xls, 'income')).set_index(index)
balance = (pd.read_excel(xls, 'balance')).set_index(index)
cashflow = (pd.read_excel(xls, 'cashflow')).set_index(index)

growth = pd.DataFrame()
mean = pd.DataFrame()
revenue = income[income.columns[0:8]]
for col in revenue.columns:
    print(col)
    growth[col] = revenue[col].diff()/revenue[col].shift(1)

    # mean[col] = [x for x in growth[col] if pd.isnull(x) == False]

# growth.replace('nan', 0).dropna()



# segment1 = pd.DataFrame(income[income.columns[1]])
# segment2 = pd.DataFrame(income[income.columns[2]])
# segment3 = pd.DataFrame(income[income.columns[3]])

