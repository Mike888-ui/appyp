import streamlit as st
import pandas as pd
import os
import csv
from collections import Counter

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
    return sum((c if c < 10 else 0) for c in cards) % 10

def init_deck():
    return {n: 32 for n in range(1, 14)}

def deck_str(deck):
    return ' '.join(f'{card_str(k)}:{deck[k]}' for k in range(1,14))

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

# 初始化
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'player', 'player_cards', 'banker', 'banker_cards',
            'final', 'advice'
        ])

deck = init_deck()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'p_list' not in st.session_state:
    st.session_state.p_list = []
if 'b_list' not in st.session_state:
    st.session_state.b_list = []

def update_deck(history, p_list, b_list):
    tmp_deck = init_deck()
    for h in history:
        for card in h.get('p_list', []) + h.get('b_list', []):
            tmp_deck[card] -= 1
    for card in p_list + b_list:
        if tmp_deck[card] > 0:
            tmp_deck[card] -= 1
    return tmp_deck

st.set_page_config('百家樂Web手機版', layout='centered')
st.markdown('<h2 style="text-align:center; font-size:2.2rem;">百家樂 比對分析 (手機優化)</h2>', unsafe_allow_html=True)

# --- 數字按鈕 UI ---
def number_pad(side):
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    for i in range(1,11):
        if (i-1)%4==0: col = col1
        elif (i-1)%4==1: col = col2
        elif (i-1)%4==2: col = col3
        else: col = col4
        if col.button(str(i), key=f'{side}_card_{i}', use_container_width=True):
            st.session_state[f'{side}_list'].append(i)
    # J Q K
    col1, col2, col3 = st.columns([1,1,1])
    for idx, face in enumerate(['J', 'Q', 'K']):
        if col1.button(face, key=f'{side}_card_{face}', use_container_width=True) if idx==0 \
        else col2.button(face, key=f'{side}_card_{face}', use_container_width=True) if idx==1 \
        else col3.button(face, key=f'{side}_card_{face}', use_container_width=True):
            st.session_state[f'{side}_list'].append(FACE_TO_NUM[face])
    # 刪除按鈕
    if st.button('刪除一張', key=f'{side}_del', use_container_width=True):
        if st.session_state[f'{side}_list']:
            st.session_state[f'{side}_list'].pop()
    if st.button('全部清除', key=f'{side}_clear', use_container_width=True):
        st.session_state[f'{side}_list'] = []

# --- UI區 ---
with st.container():
    st.markdown('#### 閒家出牌')
    if 'p_list' not in st.session_state:
        st.session_state.p_list = []
    number_pad('p')
    st.write("已選牌:", show_cards(st.session_state.p_list))
    st.write("點數:", calc_baccarat_point(st.session_state.p_list) if st.session_state.p_list else "")

    st.markdown('#### 莊家出牌')
    if 'b_list' not in st.session_state:
        st.session_state.b_list = []
    number_pad('b')
    st.write("已選牌:", show_cards(st.session_state.b_list))
    st.write("點數:", calc_baccarat_point(st.session_state.b_list) if st.session_state.b_list else "")

# 剩餘牌池顯示
deck_show = deck_str(update_deck(st.session_state.history, st.session_state.p_list, st.session_state.b_list))
st.markdown(f'<div style="color:#008080;font-weight:bold;font-size:1rem;">剩餘牌池：{deck_show}</div>', unsafe_allow_html=True)

# --- 操作按鈕 ---
col1, col2, col3 = st.columns(3)
with col1:
    比對 = st.button('比對', use_container_width=True)
with col2:
    清空 = st.button('全部清空', use_container_width=True)
with col3:
    匯出 = st.button('匯出Excel', use_container_width=True)

# --- 主邏輯 ---
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
    st.success(f'本局結果：閒={p_point} [{show_cards(p_list)}] 莊={b_point} [{show_cards(b_list)}] 結果={advice}')
    st.session_state.p_list = []
    st.session_state.b_list = []

if 清空:
    st.session_state.p_list = []
    st.session_state.b_list = []

if 匯出:
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    sheetname = f'牌局記錄{pd.Timestamp.now().strftime("%m%d_%H%M%S")}'
    excel_out = CSV_FILE.replace('.csv', '.xlsx')
    if os.path.exists(excel_out):
        os.remove(excel_out)
    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheetname, index=False)
    st.success(f"已匯出：{excel_out}")

# 比對預測
pred, rate = ai_predict_next_adviceN_only(CSV_FILE, N=3)
auto_pred, auto_rate = ai_predict_next_adviceN_only(CSV_FILE, N=6)
st.markdown(f'**比對預測(3局)：** {pred}')
st.markdown(f'**比對預測(6局)：** {auto_pred}')
st.markdown(f'**比對正確率：** {auto_rate}')

# 記錄區
st.markdown('---')
st.markdown('### 歷史紀錄')
try:
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    st.dataframe(df.tail(20), use_container_width=True)
except:
    st.warning('目前無紀錄資料')

