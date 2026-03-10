# 📈 QuantRisk

A web-based portfolio risk analysis tool that helps everyday investors understand their risk exposure using the same statistical methods used by professional fund managers — built with Python, Pandas, NumPy, Plotly, Streamlit, and Claude AI.

🔗 **Project Link:** https://finance-risk-analyzer.streamlit.app/

---

## Overview

Enter your stocks and investment amounts, and the dashboard instantly computes volatility, risk-adjusted returns, worst-case scenarios, and diversification metrics across your entire portfolio. Then AI synthesizes all of it into a plain English summary.

---

## Features

- **Portfolio Safety Score** — a single 0-100 score summarizing overall portfolio risk based on volatility, drawdown, and correlation
- **Price History** — interactive line chart of historical prices across all assets
- **Volatility Analysis** — annualized volatility per stock, color-coded by risk level
- **Sharpe Ratio** — measures return per unit of risk (>1 is good, >2 is great)
- **Max Drawdown** — worst peak-to-trough loss for each asset in the selected period
- **Correlation Heatmap** — shows how stocks move relative to each other to assess diversification
- **Monte Carlo Simulation** — runs 1,000 simulated market scenarios to show best case, expected, and worst case portfolio values over the next year
- **Value at Risk (VaR)** — the maximum you are likely to lose in a single trading day at 95% confidence, the same metric used by major banks and hedge funds
- **Benchmark Comparison** — compare your portfolio returns against SPY, QQQ, or DIA to see if you beat the market
- **Rebalancing Suggestions** — data-driven weight recommendations to reduce risk without sacrificing returns
- **AI Portfolio Summary** — AI reads all your metrics and writes a plain English explanation with actionable suggestions

---

## Tech Stack

- Python
- yfinance (real-time stock data)
- Pandas & NumPy (data processing & statistical analysis)
- Plotly (interactive visualizations)
- Streamlit (web app framework)
- Anthropic Claude API (AI-generated summaries)

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

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Example Usage

Enter tickers: `AAPL, TSLA, GOOGL`  
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
