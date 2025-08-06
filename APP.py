import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="百家樂 AI Web", layout="centered")
st.title("百家樂 AI 分析 Web App（四鍵輸入+比對）")

CSV_FILE = 'ai_train_history.csv'

# --------- 1. 按鍵輸入區 ---------
st.markdown("### 1. 當局結果輸入")

button_labels = [("莊", 60), ("閒", 60), ("和", 60), ("刪除", 80)]
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

# --------- 2. 暫存本局結果 ---------
if "curr_result" not in st.session_state:
    st.session_state["curr_result"] = ""

if btn_clicked in ["莊", "閒", "和"]:
    st.session_state["curr_result"] = btn_clicked
elif btn_clicked == "刪除":
    # 刪除最後一筆歷史紀錄
    if "history" not in st.session_state:
        if os.path.exists(CSV_FILE):
            st.session_state['history'] = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        else:
            st.session_state['history'] = pd.DataFrame(columns=["advice", "final", "time"])
    if not st.session_state['history'].empty:
        st.session_state['history'] = st.session_state['history'].iloc[:-1, :]
        st.session_state['history'].to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.success("已刪除最後一筆紀錄")
    else:
        st.warning("目前沒有可刪除的紀錄")

# --------- 3. 顯示暫存輸入內容 ---------
if st.session_state["curr_result"]:
    st.info(f"目前待比對內容：{st.session_state['curr_result']}", icon="🔸")
else:
    st.info("請選擇本局結果（莊/閒/和）")

# --------- 4. 比對按鍵 ---------
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

if st.button("比對 / 預測", key="compare_btn", use_container_width=True):
    if not st.session_state["curr_result"]:
        st.error("請先選擇本局結果（莊/閒/和）")
    else:
        # 新增紀錄
        if 'history' in st.session_state and not st.session_state['history'].empty:
            pred_3 = ai_predict_next_adviceN_only(st.session_state['history'], 3)
        else:
            pred_3 = ""
        new_record = {
            "advice": st.session_state["curr_result"],
            "final": pred_3,  # 新增final欄
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        # 讀舊的
        if os.path.exists(CSV_FILE):
            try:
                history = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            except Exception:
                history = pd.DataFrame(columns=["advice", "final", "time"])
        else:
            history = pd.DataFrame(columns=["advice", "final", "time"])
        history = pd.concat([history, pd.DataFrame([new_record])], ignore_index=True)
        history.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        st.session_state['history'] = history
        st.session_state["curr_result"] = ""  # 清空
        st.success(f"已比對並記錄：{new_record['advice']}")

# --------- 5. 讀取歷史紀錄 ---------
if 'history' not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            st.session_state['history'] = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        except Exception:
            st.session_state['history'] = pd.DataFrame(columns=["advice", "final", "time"])
    else:
        st.session_state['history'] = pd.DataFrame(columns=["advice", "final", "time"])

# --------- 6. 預測功能 ---------
st.markdown("### 2. 比對預測")
history = st.session_state['history']
if not history.empty:
    pred_3 = ai_predict_next_adviceN_only(history, 3)
    pred_6 = ai_predict_next_adviceN_only(history, 6)
    st.markdown(f"#### 比對預測 (3局)： {pred_3}")
    st.markdown(f"#### 比對預測 (6局)： {pred_6}")
else:
    st.info("目前無紀錄")

# --------- 7. 歷史紀錄與下載（隱藏/展開） ---------
st.markdown("### 3. 歷史紀錄")
with st.expander("點此展開/收起 歷史紀錄", expanded=False):
    if not history.empty:
        st.dataframe(history, use_container_width=True)
        st.download_button("下載 CSV", data=history.to_csv(index=False), file_name="ai_train_history.csv")
        history.to_excel("ai_train_history.xlsx", index=False)
        with open("ai_train_history.xlsx", "rb") as f:
            st.download_button("下載 Excel", data=f, file_name="ai_train_history.xlsx")
    else:
        st.write("暫無歷史紀錄")
