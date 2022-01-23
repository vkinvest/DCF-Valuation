import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics


def scatter():
    expense_revenue.describe()
    expense_revenue.plot(x='TotalExpenses', y='TotalRevenue', style='o')
    plt.title('Expenses vs Revenue')
    plt.xlabel('TotalExpenses')
    plt.ylabel('TotalRevenue')
    plt.show()


def regression():
    x = financials['TotalExpenses'].values.reshape(-1,1)
    y = financials['TotalRevenue'].values.reshape(-1,1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
    regressor.fit(x_train, y_train)
    print(regressor.intercept_, regressor.coef_)


def results(): # how to use class to simplify
    x = financials['TotalExpenses'].values.reshape(-1,1)
    y = financials['TotalRevenue'].values.reshape(-1,1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
    regressor.fit(x_train, y_train)
    y_pred = regressor.predict(x_test)
    df = pd.DataFrame({'Actual': y_test.tolist(), 'Predicted': y_pred.tolist()}, index = range(len(y_test)))
    print(df) # how to remove [] signs from the list
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))


ticker = 'TSLA'
financials = pd.read_excel(f'{ticker}_quarterly_financials.xlsx')[:-1]
expense_revenue = financials.filter(regex=r'TotalRevenue$|TotalExpenses').set_index(financials['name'])
regressor = LinearRegression()

scatter()
regression()
results()
