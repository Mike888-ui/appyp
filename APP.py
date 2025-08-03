import streamlit as st
import pandas as pd
import os
import csv
from collections import Counter

CSV_FILE = 'ai_train_history.csv'
COLUMNS = [
    'player', 'player_cards',
    'banker', 'banker_cards',
    'final', 'advice',
    'big_eye_banker', 'small_banker', 'cockroach_banker',
    'big_eye_player', 'small_player', 'cockroach_player'
]

# 初始化csv
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)

if 'history' not in st.session_state:
    st.session_state.history = []
if 'round_log' not in st.session_state:
    st.session_state.round_log = ""

def write_to_csv(record):
    with open(CSV_FILE, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([record.get(col, '') for col in COLUMNS])

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
    show_detail = f"莊:{stat.get('莊',0)} 閒:{stat.get('閒',0)} 和:{stat.get('和',0)}"
    return f"{most} ({percent}%)「{show_detail}」", f"{percent}%"

st.set_page_config('百家樂結果輸入', layout='wide')
st.markdown("<h1 style='text-align:center;color:#154278;'>百家樂 結果輸入（完整欄位）</h1>", unsafe_allow_html=True)

left, right = st.columns([2,3])

with left:
    st.markdown("### 當局結果")

    # 結果按鍵
    btn_cols = st.columns(4)
    if btn_cols[0].button("莊", use_container_width=True):
        record = {
            'player': '', 'player_cards': '',
            'banker': '', 'banker_cards': '',
            'final': '', 'advice': '莊',
            'big_eye_banker': '', 'small_banker': '', 'cockroach_banker': '',
            'big_eye_player': '', 'small_player': '', 'cockroach_player': ''
        }
        write_to_csv(record)
        st.session_state.round_log += f"紀錄: 結果advice=莊\n"
        st.rerun()
    if btn_cols[1].button("閒", use_container_width=True):
        record = {
            'player': '', 'player_cards': '',
            'banker': '', 'banker_cards': '',
            'final': '', 'advice': '閒',
            'big_eye_banker': '', 'small_banker': '', 'cockroach_banker': '',
            'big_eye_player': '', 'small_player': '', 'cockroach_player': ''
        }
        write_to_csv(record)
        st.session_state.round_log += f"紀錄: 結果advice=閒\n"
        st.rerun()
    if btn_cols[2].button("和", use_container_width=True):
        record = {
            'player': '', 'player_cards': '',
            'banker': '', 'banker_cards': '',
            'final': '', 'advice': '和',
            'big_eye_banker': '', 'small_banker': '', 'cockroach_banker': '',
            'big_eye_player': '', 'small_player': '', 'cockroach_player': ''
        }
        write_to_csv(record)
        st.session_state.round_log += f"紀錄: 結果advice=和\n"
        st.rerun()
    if btn_cols[3].button("刪除", use_container_width=True):
        # 刪最後一筆
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            if len(df) > 0:
                df = df.iloc[:-1, :]
                df.to_csv(CSV_FILE, encoding='utf-8-sig', index=False)
        # Log 也刪掉
        logs = st.session_state.round_log.strip().split("\n")
        if logs:
            logs = logs[:-1]
            st.session_state.round_log = "\n".join(logs) + ("\n" if logs else "")
        st.rerun()

    # 操作按鈕
    st.markdown("---")
    btn2 = st.columns(2)
    if btn2[0].button('比對', use_container_width=True):
        # 觸發預測更新
        st.session_state['do_compare'] = True
        st.rerun()
    if btn2[1].button('重設牌池', use_container_width=True):
        # 只是清除全部暫存資料（或可延伸為重設欄位）
        st.session_state.round_log = ""
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            df = df.iloc[0:0, :]  # 清空但保留欄位
            df.to_csv(CSV_FILE, encoding='utf-8-sig', index=False)
        st.rerun()

    # 匯出按鈕
    st.markdown("---")
    if st.button('匯出Excel', use_container_width=True):
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        sheetname = f'牌局記錄{pd.Timestamp.now().strftime("%m%d_%H%M%S")}'
        excel_out = CSV_FILE.replace('.csv', '.xlsx')
        if os.path.exists(excel_out):
            os.remove(excel_out)
        with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheetname, index=False)
        st.success(f"已將本次紀錄存為：{excel_out}")

with right:
    # 比對顯示
    def show_compare():
        st.markdown("#### 比對(3局)：")
        pred, rate = ai_predict_next_adviceN_only(CSV_FILE, N=3)
        st.markdown(f"<div style='color:blue;'>{pred}</div>", unsafe_allow_html=True)
        st.markdown("#### 比對(6局)：")
        auto_pred, auto_rate = ai_predict_next_adviceN_only(CSV_FILE, N=6)
        st.markdown(f"<div style='color:blue;'>{auto_pred}</div>", unsafe_allow_html=True)
        st.markdown("#### ---：")
        st.markdown(f"<div style='color:blue;'>{auto_rate}</div>", unsafe_allow_html=True)
    show_compare()

    # 牌局記錄區
    st.markdown("#### 牌局記錄區：")
    st.text_area('', st.session_state.round_log, height=300, key='round_log_show', disabled=True)

    # 完整欄位紀錄表格
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        st.markdown("---")
        st.dataframe(df.tail(30), use_container_width=True)
    except:
        st.warning('目前無紀錄資料')
