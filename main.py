import yaml
import akshare as ak
import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_stock_data(symbol):
    try:
        if len(symbol) == 6:
            return ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20250101", adjust="")
        else:
            return yf.download(symbol, start="2025-01-01", interval="1d")
    except Exception as e:
        print(f"获取{symbol}数据失败: {e}")
        return pd.DataFrame()

def analyze_stock(df):
    if df.empty:
        return "⚠️ 数据获取失败，无法分析"
    last_close = df["Close"].iloc[-1]
    ma5 = df["Close"].rolling(5).mean().iloc[-1]
    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    if last_close > ma5 and ma5 > ma20:
        return f"✅ 看多信号：当前收盘价{last_close:.2f}，站上5日和20日均线，短期偏多"
    else:
        return f"⏳ 观望信号：当前收盘价{last_close:.2f}，未站上均线，建议观望"

def send_email(config, content):
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = "📈 每日股票分析报告"
    msg["From"] = config["email_user"]
    msg["To"] = config["email_to"]
    try:
        with smtplib.SMTP_SSL(config["email_host"], config["email_port"]) as server:
            server.login(config["email_user"], config["email_pass"])
            server.send_message(msg)
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    config = load_config()
    all_content = []
    for symbol in config["symbols"]:
        df = get_stock_data(symbol)
        res = analyze_stock(df)
        all_content.append(f"股票 {symbol} 分析结果：\n{res}\n---")
    final_content = "\n".join(all_content)
    print(final_content)
    if config["email_enable"]:
        send_email(config, final_content)
