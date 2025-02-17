# Oil Macro Systematic Strategies Dashboard
This dashboard is infrastructure meant to assist the user in backtesting and trading systematic strategies in crude oil futures. It also contains sample trading strategies and is updated automatically on a daily basis. \
\
[DASHBOARD](https://docs.google.com/spreadsheets/d/1L342Ry5Iw-goGuJmwBVkNn1u6UZRKCzwKGlgyMtq6Ak/edit?gid=1875174327#gid=1875174327)\
[DEMO VIDEO -- creating a trading strategy](https://drive.google.com/file/d/1QN9YQprK8I1zcx8Q_GoD4n3zMW-dYMKs/view)\
\
The dashboard allows the user to build their own signals off of either futures price data or data pulled from FRED, which will be updated daily. A family of strategies is available for users to construct from their chosen signals. From here, a dashboard is provided which can be used to study how strategies can be combined, assess their historic risk and return, and track their performance over time. Finally, net positioning across the futures curve is tracked to assist the user in trading their strategies. This sheet is "live" and updates daily it uses a Google Cloud Function Backend combined with Google Apps Script. Example strategies are provided in the dashboard.

## Description of Components
### Dashboard
On the dashboard sheet, the user can view the historic performance of their created strategies and study how the strategies can be favorably combined. The user can weight the strategies and also select and remove strategies. The dashboard also aggregates the present positionong of the combined strategy across the futures curve on the present day to assist the user in trading the combined strategy.
### Strategy Construction
This page allows the user to take computed signals and combine them with trading rules to create strategies. The strategies considered here are a particular class of strategies that trade when the rolling t-value of a signal passes the low threshold, but remains below the high threshold. The positioning of the strategies are computed in a Google Cloud Function "RunStrategy". The user can customize the parameters of the trading strategy including the signal is used and the thresholds for initiating positioning.
### Signals
This is where the user can pull in the avaialble signals for trading. Provided here are baseline signals including the price-level, which could be used in momentum strategies, as well as carry. Also included is a leading indicator index, formed in the page "Leading Indicators". This is composed of several forward-looking macroeconomic indicators.
### Leading Indicators
This page showcases the sheet's ability to pull in data from FRED in order to construct trading signals. In this case, a set of variables that are thought to be leading indicators of the business cycle are provided. All of the variables are point-in-time, meaning they reflect information that would actually be tradeable on a given date. The calls to FRED are managed by Google Cloud functions "PullFredEconData" and "PullFredFinanceData".
## Description of Code Repository
The files found in this repository are the Python functions that are deployed to Google Cloud and are called by the dashboard to perform more advanced functionality. PullFredEconData.py and PullFredFinanceData.py pull data from FRED and do processing to make this data usable for trading strategies. In particular, they compute point-in-time data for each trading date where the data is the standard deviations of the variable over its 10-year mean. The file RunStrategy.py translates signals into trading strategy positioning based on very simple rules.  
