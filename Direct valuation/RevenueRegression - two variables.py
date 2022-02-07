import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics


class TwoVariablesRegression:

    def __init__(self, ticker):
        self.ticker = ticker
        self.income = pd.read_excel(f'{ticker}_annual_financials.xlsx')[:-1]#.set_index('Date')
        self.expense_revenue = self.income.filter(regex=r'Date|TotalRevenue$|TotalExpenses').set_index('Date')
        self.expense = self.income['TotalExpenses'].values.reshape(-1, 1)
        self.revenue = self.income['TotalRevenue'].values.reshape(-1, 1)
        self.regressor = LinearRegression()
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.expense, self.revenue, test_size=0.2, random_state=0)

    def scatter(self):
        self.expense_revenue.describe()
        self.expense_revenue.plot(x='TotalExpenses', y='TotalRevenue', style='o')
        plt.title('Expenses vs Revenue')
        plt.xlabel('TotalExpenses')
        plt.ylabel('TotalRevenue')
        plt.show()

    def regression(self):
        self.regressor.fit(self.x_train, self.y_train)
        print(f'Intercept:{self.regressor.intercept_}', f'Coefficient: {self.regressor.coef_}')

    def results(self):
        y_pred = self.regressor.predict(self.x_test)
        df = pd.DataFrame({'Actual': self.y_test.tolist(), 'Predicted': y_pred.tolist()}, index=range(len(self.y_test)))
        print(df)  # how to remove [] signs from the list
        print('Mean Absolute Error:', metrics.mean_absolute_error(self.y_test, y_pred))
        print('Mean Squared Error:', metrics.mean_squared_error(self.y_test, y_pred))
        print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(self.y_test, y_pred)))


t = TwoVariablesRegression('tsla')
t.scatter()
t.regression()
t.results()