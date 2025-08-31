import streamlit as st
import requests
import pandas as pd
import time

# ================== CONFIG ==================
BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]  # store in secrets.toml
CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

def send_telegram_alert(message: str):
    """Send alert to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_price(symbol: str = "BTCUSDT") -> float:
    """Fetch live price from Binance"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

# ================== UI ==================
st.title("🚨 Multi-Coin Crypto Price Alert App")

# Use session_state to store alerts
if "alerts" not in st.session_state:
    st.session_state.alerts = []

with st.form("add_alert"):
    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.text_input("Symbol (e.g. BTCUSDT, ETHUSDT)", "BTCUSDT")
    with col2:
        target_price = st.number_input("Target Price", value=70000.0, step=100.0)
    with col3:
        direction = st.radio("Direction", ["Above", "Below"], horizontal=True)
    submitted = st.form_submit_button("➕ Add Alert")
    if submitted:
        st.session_state.alerts.append({"symbol": symbol.upper(),
                                        "target": target_price,
                                        "direction": direction,
                                        "triggered": False})

# Show current alerts
if st.session_state.alerts:
    st.subheader("📋 Active Alerts")
    df = pd.DataFrame(st.session_state.alerts)
    st.table(df[["symbol", "target", "direction", "triggered"]])

# Monitoring button
if st.button("▶ Start Monitoring"):
    st.success("Monitoring started... (check Telegram for alerts)")
    placeholder = st.empty()

    while True:
        results = []
        for alert in st.session_state.alerts:
            if alert["triggered"]:
                results.append(f"{alert['symbol']} already triggered ✅")
                continue

            price = get_price(alert["symbol"])
            condition = (
                (alert["direction"] == "Above" and price >= alert["target"]) or
                (alert["direction"] == "Below" and price <= alert["target"])
            )

            if condition:
                msg = f"🚨 {alert['symbol']} {alert['direction']} {alert['target']} | Current: {price}"
                send_telegram_alert(msg)
                alert["triggered"] = True
                results.append(msg + " ✅ (alert sent)")
            else:
                results.append(f"{alert['symbol']} @ {price} (waiting)")

        placeholder.write("\n".join(results))
        time.sleep(10)  # check every 10 sec
