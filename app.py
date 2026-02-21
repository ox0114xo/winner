import streamlit as st
import pandas as pd

# --- App 頁面設定 ---
st.set_page_config(page_title="WinnerFlow 贏家資產導流", layout="centered")

st.title("🛡️ WinnerFlow 贏家決策系統")
st.markdown("### 從台股利潤，灌溉美股成長")

# --- 側邊欄：使用者輸入 ---
st.sidebar.header("📊 我的資產參數")
shares = st.sidebar.number_input("0050 持有股數", value=1602, step=100)
cost_price = st.sidebar.number_input("0050 買進成本 (TWD)", value=48.0, step=1.0)
current_price = st.sidebar.number_input("0050 目前市價 (TWD)", value=77.0, step=1.0)
qqq_now = st.sidebar.number_input("QQQ 現有資產 (USD)", value=25660, step=1000)
fx_rate = st.sidebar.number_input("目前匯率 (USD/TWD)", value=31.4, step=0.1)

st.sidebar.divider()
st.sidebar.header("📈 成長預測參數")
expected_return = st.sidebar.slider("QQQ 預期年化報酬率 (%)", min_value=1.0, max_value=25.0, value=11.0) / 100
years = st.sidebar.slider("預測年限 (年)", min_value=1, max_value=30, value=10)

# --- 核心邏輯計算 ---
total_profit = (current_price - cost_price) * shares
safety_margin = (current_price - cost_price) / current_price
transfer_25pct = (total_profit * 0.25) / fx_rate

# 動態判斷本金：如果安全水位大於 20% 才把資金灌入 QQQ
if safety_margin > 0.2:
    principal = qqq_now + transfer_25pct
else:
    principal = qqq_now

# --- 計算每年成長軌跡 (複利迴圈) ---
growth_data = []
for year in range(years + 1): # 從第 0 年算到設定的年限
    future_value = principal * ((1 + expected_return) ** year)
    growth_data.append({
        "年度": f"第 {year} 年", 
        "資產規模 (USD)": future_value
    })

# 轉換為 pandas DataFrame 供圖表使用
df_growth = pd.DataFrame(growth_data).set_index("年度")
final_future_value = df_growth["資產規模 (USD)"].iloc[-1]

# --- 介面顯示：贏家儀表板 ---
col1, col2 = st.columns(2)
with col1:
    st.metric("安全水位 (跌幅容忍度)", f"{safety_margin:.1%}")
with col2:
    st.metric("可搬家純利潤 (TWD)", f"${total_profit:,.0f}")

st.divider()

# --- 決策建議 ---
if safety_margin > 0.2:
    st.success(f"✅ **贏家信號：水位安全！**\n\n本季建議導流 **${transfer_25pct:,.0f} USD** (25% 獲利) 至 QQQ")
elif safety_margin > 0:
    st.warning("⚠️ **守備信號：護城河縮減。**\n\n獲利偏低，建議暫緩導流，固守基本盤。（以下預測將不包含此次導流資金）")
else:
    st.error("🚨 **虧損信號：目前帳面呈現虧損。**\n\n請重新評估 0050 持倉策略。（以下預測將不包含此次導流資金）")

st.info(f"🔮 預估 **{years} 年後** QQQ 資產將達：**${final_future_value:,.0f} USD** (以年化 {expected_return:.1%} 計算)")

# --- 視覺化圖表：折線圖 ---
st.markdown("#### 📈 歷年資產成長軌跡 (複利效應)")
# 使用 area_chart 讓底部有填色，視覺上更有「資產累積」的豐滿感
st.area_chart(df_growth)

