import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as py
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Portfolio Risk Dashboard", page_icon="📈", layout="wide")
st.title("📈 Portfolio Risk Dashboard")
st.write("Enter your portfolio below to analyze risk, volatility, and get rebalancing suggestions.")

st.markdown("### Enter Your Portfolio")

tickers_input = st.text_input("Stock Tickers", placeholder="e.g. AAPL, GOOGL")
amounts_input = st.text_input("Amount Invested per Stock ($)", placeholder="e.g. 1000,2000")

if st.button("Analyze Portfolio", use_container_width=True):
    if tickers_input and amounts_input:
        tickers = [t.strip().upper() for t in tickers_input.split(" ,")]
        amounts = [float(a.strip()) for a in amounts_input.split(" ,")]
    
    if len(tickers) != len(amounts):
        st.error("Number of tickers and amounts must match.")
    else:
        st.success(f"Analyzing {tickers}")
else:
    st.warning("Please enter both tickers and amounts.")
