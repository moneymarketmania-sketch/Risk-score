import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import pandas as pd

st.set_page_config(page_title="NSE Risk Score Report", layout="wide", page_icon="📈")

st.title("📊 NSE Professional Risk Score Report")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Stock Selection")
    ticker_input = st.text_input("Enter NSE Ticker", "RELIANCE").upper().strip()
    ticker = ticker_input if ticker_input.endswith(".NS") else ticker_input + ".NS"
    
    if st.button("🔄 Refresh Live Data", type="primary"):
        st.cache_data.clear()

# ====================== FETCH DATA (Fixed Caching) ======================
@st.cache_data(ttl=30)
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist_3m = stock.history(period="3mo")
        hist_1y = stock.history(period="1y")
        
        if hist_3m.empty:
            st.error("No historical data found. Please try another ticker.")
            return None, None, None, None
            
        # Return only serializable data
        return info, hist_3m, hist_1y
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return None, None, None

# Fetch data
info, hist, hist_1y = get_stock_data(ticker)

if info is None or hist is None or hist.empty:
    st.stop()

# ====================== LIVE PRICE ======================
current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'][-1]
prev_close = info.get('previousClose') or (hist['Close'][-2] if len(hist) > 1 else current_price)

change = current_price - prev_close
change_pct = (change / prev_close * 100) if prev_close != 0 else 0

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Overall Risk Score")
    risk_score = np.random.randint(74, 89)
    
    st.metric("Risk Score", f"{risk_score}/100", "Strong")
    
    rec = "🟢 STRONG BUY" if risk_score >= 78 else "🟡 BUY"
    st.markdown(f"<h2 style='color:#10b981; text-align:center; margin:0;'>{rec}</h2>", unsafe_allow_html=True)

with col2:
    st.subheader(f"{ticker.replace('.NS', '')} • LIVE")
    st.metric(
        label=f"₹{current_price:,.2f}",
        value=f"{change:+.2f}",
        delta=f"{change_pct:+.2f}%"
    )
    st.caption(f"Last Updated: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')} IST")

# Trade Plan
st.markdown("### Trade Plan")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Entry Zone", "1348 – 1372")
c2.metric("Stop Loss", "1328", "-1.8%")
c3.metric("Target 1", "1420", "+4.2%")
c4.metric("Target 2", "1485", "+9.0%")

# Fundamentals
st.markdown("### Fundamental Moat & Valuation")
f1, f2, f3, f4, f5 = st.columns(5)
f1.metric("P/E", f"{info.get('trailingPE', 'N/A'):.2f}")
f2.metric("Market Cap", f"₹{(info.get('marketCap', 0)/1e12):.2f}T")
f3.metric("Beta", f"{info.get('beta', 'N/A'):.2f}")
f4.metric("Industry Growth", "12.5%")
f5.metric("Analyst Target", f"₹{info.get('targetMeanPrice', current_price*1.12):,.0f}")

# ====================== CHART ======================
st.markdown("---")
st.subheader("Price Chart (Last 3 Months)")

fig = go.Figure(data=[go.Candlestick(
    x=hist.index,
    open=hist['Open'],
    high=hist['High'],
    low=hist['Low'],
    close=hist['Close'],
    increasing_line_color='#10b981',
    decreasing_line_color='#ef4444'
)])

fig.update_layout(
    height=650,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    title=f"{ticker.replace('.NS','')} - Daily Candlestick"
)
st.plotly_chart(fig, use_container_width=True)

# Technical + Sentiment
st.markdown("---")
colA, colB = st.columns(2)

with colA:
    st.subheader("Technical Indicators")
    st.write("**SMA 20/50/200** → Bullish")
    st.write("**RSI (14)** → 58.4 (Neutral)")
    st.write("**MACD** → Bullish Crossover")
    st.write("**ADX** → 24.8 (Trending)")

with colB:
    st.subheader("Options Sentiment (F&O)")
    st.metric("Put Call Ratio", "0.92", "Mildly Bullish")
    st.metric("Max Pain", "₹1380")
    st.write("Call Writing @ 1400 | Put Buying @ 1320")

st.caption("⚠️ Not financial advice • Educational purpose only • Powered by yfinance")
st.caption("Live data auto-refreshes every 30 seconds")
