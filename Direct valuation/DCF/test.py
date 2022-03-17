import pandas as pd

import seaborn as sn
import matplotlib.pyplot as plt


# def get_regressor():
#     element = income.filter(regex=r'TotalRevenue|^CostOfRevenue|TotalExpenses|GrossProfit')
#     corr = (element / 1000).corr()
#     max_corr = corr['TotalRevenue'].nlargest(2).nsmallest(1)
#     regressor = max_corr.index.values[0]
#     selected = income.filter(regex=f'TotalRevenue|^{regressor}')
#     selected.plot(x=f'{regressor}', y='TotalRevenue', style='o')
#     plt.xlabel('CostOfRevenues') and plt.ylabel('TotalRevenue')
#     plt.title('Expenses vs Revenue') and plt.show()
#     return regressor
#
#
# def run_regression():
#     regression = LinearRegression()
#     revenue = (income['TotalRevenue'] / 1000).values.reshape(-1, 1)
#     regressor = (income[f'{get_regressor()}'] / 1000).values.reshape(-1, 1)
#     x_train, x_test, y_train, y_test = train_test_split(regressor, revenue, test_size=0.10, random_state=0)
#     regression.fit(x_train, y_train)
#
#     def result_accuracy():
#         y_pred = regression.predict(x_test)
#         accuracy = pd.DataFrame({'Actual': y_test.tolist(), 'Predicted': y_pred.tolist()},
#                                 index=range(len(y_test)))
#         print('Mean Absolute Error:', int(metrics.mean_absolute_error(y_test, y_pred)))
#         print('Mean Squared Error:', int(metrics.mean_squared_error(y_test, y_pred)))
#         print('Root Mean Squared Error:', int(np.sqrt(metrics.mean_squared_error(y_test, y_pred))))
#         print(accuracy)  # how to remove [] signs from the list
#
#     co_efficient = float(regression.coef_)
#     result_accuracy()
#     return co_efficient
#
#
# rate = run_regression()


from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
import seaborn as sn
import statistics

class A:
    def __init__(self, ticker):
        self.ticker = ticker
        self.income = 1
        self.regressor = LinearRegression()

    def get_a(self):
        def regressor():
            b = 'CostOfRevenue'
            return b

        def regression():
            revenue = (income['TotalRevenue'] / 1000000).values.reshape(-1, 1)
            regressor1 = (income[f'{regressor()}'] / 1000000).values.reshape(-1, 1)
            x_train, x_test, y_train, y_test = train_test_split(regressor1, revenue, test_size=0.10, random_state=0)
            self.regressor.fit(x_train, y_train)
            co_efficient = float(self.regressor.coef_)
            return co_efficient

        a = regression()
        return a

    def get(self):
        rev_est = self.analysts_est['Revenue Estimate'].iloc[1].filter(regex=r'Year')
        current_est = float(rev_est[-1].replace('B', '0'))  # 2 analyst projections
        next1_est = float(rev_est[-2].replace('B', '0'))

ticker = 'TSLA'
income = pd.read_excel(f'{ticker}_annual_financials.xlsx')[:-1].fillna(0).set_index('Date')
run = A(ticker)
a = run.get_a()
print(a)


net_income = income['NetIncome'] / 1000000
revenue = income['TotalRevenue'] / 1000

growth = (revenue.diff())/revenue

from sklearn import linear_model
reg = linear_model.LinearRegression()

reg.fit(growth.values.reshape(-1,1), growth.index.values.reshape(-1,1))
LinearRegression()

reg.coef_

growth = statistics.mean((revenue.diff()/revenue).dropna())










