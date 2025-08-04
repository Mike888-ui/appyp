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

st.markdown("### 選擇當局結果")

# ----【1. 按鈕靠攏】
# 設計：欄寬全部均分，按鈕用小字，padding/高度精簡
# --- 五鍵完全靠攏無間隙
# --- 五鍵完全靠攏無間隙
btn_css = f"""
<style>
div[data-testid="column"] > div {{
    padding: 0 !important;
}}
div[data-testid="columns"] {{
    gap: 14px !important;
}}
button[kind="secondary"], button[kind="primary"] {{
    font-size: 22px !important;
    height: 54px !important;
    width: 100% !important;
    border-radius: 10px !important;
    background: #345 !important;
    color: #fff !important;
    margin: 0 0 0 0 !important;
    box-shadow: 2px 2px 4px #0003;
    transition: background 0.2s, color 0.2s;
}}
button[disabled] {{
    background: #ccc !important;
    color: #999 !important;
}}
/* 高亮顯示目前選擇的按鈕 */
.cur_selected button {{
    background: #ea9e2e !important;
    color: #222 !important;
    border: 2px solid #e65100 !important;
    font-weight: bold !important;
}}
</style>
"""
st.markdown(btn_css, unsafe_allow_html=True)

# 五個欄，全部均寬
cols = st.columns([1,1,1,1,1])

btn_labels = ["莊", "閒", "和", "清除", "比對 / 紀錄"]
btn_keys = ["b1", "b2", "b3", "b4", "b5"]

# 取得當前狀態
if 'cur_result' not in st.session_state:
    st.session_state['cur_result'] = ""
cur_result = st.session_state['cur_result']

btn_clicks = []

for i, col in enumerate(cols):
    # 若該按鈕是目前選擇，外框加高亮 class
    btn_container = col
    with col:
        _add_cur = False
        if i == 0 and cur_result == "莊":
            st.markdown('<div class="cur_selected">', unsafe_allow_html=True)
            _add_cur = True
        elif i == 1 and cur_result == "閒":
            st.markdown('<div class="cur_selected">', unsafe_allow_html=True)
            _add_cur = True
        elif i == 2 and cur_result == "和":
            st.markdown('<div class="cur_selected">', unsafe_allow_html=True)
            _add_cur = True
        elif i == 3 and cur_result == "":
            st.markdown('<div class="cur_selected">', unsafe_allow_html=True)
            _add_cur = True
        if i < 4:
            btn_clicks.append(st.button(btn_labels[i], key=btn_keys[i]))
        else:
            btn_clicks.append(st.button(btn_labels[i], key=btn_keys[i], disabled=not cur_result))
        if _add_cur:
            st.markdown('</div>', unsafe_allow_html=True)

# 狀態處理
if btn_clicks[0]:
    st.session_state['cur_result'] = "莊"
if btn_clicks[1]:
    st.session_state['cur_result'] = "閒"
if btn_clicks[2]:
    st.session_state['cur_result'] = "和"
if btn_clicks[3]:
    st.session_state['cur_result'] = ""
cur_result = st.session_state.get('cur_result', "")

if btn_clicks[4] and cur_result:
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

st.caption("手機/電腦可用．所有主操作按鈕一列並排，單手也能秒選！精簡顯示。")
