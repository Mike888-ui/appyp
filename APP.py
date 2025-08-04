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
btn_css = """
<style>
div[data-testid="column"] > div {
    padding: 0 !important;
}
div[data-testid="columns"] {
    gap: 14px !important;
}
/* 一般狀態 */
button[kind="secondary"], button[kind="primary"] {
    font-size: 22px !important;
    height: 54px !important;
    width: 100% !important;
    border-radius: 15px !important;
    background: #345 !important;
    color: #fff !important;
    margin: 0 !important;
    border: 0 !important;
    outline: none !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
    transition: none !important;
}
/* 禁用樣式 */
button[disabled] {
    background: #ccc !important;
    color: #999 !important;
    outline: none !important;
    box-shadow: none !important;
    border: 0 !important;
}
/* 只要選取就變白底深字，完全沒有任何額外特效 */
.cur_selected button {
    background: #fff !important;
    color: #223 !important;
    font-weight: bold !important;
    outline: none !important;
    border: 0 !important;
    box-shadow: none !important;
    transition: none !important;
}
/* 終極防呆：所有互動態全部無外框、無陰影、無位移、無hover特效 */
button:focus, button:active, button:target, button:visited, button:focus-visible, button:hover {
    outline: none !important;
    box-shadow: none !important;
    border: 0 !important;
    background: inherit !important;
    color: inherit !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}
</style>
"""
st.markdown(btn_css, unsafe_allow_html=True)

# 狀態判斷
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
