import streamlit as st
import pandas as pd
import csv, os
from collections import Counter

csv_file = os.path.join(os.path.dirname(__file__), 'ai_train_history.csv')
if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['advice'])

st.set_page_config(page_title="百家樂-快速紀錄", layout="centered")
st.title("百家樂-快速紀錄&分析 (手機極簡版)")

# ---- 用 Streamlit 原生 button 直排（最佳兼容性）
st.markdown("### 選擇當局結果")
btn_size = (6, 2)  # (width, height)

col = st.container()
with col:
    c1 = st.button("莊", key="b1", use_container_width=True)
    c2 = st.button("閒", key="b2", use_container_width=True)
    c3 = st.button("和", key="b3", use_container_width=True)
    c4 = st.button("清除", key="b4", use_container_width=True)

if 'cur_result' not in st.session_state:
    st.session_state['cur_result'] = ""

if c1:
    st.session_state['cur_result'] = "莊"
if c2:
    st.session_state['cur_result'] = "閒"
if c3:
    st.session_state['cur_result'] = "和"
if c4:
    st.session_state['cur_result'] = ""

cur_result = st.session_state.get('cur_result', "")

st.markdown("---")
st.markdown("#### 當前選擇結果")
if cur_result:
    st.info(f"已選擇：{cur_result}")
else:
    st.warning("請選擇一個結果")

# -- 只在按下比對/紀錄才紀錄＋顯示「已紀錄：」訊息
if st.button("比對 / 紀錄", type="primary", use_container_width=True, disabled=not cur_result):
    with open(csv_file, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([cur_result])
    st.success(f"已紀錄：{cur_result}")
    st.session_state['last_record'] = cur_result
    st.session_state['cur_result'] = ""

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

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
else:
    df = pd.DataFrame(columns=['advice'])

if len(df) > 0:
    pred, rate = ai_predict_next_adviceN_only(csv_file, N=3)
    auto_pred, auto_rate = ai_predict_next_adviceN_only(csv_file, N=6)
    st.info(f"比對預測(3局)：{pred}")
    st.info(f"比對預測(6局)：{auto_pred}")
    st.write(f"比對正確率：{auto_rate}")

st.markdown("---")
st.markdown("#### 歷史紀錄")
last_record = st.session_state.get('last_record', None)
if last_record:
    st.write(f"已紀錄：{last_record}")
else:
    st.write("尚未紀錄新一局")

if st.button("匯出Excel"):
    if os.path.exists(csv_file):
        excel_out = csv_file.replace('.csv', '.xlsx')
        if os.path.exists(excel_out):
            os.remove(excel_out)
        with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="牌局記錄", index=False)
        st.success(f"已匯出: {excel_out}")

st.caption("手機/電腦可用．單列直排按鈕，無前端自訂 HTML/JS，100%支援雲端。")
