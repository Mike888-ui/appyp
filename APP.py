import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="百家樂 AI Web", layout="centered")
st.title("百家樂 AI 分析 Web App（四鍵輸入簡版）")

CSV_FILE = 'ai_train_history.csv'

# --------- 1. 按鍵輸入區 ---------
st.markdown("### 1. 當局結果輸入")

# 按鍵內容與自適應寬度設計
button_labels = [("莊", 60), ("閒", 60), ("和", 60), ("刪除", 80)]  # (文字, 最小寬度 px)

# 依據字數自動設寬度
cols = st.columns(len(button_labels), gap="medium")
btn_clicked = None
for i, (label, min_width) in enumerate(button_labels):
    style = f"""
        <style>
        .stButton > button {{
            min-width: {min_width}px;
            font-size: 1.25rem;
            font-weight: bold;
            padding: 0.7em 1em;
            border-radius: 0.75em;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    if cols[i].button(label, use_container_width=True, key=f"btn_{label}"):
        btn_clicked = label

# --------- 2. 按鍵邏輯與記錄 ---------
if 'history' not in st.session_state:
    if os.path.exists(CSV_FILE):
        st.session_state['history'] = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    else:
        st.session_state['history'] = pd.DataFrame()

if btn_clicked == "刪除":
    # 刪除最後一筆紀錄
    if not st.session_state['history'].empty:
        st.session_state['history'] = st.session_state['history'][:-1]
        st.session_state['history'].to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success("已刪除最後一筆紀錄")
    else:
        st.warning("目前沒有可刪除的紀錄")
elif btn_clicked in ["莊", "閒", "和"]:
    # 新增紀錄
    new_record = {
        "advice": btn_clicked,
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state['history'] = st.session_state['history'].append(new_record, ignore_index=True)
    st.session_state['history'].to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    st.success(f"已記錄：{btn_clicked}")

# --------- 3. 預測功能 ---------
def ai_predict_next_adviceN_only(df, N=3):
    if 'advice' not in df.columns or df.empty:
        return '資料異常'
    advs = df['advice'].astype(str).tolist()
    now_count = min(len(advs), N)
    if len(advs) < N:
        return '暫無資料'
    last_n = advs[-now_count:]
    matches = []
    for i in range(len(advs) - now_count):
        if advs[i:i+now_count] == last_n:
            if i + now_count < len(advs):
                matches.append(advs[i + now_count])
    if not matches:
        return '暫無資料'
    from collections import Counter
    stat = Counter(matches)
    most, cnt = stat.most_common(1)[0]
    percent = int(cnt / len(matches) * 100)
    show_detail = f"莊:{stat.get('莊',0)} 閒:{stat.get('閒',0)} 和:{stat.get('和',0)}"
    return f"{most} ({percent}%) [{show_detail}]"

# --------- 4. 比對/預測顯示 ---------
st.markdown("### 2. 比對預測")
history = st.session_state['history']
if not history.empty:
    pred_3 = ai_predict_next_adviceN_only(history, 3)
    pred_6 = ai_predict_next_adviceN_only(history, 6)
    st.markdown(f"#### 比對預測 (3局)： {pred_3}")
    st.markdown(f"#### 比對預測 (6局)： {pred_6}")
else:
    st.info("目前無紀錄")

# --------- 5. 歷史紀錄與下載 ---------
st.markdown("### 3. 歷史紀錄")
if not history.empty:
    st.dataframe(history, use_container_width=True)
    st.download_button("下載 CSV", data=history.to_csv(index=False), file_name="ai_train_history.csv")
    history.to_excel("ai_train_history.xlsx", index=False)
    with open("ai_train_history.xlsx", "rb") as f:
        st.download_button("下載 Excel", data=f, file_name="ai_train_history.xlsx")
else:
    st.write("暫無歷史紀錄")
