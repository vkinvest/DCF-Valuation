import pandas_datareader as web
import pandas as pd
import yahoo_fin.stock_info as si
import datetime as dt


tickers = si.tickers_sp500()

start = dt.datetime.now() - dt.timedelta(days=365)
end = dt.datetime.now()

sp500_df = web.DataReader('^GSPC', 'yahoo', start, end)
sp500_df['Pct Change'] = sp500_df['Adj Close'].pct_change()
sp500_return = (sp500_df['Pct Change'] + 1).cumprod()[-1]

return_list = []
final_df = pd.DataFrame(columns=['Ticker', 'Latest_Price', 'PE_Ratio', '52_week_Low'])


counter = 0
for ticker in tickers:
    df = web.DataReader(ticker, 'yahoo', start, end)
    df.to_csv(f'/Users/vl/Desktop/PycharmProjects/Finance/Fundamental/StockScreener/stock_data/{ticker}.csv')

    df['Pct Change'] = df['Adj Close'].pct_change()
    stock_return = (df['Pct Change'] + 1).cumprod()[-1]

    returns_compared = round((stock_return / sp500_return), 2)
    return_list.append(returns_compared)

    counter += 1
    if counter == 10:
        break

best_performers = pd.DataFrame(list(zip(tickers, return_list)), columns=['Ticker', 'Returns Compared'])
best_performers['Score'] = best_performers['Returns Compared'].rank(pct=True) * 100
best_performers = best_performers[best_performers['Score'] >= best_performers['Score'].quantile(0.7)]  # top 30%
print(best_performers)

for ticker in best_performers['Ticker']:
    try:
        df = pd.read_csv(f'/Users/vl/Desktop/PycharmProjects/Finance/Fundamental/StockScreener/stock_data/{ticker}.csv', index_col=0)
        mas = [150, 200]
        for ma in mas:
            df['SMA_' + str(ma)] = round(df['Adj Close'].rolling(window=ma).mean(), 2)

        latest_price = df['Adj Close'][-1]
        pe_ratio = float(si.get_quote_table(ticker)['PE Ratio (TTM)'])
        # peg_ratio = float(si.get_stats_valuation(ticker).iloc[4][1])
        # print(peg_ratio)
        ma150 = df['SMA_150'][-1]
        ma200 = df['SMA_200'][-1]
        low_52week = round(min(df['Low'][-(52*5):]), 2)
        high_52week = round(min(df['High'][-(52*5):]), 2)

        score = round(best_performers[best_performers['Ticker'] == ticker]['Score'].tolis()[0])
        print(score)

        condition_1 = latest_price > ma150 > ma200
        condition_2 = latest_price >= (1.3 * low_52week)
        condition_3 = latest_price >= (0.75 * high_52week)
        # condition_4 = pe_ratio < 40
        condition_5 = peg_ratio < 2

        if condition_1 and condition_2 and condition_3 and condition_5:
            final_df = final_df.append({'Ticker': ticker,
                                        'Latest_price': latest_price,
                                        'Score': score,
                                        'PE_Ratio': pe_ratio,
                                        'SMA_150': ma150,
                                        'SMA_200': ma200,
                                        '52_Week_Low': low_52week,
                                        '52_Week_high': high_52week}, ignore_index=True)
    except Exception as e:
        print(f'{e} for {ticker}')
print(final_df)
#%%
final_df.sort_values(by='Score', ascending=False)
pd.set_option('display.max_columns', 10)
print(final_df)
final_df.to_csv('final.csv')
