## 📈 Portfolio Risk Dashboard

A web-based portfolio risk analysis tool that helps everyday investors understand their risk exposure using the same statistical methods used by professional fund managers — built with Python, Pandas, NumPy, Plotly, and Streamlit.

🔗 **Project Link:**

---

## Overview

Most retail investors buy stocks without understanding the risk they're taking on. This tool bridges that gap by giving anyone the ability to analyze their portfolio the same way hedge funds and institutional investors do — for free.

Enter your stocks and investment amounts, and the dashboard instantly computes volatility, risk-adjusted returns, worst-case scenarios, and diversification metrics across your entire portfolio.

---

## Features

- **Portfolio Input** — enter any combination of stock tickers and investment amounts
- **Price History** — interactive line chart of historical prices across all assets
- **Volatility Analysis** — annualized volatility per stock, color-coded by risk level
- **Sharpe Ratio** — measures return per unit of risk (>1 is good, >2 is great)
- **Max Drawdown** — worst peak-to-trough loss for each asset in the selected period
- **Correlation Heatmap** — shows how stocks move relative to each other to assess diversification
- **Monte Carlo Simulation** — runs 1,000 simulated market scenarios to show best case, expected, and worst case portfolio values over the next year
- **Multiple Time Periods** — analyze across 6 months, 1 year, 2 years, or 5 years of data

---

## Tech Stack

- Python
- yfinance
- Pandas
- NumPy
- Plotly 
- Streamlit

---

## Run Locally
```bash
git clone https://github.com/vgoradia/financial-risk-analyzer.git
cd financial-risk-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
---

## Example Usage

Enter tickers: `AAPL, TSLA, GOOGL.`  
Enter amounts: `1000, 2000, 1500`  
Select time period: `1y`  
Click **Analyze Portfolio**

---

## Project Structure
```
financial-risk-analyzer/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
└── README.md
```

---
