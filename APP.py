import streamlit as st
import pandas as pd
import os
from collections import Counter

csv_file = "ai_train_history.csv"

# ===== 資料初始化，確保advice欄存在 =====
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["advice"])
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
else:
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    if "advice" not in df.columns:
        df = pd.DataFrame(columns=["advice"])
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="百家樂比對資料分析", layout="centered")
st.title("百家樂 比對資料分析（手機/電腦版）")

st.markdown("---")

# ===== 當局結果輸入操作區 =====
st.subheader("操作區")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("莊", use_container_width=True):
        st.session_state['advice_input'] = "莊"
with col2:
    if st.button("閒", use_container_width=True):
        st.session_state['advice_input'] = "閒"
with col3:
    if st.button("和", use_container_width=True):
        st.session_state['advice_input'] = "和"
with col4:
    if st.button("刪除", use_container_width=True):
        if len(df) > 0:
            df = df.iloc[:-1]
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            st.success("已刪除上一筆紀錄")
        else:
            st.warning("沒有可刪除資料")
with col5:
    if st.button("輸入", use_container_width=True):
        advice_input = st.session_state.get('advice_input', "")
        if advice_input:
            df = pd.concat([df, pd.DataFrame({"advice":[advice_input]})], ignore_index=True)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            st.success(f"已新增紀錄：{advice_input}")
            st.session_state['advice_input'] = ""
        else:
            st.error("請先按下莊/閒/和選擇結果！")

st.markdown("---")

# ===== 比對預測功能 =====
def ai_predict_next_adviceN_only(df, N=3):
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

# ========== 比對預測、顯示 ==============
st.subheader("比對預測區")
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("比對", use_container_width=True, key="compare_btn"):
        st.session_state['do_compare'] = True
with btn_col2:
    if st.button("儲存紀錄", use_container_width=True, key="save_btn"):
        excel_out = csv_file.replace('.csv', '.xlsx')
        df.to_excel(excel_out, index=False)
        st.success(f"已將紀錄存為 {excel_out}")

if st.session_state.get('do_compare', False):
    pred_3, rate_3 = ai_predict_next_adviceN_only(df, N=3)
    pred_6, rate_6 = ai_predict_next_adviceN_only(df, N=6)
    st.markdown(f"<div style='font-size:16px;font-weight:bold;'>比對預測(3局)：<span style='color:#1761e6'>{pred_3}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:16px;font-weight:bold;'>比對預測(6局)：<span style='color:#1761e6'>{pred_6}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:16px;font-weight:bold;'>比對正確率：<span style='color:#1761e6'>{rate_6}</span></div>", unsafe_allow_html=True)
    st.session_state['do_compare'] = False

st.markdown("---")

# ===== 記錄區（即時顯示所有歷史advice） =====
st.subheader("記錄區")
if len(df) == 0:
    st.write("尚無紀錄")
else:
    log = ""
    for i, row in df.iterrows():
        log += f"已紀錄: 結果advice={row['advice']}\n"
    st.text_area("歷史記錄", value=log, height=220, key="history_log", disabled=True, label_visibility="collapsed")
