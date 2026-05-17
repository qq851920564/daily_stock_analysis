import smtplib
from email.mime.text import MIMEText
import akshare as ak
import pandas as pd

# 你的配置（直接用就行，不用改）
EMAIL = "gelu.kam@foxmail.com"
PASSWORD = "attbrgfbjyoabeae"
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
STOCK_CODE = "000878"

def get_stock_data(symbol):
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="")
        return df
    except Exception as e:
        print(f"数据获取失败：{e}")
        return pd.DataFrame()

def short_term_analysis(df):
    if df.empty:
        return "⚠️ 数据获取失败，请检查网络或接口"

    close = df["收盘"].iloc[-1]
    ma5 = df["收盘"].rolling(5).mean().iloc[-1]
    ma10 = df["收盘"].rolling(10).mean().iloc[-1]
    ma20 = df["收盘"].rolling(20).mean().iloc[-1]
    vol = df["成交量"].iloc[-1]
    vol_ma5 = df["成交量"].rolling(5).mean().iloc[-1]

    # 均线信号
    ma_signal = "✅ 短线多头排列" if (ma5 > ma10 > ma20) else "🔴 短线空头排列"

    # RSI 14
    delta = df["收盘"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_val = rsi.iloc[-1]
    if rsi_val > 75:
        rsi_msg = "🔴 超买，警惕回落"
    elif rsi_val < 25:
        rsi_msg = "✅ 超卖，可关注反弹"
    else:
        rsi_msg = "➖ 正常区间"

    # KDJ
    low = df["最低"].rolling(9).min()
    high = df["最高"].rolling(9).max()
    rsv = (df["收盘"] - low) / (high - low) * 100
    k = rsv.ewm(span=3).mean()
    d = k.ewm(span=3).mean()
    kdj_msg = "✅ KDJ金叉 短线买入信号" if k.iloc[-1] > d.iloc[-1] else "🔴 KDJ死叉 短线卖出信号"

    # MACD
    ema12 = df["收盘"].ewm(span=12).mean()
    ema26 = df["收盘"].ewm(span=26).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9).mean()
    macd_msg = "✅ MACD多头" if dif.iloc[-1] > dea.iloc[-1] else "🔴 MACD空头"

    # 成交量
    vol_msg = "✅ 放量上涨" if vol > vol_ma5 * 1.2 else "➖ 量能正常"

    return f"""
【📈 短线交易分析报告】
代码：{STOCK_CODE}
收盘价：{close:.2f}

【均线】{ma_signal}
【RSI】{rsi_val:.1f} | {rsi_msg}
【KDJ】{kdj_msg}
【MACD】{macd_msg}
【成交量】{vol_msg}

【短线操作建议】
→ 金叉+多头=可低吸
→ 死叉+空头=规避
→ 超卖=关注
→ 超买=减仓
"""

def send_email(content):
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = "⚡【短线专用】每日股票分析报告"
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    print("开始获取数据...")
    df = get_stock_data(STOCK_CODE)
    print("开始分析...")
    result = short_term_analysis(df)
    print(result)
    send_email(result)