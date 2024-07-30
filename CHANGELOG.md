## 2024-06-30

### Added
- Multiple Streamlit dashboards for the Algozen Backtesting Service, including real-time and historical status tracking.
- Custom CSS for light and dark themes in the dashboards.
- Functions for fetching website status, plotting status bars, and creating donut charts.
- Test script for fetching website status and saving results to a JSON file.
- Dependencies for matplotlib and streamlit-autorefresh.

## 2024-07-11

### Added
- Added appropriate checks and modulazrize the code into a clean and easy to understand format.
- Apply suggestions by github and converstations.
- Added code for latency and made graphs for them.
- The data is now being saved into csv instead of jsons.

## 2024-07-12
- Refactored the code into a table format for each URL now.
- Changed the logic into the correct one for uptime/downtine , pass/fail.

## 2024-07-13
- Added the tables for the previous 100 entries for each URL.
- Added scatterplots for easy visualisation of different uptimes, pass/fail and latency for data more than 1000 or 5000.


urls = [
    # Development URLs
    {"url": "http://dev.algozen.io/api/v2/backtest/backtest", "pass_method": "200 OK", "service_name": "Backtest", "service_type": "development"},
    {"url": "https://dev.algozen.io/api/v2/backtest/flow", "pass_method": "200 OK", "service_name": "Flow", "service_type": "development"},
    {"url": "https://dev.algozen.io/canvas", "pass_method": "200 OK", "service_name": "Canvas", "service_type": "development"},
    {"url": "https://dev.algozen.io/dashboard", "pass_method": "200 OK", "service_name": "Dashboard", "service_type": "development"},
    {"url": "https://dev.algozen.io/algo_view", "pass_method": "200 OK", "service_name": "AlgoView", "service_type": "development"},
    {"url": "https://dev.algozen.io/logicboard", "pass_method": "200 OK", "service_name": "LogicBoard", "service_type": "development"},
    
    # Staging URLs
    {"url": "https://staging.algozen.io/canvas", "pass_method": "200 OK", "service_name": "Canvas", "service_type": "staging"},
    {"url": "https://staging.algozen.io/dashboard", "pass_method": "200 OK", "service_name": "Dashboard", "service_type": "staging"},
    {"url": "https://staging.algozen.io/algo_view", "pass_method": "200 OK", "service_name": "AlgoView", "service_type": "staging"},
    {"url": "https://staging.algozen.io/logicboard", "pass_method": "200 OK", "service_name": "LogicBoard", "service_type": "staging"},
    
    # Production URLs
    {"url": "https://algozen.io/canvas", "pass_method": "200 OK", "service_name": "Canvas", "service_type": "production"},
    {"url": "https://algozen.io/dashboard", "pass_method": "200 OK", "service_name": "Dashboard", "service_type": "production"},
    {"url": "https://algozen.io/algo_view", "pass_method": "200 OK", "service_name": "AlgoView", "service_type": "production"},
    {"url": "https://algozen.io/logicboard", "pass_method": "200 OK", "service_name": "LogicBoard", "service_type": "production"},
]
