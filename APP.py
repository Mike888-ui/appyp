# ===== 百家樂簡化紀錄APP（自訂合併邏輯/來源標記/欄位去重）=====
# 作者: MASA & 俊賢

import streamlit as st
import pandas as pd
import os
import csv
from collections import Counter

st.set_page_config(page_title='百家樂簡化紀錄APP', layout="centered")
st.markdown("""
<div style='text-align:center;font-size:1.5em;font-weight:bold;color:#1761e6;margin-bottom:0.2em'>百家樂簡化紀錄APP</div>
<div style='text-align:center;color:#888;font-size:1.1em;margin-bottom:1em'>設計：MASA & 俊賢</div>
""", unsafe_allow_html=True)

NUM_TO_FACE = {11: 'J', 12: 'Q', 13: 'K'}
FACE_TO_NUM = {'J': 11, 'Q': 12, 'K': 13}
def card_str(n): return NUM_TO_FACE.get(n, str(n))
def parse_cards(s):
    out = []
    for x in str(s).replace('，',',').replace(' ', ',').split(','):
        x = x.strip().upper()
        if not x: continue
        if x in FACE_TO_NUM: out.append(FACE_TO_NUM[x])
        elif x.isdigit() and 1 <= int(x) <= 13: out.append(int(x))
    return out[:4]
def show_cards(cards): return ','.join([card_str(c) for c in cards])
def calc_baccarat_point(cards): return sum((c if c < 10 else 0) for c in cards) % 10 if cards else None
def init_deck(): return {n: 32 for n in range(1, 14)}
def deck_str(deck): return ' '.join(f'{card_str(k)}:{deck[k]}' for k in range(1,14))

# ----- 資料合併（依player_cards+banker_cards去重，標記來源）-----
def load_data(N=None):
    xlsx_file = 'ai_train_history.xlsx'
    csv_file = 'ai_train_history.csv'
    dfs = []
    if os.path.exists(xlsx_file):
        df_xlsx = pd.read_excel(xlsx_file)
        df_xlsx["_source"] = "xlsx"
        dfs.append(df_xlsx)
    if os.path.exists(csv_file):
        df_csv = pd.read_csv(csv_file, encoding='utf-8-sig')
        df_csv["_source"] = "csv"
        dfs.append(df_csv)
    if not dfs:
        return pd.DataFrame()
    # 合併，依「player_cards, banker_cards」去重
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["player_cards", "banker_cards"], keep='first')
    # 排序（可根據需要調整）
    df = df.sort_values(by=["_source", "player_cards", "banker_cards"], ascending=[True, True, True], ignore_index=True)
    if N:
        return df.tail(N)
    return df

def ai_predict_next_adviceN_only(df, N=3):
    if df.empty or 'advice' not in df.columns: return '暫無相關數據資料', ''
    advs = df['advice'].astype(str).tolist()
    now_count = min(len(advs), N)
    if len(advs) < N: return '暫無相關數據資料', ''
    last_n = advs[-now_count:]
    matches = []
    for i in range(len(advs) - now_count):
        if advs[i:i+now_count] == last_n:
            if i + now_count < len(advs):
                matches.append(advs[i + now_count])
    if not matches: return '暫無相關數據資料', ''
    stat = Counter(matches)
    most, cnt = stat.most_common(1)[0]
    percent = int(cnt / len(matches) * 100)
    show_detail = f"莊：{stat.get('莊',0)}筆  閒：{stat.get('閒',0)}筆  和：{stat.get('和',0)}筆"
    return f"{most} ({percent}%)「{show_detail}」", f"{percent}%"

csv_file = 'ai_train_history.csv'
if not os.path.exists(csv_file):
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'player', 'player_cards',
            'banker', 'banker_cards',
            'final', 'advice'
        ])
if "deck" not in st.session_state: st.session_state.deck = init_deck()
if "history" not in st.session_state: st.session_state.history = []

col1, col2 = st.columns(2)

# ========== 閒家牌 ==========
with col1:
    st.write("### 閒家牌")
    if "_player_cards" not in st.session_state:
        st.session_state["_player_cards"] = ""
    player_cards = st.text_input("輸入閒家牌(1~13/JQK)", value=st.session_state["_player_cards"], key="player_cards_input")
    btns = st.columns(7)
    for idx, val in enumerate([1,2,3,4,5,6,7,8,9,10,11,12,13]):
        b = btns[idx%7]
        if b.button(card_str(val), key=f'pc{val}'):
            curr = parse_cards(st.session_state["_player_cards"])
            if len(curr)<4: curr.append(val)
            st.session_state["_player_cards"] = show_cards(curr)
            st.rerun()
    if st.button("刪除", key="pdel"):
        curr = parse_cards(st.session_state["_player_cards"])
        if curr: curr.pop()
        st.session_state["_player_cards"] = show_cards(curr)
        st.rerun()
    st.info(f"點數：{calc_baccarat_point(parse_cards(st.session_state['_player_cards']))}")

# ========== 莊家牌 ==========
with col2:
    st.write("### 莊家牌")
    if "_banker_cards" not in st.session_state:
        st.session_state["_banker_cards"] = ""
    banker_cards = st.text_input("輸入莊家牌(1~13/JQK)", value=st.session_state["_banker_cards"], key="banker_cards_input")
    btns = st.columns(7)
    for idx, val in enumerate([1,2,3,4,5,6,7,8,9,10,11,12,13]):
        b = btns[idx%7]
        if b.button(card_str(val), key=f'bc{val}'):
            curr = parse_cards(st.session_state["_banker_cards"])
            if len(curr)<4: curr.append(val)
            st.session_state["_banker_cards"] = show_cards(curr)
            st.rerun()
    if st.button("刪除", key="bdel"):
        curr = parse_cards(st.session_state["_banker_cards"])
        if curr: curr.pop()
        st.session_state["_banker_cards"] = show_cards(curr)
        st.rerun()
    st.info(f"點數：{calc_baccarat_point(parse_cards(st.session_state['_banker_cards']))}")

# 剩餘牌池計算
def update_deck():
    deck = init_deck()
    df = load_data()
    if not df.empty:
        for idx, row in df.iterrows():
            for k in ['player_cards','banker_cards']:
                if k in row and pd.notnull(row[k]):
                    for c in parse_cards(row[k]):
                        deck[c] -= 1
    for c in parse_cards(st.session_state["_player_cards"]) + parse_cards(st.session_state["_banker_cards"]):
        deck[c] -= 1
    return deck

st.info(f"剩餘牌池：{deck_str(update_deck())}")

# 比對/紀錄/顯示
if st.button("比對/紀錄"):
    p_list = parse_cards(st.session_state["_player_cards"])
    b_list = parse_cards(st.session_state["_banker_cards"])
    p_point = calc_baccarat_point(p_list)
    b_point = calc_baccarat_point(b_list)
    iff = abs(p_point-b_point) if (p_point is not None and b_point is not None) else ''
    advice = ""
    if p_point is None or b_point is None: advice = ""
    elif p_point > b_point: advice="閒"
    elif p_point < b_point: advice="莊"
    else: advice="和"
    record = {
        'player':p_point, 'player_cards':show_cards(p_list),
        'banker':b_point, 'banker_cards':show_cards(b_list),
        'final':iff, 'advice':advice
    }
    # -- 寫入CSV（無論目前用 xlsx/csv查詢都寫入csv，保證通用）
    write_head = not os.path.exists(csv_file)
    with open(csv_file,'a',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=record.keys())
        if write_head: writer.writeheader()
        writer.writerow(record)
    st.success(f"已記錄: 閒={p_point}[{show_cards(p_list)}] 莊={b_point}[{show_cards(b_list)}] 結果={advice}")

    # 3/6局預測
    df_hist = load_data()
    pred, rate = ai_predict_next_adviceN_only(df_hist, N=3)
    auto_pred, auto_rate = ai_predict_next_adviceN_only(df_hist, N=6)
    st.info(f"比對預測(3局)：{pred}")
    st.info(f"比對預測(6局)：{auto_pred}")
    st.info(f"比對正確率：{auto_rate}")

    # 清空欄位
    st.session_state["_player_cards"] = ""
    st.session_state["_banker_cards"] = ""
    st.rerun()

# 匯出 Excel
if st.button("儲存紀錄為Excel"):
    df = load_data()
    sheetname = f"牌局記錄{pd.Timestamp.now().strftime('%m%d_%H%M%S')}"
    excel_out = csv_file.replace('.csv', '.xlsx')
    if os.path.exists(excel_out): os.remove(excel_out)
    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheetname, index=False)
    st.success(f"已將本次紀錄到 {excel_out} [{sheetname}]")

# 歷史紀錄
st.markdown("#### 歷史紀錄")
df_hist = load_data(30)
if not df_hist.empty and 'player_cards' in df_hist.columns and 'banker_cards' in df_hist.columns:
    st.dataframe(df_hist, use_container_width=True)
else:
    st.info("尚無紀錄資料")
