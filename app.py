import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Portfolio Risk Dashboard", page_icon="📈", layout="wide")
st.title("📈 Portfolio Risk Dashboard")
st.write("Enter your portfolio below to analyze risk, volatility, and get rebalancing suggestions.")

st.markdown("### Enter Your Portfolio")

tickers_input = st.text_input("Stock Tickers", placeholder="e.g. AAPL, GOOGL")
amounts_input = st.text_input("Amount Invested per Stock ($)", placeholder="e.g. 1000,2000")

period = st.selectbox("Time Period", ["6mo", "1y", "2y", "5y"], index=1)

if st.button("Analyze Portfolio", use_container_width=True):
    if tickers_input and amounts_input:
        tickers = [t.strip().upper() for t in tickers_input.split(",")]
        amounts = [float(a.strip()) for a in amounts_input.split(",")]
    
        if len(tickers) != len(amounts):
            st.error("Number of tickers and amounts must match.")
        else:
            st.success(f"Analyzing {tickers}")

            data = yf.download(tickers, period=period)["Close"]
            if isinstance(data, pd.Series):
                data = data.to_frame(name=tickers[0])
            if data.empty:
                st.error("Could not fetch the data, check your ticker symbols.")
            else:
                st.markdown("### Price History")
                st.line_chart(data)
                st.markdown("### Volatility Analysis")
                returns = data.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)

                vol_df = pd.DataFrame({
                    "Ticker": volatility.index,
                    "Annual Volatility": (volatility.values * 100).round(2)
                })

                fig_vol = px.bar(vol_df, x="Ticker", y="Annual Volatility", title="Annualized Volatility %", color="Annual Volatility", color_continuous_scale="RdYlGn_r")
                st.plotly_chart(fig_vol, use_container_width=True)

                st.markdown("### Sharpe Ratio")
                risk_free_rate = 0.05 / 252
                sharpe_ratios = (returns.mean() - risk_free_rate) / returns.std()

                sharpe_df = pd.DataFrame({
                    "Ticker": sharpe_ratios.index,
                    "Sharpe Ratio": sharpe_ratios.values.round(2)
                })

                fig_sharpe = px.bar(sharpe_df, x="Ticker", y="Sharpe Ratio", title="Sharpe Ratio by the Stock", color="Sharpe Ratio", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_sharpe, use_container_width=True)
                st.caption("Sharpe Ratio > 1 is pretty good, > 2 is great, and < 0 means the stock lost money relative to vulnerability.")

                st.markdown("### Max Drawdown")
                def max_drawdown(series):
                    roll_max = series.cummax()
                    drawdown = (series - roll_max) / roll_max
                    return drawdown.min()
                
                drawdowns = {ticker: max_drawdown(data[ticker]) for ticker in tickers}
                drawdown_df = pd.DataFrame({
                    "Ticker": list(drawdowns.keys()),
                    "Max Drawdown in %": [round(v * 100,2) for v in drawdowns.values()]
                })
    
                fig_dd = px.bar(drawdown_df, x="Ticker", y="Max Drawdown in %", title="Max Drawdown by Stock", color="Max Drawdown in %", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_dd, use_container_width=True)
                st.caption("Max Drawdown shows the worst peak-to-trough drop. Closer to 0 would be better")

                st.markdown("### Correlation Heatmap")
                corr = returns.corr()
                fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdYlGn", title="Stock Correlation Matrix")
                st.plotly_chart(fig_corr, use_container_width=True)
                st.caption("Correlation close to 1 means stocks move together, while close to -1 means they move opposite. Lower correlation yields better diversification of stocks.")
                
                st.markdown("### Monte Carlo Simulation")
                st.write("Simulating 1,000 possible portfolio outcomes over the next year.")

                num_simulations = 1000
                num_days = 252

                weights = np.array(amounts)/ sum(amounts)
                portfolio_returns = returns.dot(weights)
                mean_return = portfolio_returns.mean()
                std_return = portfolio_returns.std()

                simulations = np.zeros((num_days, num_simulations))
                initial_value = sum(amounts)

                for i in range(num_simulations):
                    daily_returns = np.random.normal(mean_return, std_return, num_days)
                    simulations[:, i] = initial_value * np.cumprod(1 + daily_returns)
                
                sim_df = pd.DataFrame(simulations)

                fig_mc = go.Figure()
                for i in range(0, num_simulations, 10):
                    fig_mc.add_trace(go.Scatter(y=sim_df[i], mode="lines", line=dict(width=0.5, color="rgba(100,149,237,0.1)"), showlegend=False))
                
                fig_mc.update_layout(title="Monte Carlo Simulation - Your Portfolio Value Over 1 Year", xaxis_title="Trading Days", yaxis_title="Portfolio Value $")
                st.plotly_chart(fig_mc, use_container_width=True)

                percentile_5 = np.percentile(simulations[-1], 5)
                percentile_50 = np.percentile(simulations[-1], 50)
                percentile_95 = np.percentile(simulations[-1], 95)

                m1, m2, m3 = st.columns(3)
                m1.metric("Worst Case - 5th Percentile", f"{percentile_5:,.0f}")
                m2.metric("Expected - 50th Percentile", f"{percentile_50:,.0f}")
                m3.metric("Best Case - 95th Percentile", f"{percentile_95:,.0f}")  
                st.caption("These aren't predictions, they are possibilities. This is the range of the market, simulated using historical data of returns.")

    else:
        st.warning("Please enter both tickers and amounts.")
