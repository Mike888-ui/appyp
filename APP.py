import streamlit as st
import pandas as pd
import csv, os
from collections import Counter

# 檔案名稱
csv_file = os.path.join(os.path.dirname(__file__), 'ai_train_history.csv')

# 如果沒有就新建，有就保留
if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['advice'])

st.set_page_config(page_title="百家樂極簡記錄", layout="centered")
st.title("百家樂極簡記錄（比對模式）")

if 'round_log' not in st.session_state:
    st.session_state.round_log = []

def ai_predict_next_adviceN_only(csvfile, N=3):
    if not os.path.exists(csvfile):
        return '暫無相關數據資料', ''
    df = pd.read_csv(csvfile, encoding='utf-8-sig')
    if 'advice' not in df.columns:
        return '資料異常', ''
    advs = df['advice'].astype(str).tolist()
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

# --- 當局結果輸入 ---
with st.form("input_form", clear_on_submit=True):
    result = st.radio("請選擇當局結果", options=['莊', '閒', '和'], horizontal=True, key='advice_radio')
    submitted = st.form_submit_button("送出紀錄")

def write_to_csv(filename, advice):
    with open(filename, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([advice])

if submitted:
    write_to_csv(csv_file, result)
    log_str = f"紀錄：{result}"
    st.session_state.round_log.append(log_str)
    st.success(log_str)

# --- 當場紀錄區 ---
st.markdown("#### 記錄區：")
st.text('\n'.join(st.session_state.round_log[-30:]))

# --- 比對區 ---
pred_3, rate_3 = ai_predict_next_adviceN_only(csv_file, N=3)
pred_6, rate_6 = ai_predict_next_adviceN_only(csv_file, N=6)

st.markdown("#### 比對方式 & 結果")
st.write(f"比對預測 (3局)：{pred_3}")
st.write(f"比對預測 (6局)：{pred_6}")

# --- 匯出 Excel ---
if st.button("匯出Excel"):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        excel_out = csv_file.replace('.csv', '.xlsx')
        if os.path.exists(excel_out):
            os.remove(excel_out)
        with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="牌局記錄", index=False)
        st.success(f"已匯出: {excel_out}")

st.caption("點選結果後，自動紀錄、即時比對、手機/電腦皆可用。")
