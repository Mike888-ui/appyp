import streamlit as st
import pandas as pd
import os
from collections import Counter

csv_file = "ai_train_history.csv"

# ===== 資料初始化，確保advice欄存在 =====
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["advice"])
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
else:
    df = pd.read_csv(csv_file, encoding='utf-8-sig# ===== 百家樂簡化紀錄APP（手機/電腦優化版）=====
# 作者: MASA & 俊賢

import streamlit as st
import pandas as pd
import os
import csv
from collections import Counter

st.set_page_config(page_title='百家樂簡化紀錄APP', layout="centered")

st.markdown("""
<div style='text-align:center;font-size:2em;font-weight:bold;color:#1761e6;margin-bottom:0.3em'>百家樂簡化紀錄APP</div>
<div style='text-align:center;color:#888;font-size:1.1em;margin-bottom:1.2em'>設計：MASA & 俊賢</div>
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

def ai_predict_next_adviceN_only(csvfile, N=3):
    if not os.path.exists(csvfile): return '暫無相關數據資料', ''
    df = pd.read_csv(csvfile, encoding='utf-8-sig')
    if 'advice' not in df.columns: return '資料異常', ''
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

# -- 手機自適應：偵測螢幕寬度 --
def is_mobile():
    return st.runtime.scriptrunner.is_running_with_streamlit and st.query_params.get("device") == "mobile"
# 但 Streamlit cloud 不支援自動偵測，只能手動調整按鈕數量

# ========== 介面設計 ==========
def card_buttons(field_key, state_key):
    btn_vals = [1,2,3,4,5,6,7,8,9,10,11,12,13]
    btn_per_row = 4  # 手機建議4顆/row
    rows = [btn_vals[i:i+btn_per_row] for i in range(0, len(btn_vals), btn_per_row)]
    for row in rows:
        cols = st.columns(len(row))
        for idx, val in enumerate(row):
            if cols[idx].button(card_str(val), key=f'{field_key}{val}'):
                curr = parse_cards(st.session_state[state_key])
                if len(curr)<4: curr.append(val)
                st.session_state[state_key] = show_cards(curr)
                st.rerun()

st.write("#### 閒家牌")
if "_player_cards" not in st.session_state:
    st.session_state["_player_cards"] = ""
player_cards = st.text_input("輸入閒家牌(1~13/JQK)", value=st.session_state["_player_cards"], key="player_cards_input")
card_buttons('pc', "_player_cards")
if st.button("刪除(閒)", key="pdel"):
    curr = parse_cards(st.session_state["_player_cards"])
    if curr: curr.pop()
    st.session_state["_player_cards"] = show_cards(curr)
    st.rerun()
st.info(f"點數：{calc_baccarat_point(parse_cards(st.session_state['_player_cards']))}")

st.write("#### 莊家牌")
if "_banker_cards" not in st.session_state:
    st.session_state["_banker_cards"] = ""
banker_cards = st.text_input("輸入莊家牌(1~13/JQK)", value=st.session_state["_banker_cards"], key="banker_cards_input")
card_buttons('bc', "_banker_cards")
if st.button("刪除(莊)", key="bdel"):
    curr = parse_cards(st.session_state["_banker_cards"])
    if curr: curr.pop()
    st.session_state["_banker_cards"] = show_cards(curr)
    st.rerun()
st.info(f"點數：{calc_baccarat_point(parse_cards(st.session_state['_banker_cards']))}")

# 剩餘牌池
def update_deck():
    deck = init_deck()
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        df = df[[c for c in ['player_cards','banker_cards'] if c in df.columns]]
        for idx, row in df.iterrows():
            for k in ['player_cards','banker_cards']:
                if k in row and pd.notnull(row[k]):
                    for c in parse_cards(row[k]):
                        deck[c] -= 1
    for c in parse_cards(st.session_state["_player_cards"]) + parse_cards(st.session_state["_banker_cards"]):
        deck[c] -= 1
    return deck

st.info(f"剩餘牌池：{deck_str(update_deck())}")

# 比對/紀錄
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
    write_head = not os.path.exists(csv_file)
    with open(csv_file,'a',encoding='utf-8-sig',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=record.keys())
        if write_head: writer.writeheader()
        writer.writerow(record)
    st.success(f"已記錄: 閒={p_point}[{show_cards(p_list)}] 莊={b_point}[{show_cards(b_list)}] 結果={advice}")

    # 預測
    pred, rate = ai_predict_next_adviceN_only(csv_file, N=3)
    auto_pred, auto_rate = ai_predict_next_adviceN_only(csv_file, N=6)
    st.info(f"比對預測(3局)：{pred}")
    st.info(f"比對預測(6局)：{auto_pred}")
    st.info(f"比對正確率：{auto_rate}")

    st.session_state["_player_cards"] = ""
    st.session_state["_banker_cards"] = ""
    st.rerun()

# 匯出 Excel
if st.button("儲存紀錄為Excel"):
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    sheetname = f"牌局記錄{pd.Timestamp.now().strftime('%m%d_%H%M%S')}"
    excel_out = csv_file.replace('.csv', '.xlsx')
    if os.path.exists(excel_out): os.remove(excel_out)
    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheetname, index=False)
    st.success(f"已將本次紀錄到 {excel_out} [{sheetname}]")

# 歷史紀錄區
st.markdown("### 📝 歷史紀錄")
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    if 'player_cards' in df.columns and 'banker_cards' in df.columns and len(df)>0:
        st.dataframe(df.tail(30), use_container_width=True, height=350)
    else:
        st.info("目前紀錄檔無資料，請先紀錄一局")
else:
    st.info("尚無紀錄資料，請從上方建立第一筆紀錄")


    if "advice" not in df.columns:
        df = pd.DataFrame(columns=["advice"])
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="百家樂比對資料分析", layout="centered")
st.title("百家樂 比對資料分析（手機/電腦版）")

st.markdown("---")

# ===== 當局結果輸入操作區 =====
st.subheader("操作區")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("莊", use_container_width=True):
        st.session_state['advice_input'] = "莊"
with col2:
    if st.button("閒", use_container_width=True):
        st.session_state['advice_input'] = "閒"
with col3:
    if st.button("和", use_container_width=True):
        st.session_state['advice_input'] = "和"
with col4:
    if st.button("刪除", use_container_width=True):
        if len(df) > 0:
            df = df.iloc[:-1]
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            st.success("已刪除上一筆紀錄")
        else:
            st.warning("沒有可刪除資料")
with col5:
    if st.button("輸入", use_container_width=True):
        advice_input = st.session_state.get('advice_input', "")
        if advice_input:
            df = pd.concat([df, pd.DataFrame({"advice":[advice_input]})], ignore_index=True)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            st.success(f"已新增紀錄：{advice_input}")
            st.session_state['advice_input'] = ""
        else:
            st.error("請先按下莊/閒/和選擇結果！")

st.markdown("---")

# ===== 比對預測功能 =====
def ai_predict_next_adviceN_only(df, N=3):
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

# ========== 比對預測、顯示 ==============
st.subheader("比對預測區")
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("比對", use_container_width=True, key="compare_btn"):
        st.session_state['do_compare'] = True
with btn_col2:
    if st.button("儲存紀錄", use_container_width=True, key="save_btn"):
        excel_out = csv_file.replace('.csv', '.xlsx')
        df.to_excel(excel_out, index=False)
        st.success(f"已將紀錄存為 {excel_out}")

if st.session_state.get('do_compare', False):
    pred_3, rate_3 = ai_predict_next_adviceN_only(df, N=3)
    pred_6, rate_6 = ai_predict_next_adviceN_only(df, N=6)
    st.markdown(f"<div style='font-size:16px;font-weight:bold;'>比對預測(3局)：<span style='color:#1761e6'>{pred_3}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:16px;font-weight:bold;'>比對預測(6局)：<span style='color:#1761e6'>{pred_6}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:16px;font-weight:bold;'>比對正確率：<span style='color:#1761e6'>{rate_6}</span></div>", unsafe_allow_html=True)
    st.session_state['do_compare'] = False

st.markdown("---")

# ===== 記錄區（即時顯示所有歷史advice） =====
st.subheader("記錄區")
if len(df) == 0:
    st.write("尚無紀錄")
else:
    log = ""
    for i, row in df.iterrows():
        log += f"已紀錄: 結果advice={row['advice']}\n"
    st.text_area("歷史記錄", value=log, height=220, key="history_log", disabled=True, label_visibility="collapsed")
