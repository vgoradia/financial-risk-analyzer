import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import anthropic

def calculate_risk_score(volatility, max_drawdowns, corr_matrix):
    avg_vol = volatility.mean()
    if avg_vol < 0.15:
        vol_score = 100
    elif avg_vol < 0.25:
        vol_score = 75
    elif avg_vol < 0.35:
        vol_score = 50
    elif avg_vol < 0.50:
        vol_score = 25
    else:
        vol_score = 10

    avg_drawdown = abs(np.mean(list(max_drawdowns.values())))
    if avg_drawdown < 0.10:
        dd_score = 100
    elif avg_drawdown < 0.20:
        dd_score = 75
    elif avg_drawdown < 0.35:
        dd_score = 50
    elif avg_drawdown < 0.50:
        dd_score = 25
    else:
        dd_score = 10
    
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    avg_corr = upper.stack().mean()
    if avg_corr < 0.3:
        corr_score = 100
    elif avg_corr < 0.5:
        corr_score = 75
    elif avg_corr < 0.7:
        corr_score = 50
    else:
        corr_score = 25

    final_score = int((vol_score * 0.4) + (dd_score * 0.4) + (corr_score * 0.2))
    return min(final_score, 100)
def generate_summary(tickers, volatility, sharpe_ratios, drawdowns, var_dollar, risk_score, port_total_return, bench_total_return, benchmark):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    
    vol_str = ", ".join([f"{t}: {v:.1%}" for t, v in zip(tickers, volatility.values)])
    sharpe_str = ", ".join([f"{t}: {v:.2f}" for t, v in zip(tickers, sharpe_ratios.values)])
    drawdown_str = ", ".join([f"{t}: {v:.1%}" for t, v in drawdowns.items()])
    
    prompt = f"""You are a friendly financial advisor explaining a portfolio analysis to an everyday investor.

Here is the portfolio data:
- Tickers: {', '.join(tickers)}
- Portfolio Safety Score: {risk_score}/100
- Annualized Volatility: {vol_str}
- Sharpe Ratios: {sharpe_str}
- Max Drawdowns: {drawdown_str}
- Daily Value at Risk (95%): ${var_dollar:,.0f}
- Portfolio Return: {port_total_return:.1f}%
- {benchmark} Return: {bench_total_return:.1f}%

Write a 4-5 sentence plain English summary that:
1. States how risky the portfolio is overall
2. Identifies the biggest risk driver
3. Mentions if they beat the market or not
4. Gives 1-2 specific actionable suggestions
Keep it conversational, clear, and helpful. No bullet points, just natural paragraphs."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

st.set_page_config(page_title="QuantRisk", page_icon="📈", layout="wide")
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #2d3250;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0d6efd, #4da6ff);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0b5ed7, #3d95ef);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 QuantRisk")
st.write("Enter your portfolio below to analyze risk, volatility, and get rebalancing suggestions.")

st.markdown("### Enter Your Portfolio")

tickers_input = st.text_input("Stock Tickers", placeholder="e.g. AAPL, GOOGL")
amounts_input = st.text_input("Amount Invested per Stock ($)", placeholder="e.g. 1000,2000")

period = st.selectbox("Time Period", ["6mo", "1y", "2y", "5y"], index=1)
benchmark = st.selectbox("Benchmark", ["SPY", "QQQ", "DIA"], index=0)

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
                returns = data.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)

                def max_drawdown(series):
                    roll_max = series.cummax()
                    drawdown = (series - roll_max) / roll_max
                    return drawdown.min()
                
                drawdowns = {ticker: max_drawdown(data[ticker]) for ticker in tickers}
                corr = returns.corr()

                risk_score = calculate_risk_score(volatility, drawdowns, corr)
                color = "#28a745" if risk_score >= 70 else "#ffc107" if risk_score >= 45 else "#dc3545"
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a2e, {color});
                                border-radius: 16px; padding: 2rem; text-align: center; margin-bottom: 1.5rem;">
                        <div style="font-size: 4rem; font-weight: 800; color: white;">
                            {risk_score}<span style="font-size: 2rem;">/100</span>
                        </div>
                        <div style="font-size: 1.1rem; color: #a0c4ff;">Portfolio Safety Score</div>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(risk_score / 100)

                st.markdown("### Price History")
                st.line_chart(data)

                st.markdown("### Volatility Analysis")
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
                drawdown_df = pd.DataFrame({
                    "Ticker": list(drawdowns.keys()),
                    "Max Drawdown in %": [round(v * 100, 2) for v in drawdowns.values()]
                })
                fig_dd = px.bar(drawdown_df, x="Ticker", y="Max Drawdown in %", title="Max Drawdown by Stock", color="Max Drawdown in %", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig_dd, use_container_width=True)
                st.caption("Max Drawdown shows the worst peak-to-trough drop. Closer to 0 would be better.")

                st.markdown("### Correlation Heatmap")
                fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdYlGn", title="Stock Correlation Matrix")
                st.plotly_chart(fig_corr, use_container_width=True)
                st.caption("Correlation close to 1 means stocks move together, while close to -1 means they move opposite. Lower correlation yields better diversification of stocks.")
                
                st.markdown("### Monte Carlo Simulation")
                st.write("Simulating 1,000 possible portfolio outcomes over the next year.")

                num_simulations = 1000
                num_days = 252

                weights = np.array(amounts) / sum(amounts)
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
                m1.metric("Worst Case - 5th Percentile", f"${percentile_5:,.0f}")
                m2.metric("Expected - 50th Percentile", f"${percentile_50:,.0f}")
                m3.metric("Best Case - 95th Percentile", f"${percentile_95:,.0f}")
                st.caption("These aren't predictions, they are possibilities. This is the range of the market, simulated using historical data of returns.")

                st.markdown("### Value at Risk")
                confidence_level = 0.95
                portfolio_returns_series = returns.dot(weights)
                var_95 = np.percentile(portfolio_returns_series, (1 - confidence_level) * 100)
                var_dollar = abs(var_95 * initial_value)

                v1, v2 = st.columns(2)
                v1.metric("Daily VaR 95% Confidence", f"${var_dollar:,.0f}")
                v2.metric("As % of Portfolio", f"{abs(var_95 * 100):.2f}%")
                st.caption("There is a 95% chance you won't lose more than this amount in a single day of trading.")


                st.markdown("### Suggestions for Rebalancing")
                current_weights = np.array(amounts) / sum(amounts)
                inverse_vol = 1 / volatility.values
                suggested_weights = inverse_vol / inverse_vol.sum()

                rebal_df = pd.DataFrame({
                    "Ticker": tickers,
                    "Current Weight %": (current_weights * 100).round(1),
                    "Suggested Weight %": (suggested_weights * 100).round(1)
                })

                st.dataframe(rebal_df, hide_index=True)
                st.caption("Suggested weights prevent risk by putting more to less volatile stocks.")

                st.markdown("### Benchmark Comparison")
                benchmark_data = yf.download(benchmark, period=period)["Close"]
                benchmark_returns = benchmark_data.squeeze().pct_change().dropna()

                portfolio_cumulative = (1 + portfolio_returns).cumprod()
                benchmark_cumulative = (1 + benchmark_returns).cumprod()

                comparison_df = pd.DataFrame({
                    "Portfolio": portfolio_cumulative.values,
                    "Benchmark": benchmark_cumulative.values[:len(portfolio_cumulative)]
                }, index=portfolio_cumulative.index)

                fig_bench = px.line(comparison_df, title=f"Portfolio vs {benchmark}")
                st.plotly_chart(fig_bench, use_container_width=True)

                port_total_return = (portfolio_cumulative.iloc[-1] - 1) * 100
                bench_total_return = (benchmark_cumulative.iloc[-1] -1) * 100

                b1,b2,b3 = st.columns(3)
                b1.metric("Portfolio Return", f"{port_total_return:.1f}%")
                b2.metric(f"{benchmark} Return", f"{bench_total_return:.1f}%")
                if port_total_return > bench_total_return:
                    b3.metric("Result", "Beat It!")
                else:
                    b3.metric("Result", "Underperformed.")

                st.markdown("### Portfolio Summary")
                with st.spinner("Generating a summary of your portfolio..."):
                    summary = generate_summary(tickers, volatility,sharpe_ratios, drawdowns, var_dollar, risk_score, port_total_return, bench_total_return, benchmark)
                st.info(summary)
    else:
        st.warning("Please enter both tickers and amounts.")
