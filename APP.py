import streamlit as st
import pandas as pd
import csv, os
from collections import Counter

NUM_TO_FACE = {11: 'J', 12: 'Q', 13: 'K'}
FACE_TO_NUM = {'J': 11, 'Q': 12, 'K': 13}

def card_str(n):
    return NUM_TO_FACE.get(n, str(n))

def parse_cards(s):
    out = []
    for x in str(s).replace('，', ',').replace(' ', ',').split(','):
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
    return sum((c if c < 10 else 0) for c in cards) % 10 if cards else ''

def init_deck():
    return {n: 32 for n in range(1, 14)}

def deck_str(deck):
    return ' '.join(f'{card_str(k)}:{deck[k]}' for k in range(1, 14))

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

# 設定資料檔案
csv_file = os.path.join(os.path.dirname(__file__), 'ai_train_history.csv')
if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'player', 'player_cards',
            'banker', 'banker_cards',
            'final', 'advice'
        ])

st.set_page_config(page_title="百家樂自動學習助手", layout="centered")
st.title("百家樂自動學習分析 (手機版精簡)")

# -- 狀態
if 'deck' not in st.session_state:
    st.session_state.deck = init_deck()
if 'round_log' not in st.session_state:
    st.session_state.round_log = []

# -- 牌面輸入
with st.form("input_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        player_input = st.text_input("閒家牌(1~13, JQK 用英文)", key='player_cards')
    with col2:
        banker_input = st.text_input("莊家牌(1~13, JQK 用英文)", key='banker_cards')
    submitted = st.form_submit_button("紀錄/比對")

def write_to_csv(filename, record):
    row = [
        record['player'],
        show_cards(record.get('p_list', [])),
        record['banker'],
        show_cards(record.get('b_list', [])),
        record['final'],
        record['advice']
    ]
    with open(filename, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

if submitted:
    p_list = parse_cards(st.session_state.get('player_cards', ''))
    b_list = parse_cards(st.session_state.get('banker_cards', ''))
    p_point = calc_baccarat_point(p_list)
    b_point = calc_baccarat_point(b_list)
    iff = abs(p_point - b_point) if (p_list and b_list) else ''
    if p_point == '' or b_point == '':
        advice = ''
    elif p_point > b_point:
        advice = '閒'
    elif p_point < b_point:
        advice = '莊'
    else:
        advice = '和'
    record = {
        'player': p_point, 'banker': b_point, 'final': iff, 'advice': advice,
        'p_list': p_list, 'b_list': b_list
    }
    write_to_csv(csv_file, record)
    # 累積紀錄區
    log_str = f"紀錄: 閒={p_point} [{show_cards(p_list)}] 莊={b_point} [{show_cards(b_list)}] 結果advice={advice}"
    st.session_state.round_log.append(log_str)
    st.success(log_str)

    # 比對
    pred, rate = ai_predict_next_adviceN_only(csv_file, N=3)
    auto_pred, auto_rate = ai_predict_next_adviceN_only(csv_file, N=6)
    st.info(f"比對預測(3局)：{pred}")
    st.info(f"比對預測(6局)：{auto_pred}")
    st.write(f"比對正確率：{auto_rate}")

# -- 牌池餘數（根據目前已紀錄）
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    hist = df.to_dict('records')
else:
    hist = []

tmp_deck = init_deck()
for h in hist:
    for c in parse_cards(h.get('player_cards', '')):
        tmp_deck[c] -= 1
    for c in parse_cards(h.get('banker_cards', '')):
        tmp_deck[c] -= 1

# -- 紀錄區顯示（像你第一張圖，會一直累積每局）
st.markdown("#### 記錄區：")
st.text('\n'.join(st.session_state.round_log[-30:]))  # 顯示最近30筆（防爆量）

# -- 牌池顯示
st.markdown("#### 剩餘牌池")
st.code(deck_str(tmp_deck))

# -- 匯出Excel（仍保留）
if st.button("匯出Excel"):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        excel_out = csv_file.replace('.csv', '.xlsx')
        if os.path.exists(excel_out):
            os.remove(excel_out)
        with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="牌局記錄", index=False)
        st.success(f"已匯出: {excel_out}")

st.caption("手機/電腦可用，歷史資料不顯示表格，只在即時記錄區顯示。")
