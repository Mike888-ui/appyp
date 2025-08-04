import streamlit as st
import pandas as pd
import os
from collections import Counter

# 設定資料檔案路徑
csv_file = "ai_train_history.csv"

# 初始化資料
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["result"])
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
else:
    df = pd.read_csv(csv_file, encoding='utf-8-sig')

st.title("百家樂 Web 比對分析")

# ===== 1. 輸入區 =====
col1, col2 = st.columns([2,1])
with col1:
    result = st.selectbox("請選擇當局結果", ["", "莊", "閒", "和"])
with col2:
    add_btn = st.button("送出")
    del_btn = st.button("刪除上一筆")

# ===== 2. 新增紀錄功能 =====
msg = ""
if add_btn:
    if result:
        df = pd.concat([df, pd.DataFrame({"result":[result]})], ignore_index=True)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        msg = f"✅ 已記錄：{result}"
    else:
        msg = "❌ 請先選擇本局結果！"

if del_btn:
    if len(df) > 0:
        deleted = df.iloc[-1]["result"]
        df = df.iloc[:-1]
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        msg = f"🗑️ 已刪除上一筆紀錄：{deleted}"
    else:
        msg = "⚠️ 沒有資料可以刪除"

if msg:
    st.info(msg)

# ===== 3. 比對預測 =====
def ai_predict_next_adviceN_only(df, N=3):
    advs = df['result'].astype(str).tolist()
    now_count = min(len(advs), N)
    if len(advs) < N:
        return '暫無相關數據資料', ''
    last_n = advs[-now_count:]
    matches = []
    for i in range(len(advs) - now_count):
        if advs[i:i+now_count] == last_n:
            if i + now_count < len(advs):
                matches.append(advs[i + now_count])
    if not matches:
        return '暫無相關數據資料', ''
    stat = Counter(matches)
    most, cnt = stat.most_common(1)[0]
    percent = int(cnt / len(matches) * 100)
    show_detail = f"比對到的數量結果：莊：{stat.get('莊',0)}筆  閒：{stat.get('閒',0)}筆  和：{stat.get('和',0)}筆"
    return f"{most} ({percent}%)「{show_detail}」", f"{percent}%"

st.divider()
st.subheader("比對預測區")

pred_3, rate_3 = ai_predict_next_adviceN_only(df, N=3)
pred_6, rate_6 = ai_predict_next_adviceN_only(df, N=6)

st.write("比對預測 (3局)：", pred_3)
st.write("比對預測 (6局)：", pred_6)
st.write("比對正確率：", rate_6)

# ===== 4. 儲存紀錄 =====
if st.button("儲存紀錄(Excel)"):
    excel_out = csv_file.replace('.csv', '.xlsx')
    df.to_excel(excel_out, index=False)
    st.success(f"已將本次紀錄存為 {excel_out}")

# ===== 5. 歷史紀錄區 =====
st.divider()
st.subheader("歷史記錄")
if len(df) == 0:
    st.write("尚無紀錄")
else:
    for i, row in df.iterrows():
        st.write(f"{i+1}. {row['result']}")
