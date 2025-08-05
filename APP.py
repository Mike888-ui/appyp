import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="百家樂 AI Web", layout="centered")
st.title("百家樂 AI 分析 Web App（簡易 MVP）")

CSV_FILE = 'ai_train_history.csv'

# --- 牌面相關 function ---
NUM_TO_FACE = {11: 'J', 12: 'Q', 13: 'K'}
FACE_TO_NUM = {'J': 11, 'Q': 12, 'K': 13}

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

# --- 預測功能，直接複製你的桌面版 ---
def ai_predict_next_adviceN_only(df, N=3):
    if 'advice' not in df.columns:
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

# --- 主頁 UI ---
st.markdown("### 1. 輸入牌面")
col1, col2 = st.columns(2)
with col1:
    player_cards = st.text_input('閒家牌面 (1~13/JQK, 逗號分隔)', key='p_input')
with col2:
    banker_cards = st.text_input('莊家牌面 (1~13/JQK, 逗號分隔)', key='b_input')

if 'deck' not in st.session_state:
    st.session_state['deck'] = init_deck()

if st.button('比對 / 預測'):
    p_list = parse_cards(player_cards)
    b_list = parse_cards(banker_cards)
    p_point = calc_baccarat_point(p_list) if p_list else None
    b_point = calc_baccarat_point(b_list) if b_list else None

    if p_point is None or b_point is None:
        st.error("請正確輸入莊/閒牌面")
    else:
        if p_point > b_point:
            advice = '閒'
        elif p_point < b_point:
            advice = '莊'
        else:
            advice = '和'

        # 寫入CSV
        record = {
            'player': p_point,
            'player_cards': show_cards(p_list),
            'banker': b_point,
            'banker_cards': show_cards(b_list),
            'final': abs(p_point-b_point),
            'advice': advice,
        }
        file_exists = os.path.exists(CSV_FILE)
        df = pd.DataFrame([record])
        if file_exists:
            df.to_csv(CSV_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')
        else:
            df.to_csv(CSV_FILE, mode='w', index=False, header=True, encoding='utf-8-sig')
        st.success(f"已記錄：閒 {p_point} [{show_cards(p_list)}]，莊 {b_point} [{show_cards(b_list)}]，結果 {advice}")

        # 重新讀取紀錄
        st.session_state['history'] = pd.read_csv(CSV_FILE, encoding='utf-8-sig')

        # 牌池動態更新
        deck = init_deck()
        if 'history' in st.session_state:
            for idx, row in st.session_state['history'].iterrows():
                for c in parse_cards(row['player_cards']) + parse_cards(row['banker_cards']):
                    deck[c] -= 1
        st.session_state['deck'] = deck

# 顯示剩餘牌池
st.markdown("### 2. 剩餘牌池")
st.info(deck_str(st.session_state['deck']))

# 預測顯示
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    pred_3 = ai_predict_next_adviceN_only(df, 3)
    pred_6 = ai_predict_next_adviceN_only(df, 6)
    st.markdown(f"#### 比對預測 (3局)： {pred_3}")
    st.markdown(f"#### 比對預測 (6局)： {pred_6}")

# 歷史紀錄
st.markdown("### 3. 歷史紀錄")
if os.path.exists(CSV_FILE):
    history = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    st.dataframe(history, use_container_width=True)
    # 匯出下載
    st.download_button("下載 CSV", data=history.to_csv(index=False), file_name="ai_train_history.csv")
    history.to_excel("ai_train_history.xlsx", index=False)
    with open("ai_train_history.xlsx", "rb") as f:
        st.download_button("下載 Excel", data=f, file_name="ai_train_history.xlsx")

# 牌池重設
if st.button('重設牌池 / 歷史'):
    st.session_state['deck'] = init_deck()
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    st.experimental_rerun()
