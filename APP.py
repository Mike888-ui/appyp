import streamlit as st
import pandas as pd
import os
import csv
from collections import Counter

CSV_FILE = 'ai_train_history.csv'

# 初始化資料
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['advice'])
df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')

# UI
st.set_page_config('百家樂資料分析', layout='centered')
st.markdown("<h1 style='text-align:center;color:#154278;'>百家樂 比對資料分析（手機/網頁）</h1>", unsafe_allow_html=True)

# ------- 操作按鈕欄 -------
st.subheader("當局結果輸入")
btns = st.columns(5)
if "current_advice" not in st.session_state:
    st.session_state.current_advice = ""

with btns[0]:
    if st.button("莊", use_container_width=True):
        st.session_state.current_advice = "莊"
with btns[1]:
    if st.button("閒", use_container_width=True):
        st.session_state.current_advice = "閒"
with btns[2]:
    if st.button("和", use_container_width=True):
        st.session_state.current_advice = "和"
with btns[3]:
    if st.button("刪除", use_container_width=True):
        if len(df) > 0:
            df = df.iloc[:-1]
            df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
            st.success("已刪除上一筆紀錄")
            st.session_state.current_advice = ""
            st.experimental_rerun()
        else:
            st.warning("沒有可刪除資料")
with btns[4]:
    if st.button("輸入", use_container_width=True):
        adv = st.session_state.get("current_advice", "")
        if adv:
            df = pd.concat([df, pd.DataFrame({"advice": [adv]})], ignore_index=True)
            df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
            st.success(f"已新增紀錄：{adv}")
            st.session_state.current_advice = ""
            st.experimental_rerun()
        else:
            st.warning("請先選擇莊/閒/和後再按輸入")

# ------- 比對預測功能 -------
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
    show_detail = f"莊:{stat.get('莊',0)} 閒:{stat.get('閒',0)} 和:{stat.get('和',0)}"
    return f"{most} ({percent}%)「{show_detail}」", f"{percent}%"

st.markdown("---")
st.subheader("比對預測區")
pred_3, rate_3 = ai_predict_next_adviceN_only(df, N=3)
pred_6, rate_6 = ai_predict_next_adviceN_only(df, N=6)
st.markdown(f"**比對預測(3局)：** <span style='color:#1761e6'>{pred_3}</span>", unsafe_allow_html=True)
st.markdown(f"**比對預測(6局)：** <span style='color:#1761e6'>{pred_6}</span>", unsafe_allow_html=True)
st.markdown(f"**比對正確率：** <span style='color:#1761e6'>{rate_6}</span>", unsafe_allow_html=True)

# ------- 儲存紀錄 -------
if st.button('儲存紀錄', use_container_width=True):
    excel_out = CSV_FILE.replace('.csv', '.xlsx')
    df.to_excel(excel_out, index=False)
    st.success(f"已將本次紀錄存為：{excel_out}")

st.markdown("---")

# ------- 記錄區 -------
st.subheader("記錄區")
if len(df) == 0:
    st.write("尚無紀錄")
else:
    msg = ""
    for i, row in df.iterrows():
        msg += f"已紀錄: 結果advice={row['advice']}\n"
    st.text_area("歷史紀錄", value=msg, height=250, key="history_log", disabled=True, label_visibility="collapsed")
