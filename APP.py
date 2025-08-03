import streamlit as st
import pandas as pd
import os
import csv
from collections import Counter

# ---- 牌型/資料結構 ----
NUM_TO_FACE = {11: 'J', 12: 'Q', 13: 'K'}
FACE_TO_NUM = {'J': 11, 'Q': 12, 'K': 13}
CSV_FILE = 'ai_train_history.csv'

def card_str(n):
    return NUM_TO_FACE.get(n, str(n))
def parse_cards(s):
    out = []
    for x in str(s).replace('，',',').replace(' ', ',').split(','):
        x = x.strip().upper()
        if not x: continue
        if x in FACE_TO_NUM:
            out.append(FACE_TO_NUM[x])
        elif x.isdigit() and 1 <= int(x) <= 13:
            out.append(int(x))
    return out[:4]
def show_cards(cards):
    return ','.join([card_str(c) for c in cards])
def calc_baccarat_point(cards):
    return sum((c if c < 10 else 0) for c in cards) % 10 if cards else ""
def init_deck():
    return {n: 32 for n in range(1, 14)}
def deck_str(deck):
    return ' '.join(f'{card_str(k)}:{deck[k]}' for k in range(1,14))
def update_deck(history, p_list, b_list):
    tmp_deck = init_deck()
    for h in history:
        for card in h.get('p_list', []) + h.get('b_list', []):
            tmp_deck[card] -= 1
    for card in p_list + b_list:
        if tmp_deck[card] > 0:
            tmp_deck[card] -= 1
    return tmp_deck

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

# ---- 初始化檔案/狀態 ----
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'player', 'player_cards', 'banker', 'banker_cards', 'final', 'advice'
        ])

if 'history' not in st.session_state:
    st.session_state.history = []
if 'p_list' not in st.session_state:
    st.session_state.p_list = []
if 'b_list' not in st.session_state:
    st.session_state.b_list = []

# ---- UI主體：左右欄設計 ----
st.set_page_config('百家樂資料分析', layout='wide')
st.markdown("<h1 style='text-align:center;color:#154278;'>百家樂 比對資料分析（手機/網頁）</h1>", unsafe_allow_html=True)

left, right = st.columns([3, 4])

with left:
    # ------ 閒家 ------
    st.markdown("### 閒家點數：3張牌 (1~13/JQK)")
    col1, col2 = st.columns([2,2])
    with col1:
        player_input = st.text_input('', value=show_cards(st.session_state.p_list), key='player_cards_in', max_chars=14)
    with col2:
        st.markdown(f"目前點數：<span style='color:blue;font-size:1.4em;'>{calc_baccarat_point(st.session_state.p_list)}</span>", unsafe_allow_html=True)

    # --- 數字按鈕一排7顆 ---
    card_labels = [str(i) for i in range(1, 11)] + ['J', 'Q', 'K']
    card_rows = [card_labels[i:i+7] for i in range(0, len(card_labels), 7)]
    for row in card_rows:
        cols = st.columns(len(row))
        for i, v in enumerate(row):
            if cols[i].button(v, key=f'player_card_{v}', use_container_width=True):
                v_num = FACE_TO_NUM[v] if v in FACE_TO_NUM else int(v)
                if len(st.session_state.p_list) < 4:
                    st.session_state.p_list.append(v_num)
                st.rerun()
    op_cols = st.columns(2)
    if op_cols[0].button("刪除", key='player_del', use_container_width=True):
        if st.session_state.p_list:
            st.session_state.p_list.pop()
        st.rerun()
    if op_cols[1].button("重製", key='player_reset', use_container_width=True):
        st.session_state.p_list = []
        st.rerun()

    # ------ 莊家 ------
    st.markdown("### 莊家點數：3張牌 (1~13/JQK)")
    col1, col2 = st.columns([2,2])
    with col1:
        banker_input = st.text_input('', value=show_cards(st.session_state.b_list), key='banker_cards_in', max_chars=14)
    with col2:
        st.markdown(f"目前點數：<span style='color:blue;font-size:1.4em;'>{calc_baccarat_point(st.session_state.b_list)}</span>", unsafe_allow_html=True)

    card_rows = [card_labels[i:i+7] for i in range(0, len(card_labels), 7)]
    for row in card_rows:
        cols = st.columns(len(row))
        for i, v in enumerate(row):
            if cols[i].button(v, key=f'banker_card_{v}', use_container_width=True):
                v_num = FACE_TO_NUM[v] if v in FACE_TO_NUM else int(v)
                if len(st.session_state.b_list) < 4:
                    st.session_state.b_list.append(v_num)
                st.rerun()
    op_cols = st.columns(2)
    if op_cols[0].button("刪除", key='banker_del', use_container_width=True):
        if st.session_state.b_list:
            st.session_state.b_list.pop()
        st.rerun()
    if op_cols[1].button("重製", key='banker_reset', use_container_width=True):
        st.session_state.b_list = []
        st.rerun()

    # ------ 剩餘牌池 ------
    deck_show = deck_str(update_deck(st.session_state.history, st.session_state.p_list, st.session_state.b_list))
    st.markdown(f'<div style="color:#008080;font-weight:bold;font-size:1.15rem;">剩餘牌池：{deck_show}</div>', unsafe_allow_html=True)

    # ------ 主按鈕 ------
    op1, op2, op3 = st.columns(3)
    with op1:
        比對 = st.button('比對')
    with op2:
        重設牌池 = st.button('重設牌池')
    with op3:
        儲存 = st.button('儲存紀錄')

with right:
    # ------ 結果/預測區 ------
    st.markdown("#### 比對預測(3局)：")
    pred, rate = ai_predict_next_adviceN_only(CSV_FILE, N=3)
    st.markdown(f"<div style='color:blue;'>{pred}</div>", unsafe_allow_html=True)
    st.markdown("#### 比對預測(6局)：")
    auto_pred, auto_rate = ai_predict_next_adviceN_only(CSV_FILE, N=6)
    st.markdown(f"<div style='color:blue;'>{auto_pred}</div>", unsafe_allow_html=True)
    st.markdown("#### 比對正確率：")
    st.markdown(f"<div style='color:blue;'>{auto_rate}</div>", unsafe_allow_html=True)

    # ------ 記錄區 ------
    st.markdown("#### 記錄區：")
    if 'round_log' not in st.session_state:
        st.session_state.round_log = ""
    st.text_area('', st.session_state.round_log, height=230, key='round_log_show', disabled=True)

# ---- 操作主流程 ----
if 比對:
    p_list = st.session_state.p_list
    b_list = st.session_state.b_list
    p_point = calc_baccarat_point(p_list) if p_list else ''
    b_point = calc_baccarat_point(b_list) if b_list else ''
    iff = abs(p_point - b_point) if (p_list and b_list) else ''
    if p_point == '' or b_point == '':
        advice = ''
        st.warning('請同時輸入閒家與莊家的牌！')
    elif p_point > b_point:
        advice = '閒'
    elif p_point < b_point:
        advice = '莊'
    else:
        advice = '和'
    record = {
        'player': p_point,
        'player_cards': show_cards(p_list),
        'banker': b_point,
        'banker_cards': show_cards(b_list),
        'final': iff,
        'advice': advice,
        'p_list': p_list.copy(),
        'b_list': b_list.copy()
    }
    st.session_state.history.append(record)
    with open(CSV_FILE, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            record['player'],
            record['player_cards'],
            record['banker'],
            record['banker_cards'],
            record['final'],
            record['advice']
        ])
    msg = f"紀錄: 閒={p_point} [{show_cards(p_list)}] 莊={b_point} [{show_cards(b_list)}] 結果advice={advice}\n"
    if 'round_log' not in st.session_state:
        st.session_state.round_log = ""
    st.session_state.round_log += msg
    st.session_state.p_list = []
    st.session_state.b_list = []
    st.rerun()

if 重設牌池:
    st.session_state.p_list = []
    st.session_state.b_list = []
    st.rerun()

if 儲存:
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    sheetname = f'牌局記錄{pd.Timestamp.now().strftime("%m%d_%H%M%S")}'
    excel_out = CSV_FILE.replace('.csv', '.xlsx')
    if os.path.exists(excel_out):
        os.remove(excel_out)
    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheetname, index=False)
    st.success(f"已將本次紀錄存為：{excel_out}")
