import streamlit as st
import pandas as pd
import csv, os

# 檔案名稱
csv_file = os.path.join(os.path.dirname(__file__), 'ai_train_history.csv')

# 如果沒有就新建，有就保留
if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['advice'])

st.set_page_config(page_title="百家樂極簡記錄", layout="centered")
st.title("百家樂極簡記錄（僅輸入結果）")

if 'round_log' not in st.session_state:
    st.session_state.round_log = []

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

st.caption("只需點選結果即可快速累積紀錄。")
