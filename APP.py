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

# ========== 彩色按鈕CSS ==========
btn_css = """
<style>
div[data-testid="column"] > div {
    padding: 0 !important;
}
div[data-testid="columns"] {
    gap: 14px !important;
}
/* 預設彩色按鈕底色 */
.btn-banker button {background: #e53935 !important; color: #fff !important;}
.btn-player button {background: #1e88e5 !important; color: #fff !important;}
.btn-tie    button {background: #43a047 !important; color: #fff !important;}
.btn-clear  button {background: #888 !important; color: #fff !important;}
.btn-save   button {background: #ffb300 !important; color: #774700 !important;}
/* 選取高亮（白底＋彩邊框） */
.cur_selected button {
    background: #fff !important;
    color: #222 !important;
    font-weight: bold !important;
    border: 2.2px solid #ffb300 !important;
    box-shadow: none !important;
}
button[kind="secondary"], button[kind="primary"] {
    font-size: 22px !important;
    height: 54px !important;
    width: 100% !important;
    border-radius: 15px !important;
    margin: 0 !important;
    border: 0 !important;
    outline: none !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
    transition: none !important;
}
button[disabled] {
    background: #ccc !important;
    color: #999 !important;
}
button:focus, button:active, button:target {
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

cur_result = st.session_state.get('cur_result', "")
btn_clicks = []
cols = st.columns([1,1,1,1,1])
btn_labels = ["莊", "閒", "和", "清除", "比對 / 紀錄"]
btn_keys = ["b1", "b2", "b3", "b4", "b5"]
btn_css_classes = [
    "btn-banker", "btn-player", "btn-tie", "btn-clear", "btn-save"
]

if 'cur_result' not in st.session_state:
    st.session_state['cur_result'] = ""
cur_result = st.session_state['cur_result']

for i, col in enumerate(cols):
    with col:
        css_class = btn_css_classes[i]
        _add_cur = False
        if (i == 0 and cur_result == "莊") or (i == 1 and cur_result == "閒") or (i == 2 and cur_result == "和"):
            st.markdown(f'<div class="cur_selected {css_class}">', unsafe_allow_html=True)
            _add_cur = True
        elif i == 3 and cur_result == "":
            st.markdown(f'<div class="cur_selected {css_class}">', unsafe_allow_html=True)
            _add_cur = True
        else:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)

        if i < 3:
            if st.button(btn_labels[i], key=btn_keys[i]):
                st.session_state['cur_result'] = btn_labels[i]
                st.rerun()
        elif i == 3:
            if st.button(btn_labels[i], key=btn_keys[i]):
                st.session_state['cur_result'] = ""
                st.rerun()
        else:
            if st.button(btn_labels[i], key=btn_keys[i], disabled=not cur_result):
                # 執行紀錄
                with open(csv_file, 'a', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([cur_result])
                st.session_state['last_record'] = cur_result
                st.session_state['cur_result'] = ""
                st.success(f"已紀錄：{cur_result}")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 其它顯示區不變
st.markdown("---")
st.markdown('<span style="font-size:18px"><b>當前選擇結果</b></span>', unsafe_allow_html=True)
if cur_result:
    st.markdown(f'<div style="font-size:17px;color:#1a237e;background:#e3f2fd;border-radius:7px;padding:4px 10px;display:inline-block;margin:6px 0">已選擇：{cur_result}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="font-size:17px;color:#888;background:#fffde7;border-radius:7px;padding:4px 10px;display:inline-block;margin:6px 0">請選擇一個結果</div>', unsafe_allow_html=True)

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

st.caption("手機/電腦可用．每鍵不同色，主操作永遠在眼前！")
