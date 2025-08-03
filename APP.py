import streamlit as st
import gspread
from collections import Counter

# Google Sheets 設定
SHEET_ID = '你的 Google Sheet ID'  # 例如 '1NxICz6N6lsvy1OBkvh1BIk-nLVgHoV3tLh9EUnN3kjc'
COLUMNS = [
    'player', 'player_cards',
    'banker', 'banker_cards',
    'final', 'advice',
    'big_eye_banker', 'small_banker', 'cockroach_banker',
    'big_eye_player', 'small_player', 'cockroach_player'
]

def get_sheet():
    gc = gspread.service_account(filename='client_secret.json')
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1
    return worksheet

def write_to_gsheet(record):
    worksheet = get_sheet()
    row = [record.get(col, '') for col in COLUMNS]
    worksheet.append_row(row, value_input_option='USER_ENTERED')

def delete_last_row():
    worksheet = get_sheet()
    values = worksheet.get_all_values()
    if len(values) > 1:  # 保留表頭
        worksheet.delete_rows(len(values))

def get_all_records():
    worksheet = get_sheet()
    return worksheet.get_all_records()

def ai_predict_next_adviceN_only(N=3):
    rows = get_all_records()
    advs = [r['advice'] for r in rows if r.get('advice')]
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

st.set_page_config('百家樂結果輸入（雲端）', layout='wide')
st.markdown("<h1 style='text-align:center;color:#154278;'>百家樂 結果輸入（Google Sheets雲端同步）</h1>", unsafe_allow_html=True)

if 'round_log' not in st.session_state:
    st.session_state.round_log = ""
if 'compare_result' not in st.session_state:
    st.rerun()

left, right = st.columns([2,3])

with left:
    st.markdown("### 當局結果")

    btn_cols = st.columns(4)
    if btn_cols[0].button("莊", use_container_width=True):
        record = {col: '' for col in COLUMNS}
        record['advice'] = '莊'
        write_to_gsheet(record)
        st.session_state.round_log += f"紀錄: 結果advice=莊\n"
        st.rerun()
    if btn_cols[1].button("閒", use_container_width=True):
        record = {col: '' for col in COLUMNS}
        record['advice'] = '閒'
        write_to_gsheet(record)
        st.session_state.round_log += f"紀錄: 結果advice=閒\n"
        st.rerun()
    if btn_cols[2].button("和", use_container_width=True):
        record = {col: '' for col in COLUMNS}
        record['advice'] = '和'
        write_to_gsheet(record)
        st.session_state.round_log += f"紀錄: 結果advice=和\n"
        st.rerun()
    if btn_cols[3].button("刪除", use_container_width=True):
        delete_last_row()
        logs = st.session_state.round_log.strip().split("\n")
        if logs:
            logs = logs[:-1]
            st.session_state.round_log = "\n".join(logs) + ("\n" if logs else "")
        st.rerun()

    st.markdown("---")
    btn2 = st.columns(2)
    if btn2[0].button('比對', use_container_width=True):
        pred3, rate3 = ai_predict_next_adviceN_only(N=3)
        pred6, rate6 = ai_predict_next_adviceN_only(N=6)
        st.session_state.compare_result = {
            'pred3': pred3, 'rate3': rate3,
            'pred6': pred6, 'rate6': rate6
        }
        st.rerun()
    if btn2[1].button('重設牌池', use_container_width=True):
        st.session_state.round_log = ""
        st.rerun()

    st.markdown("---")
    if st.button('儲存牌局', use_container_width=True):
        # 直接在雲端表格，不需要本地excel儲存
        st.success(f"所有紀錄都自動同步到 Google Sheets，不需手動儲存！")

with right:
    st.markdown("#### 比對預測")
    compare_result = st.session_state.get('compare_result', {})
    st.markdown(f"**比對(3局)：** <span style='color:blue;'>{compare_result.get('pred3', '')}</span>", unsafe_allow_html=True)
    st.markdown(f"**比對(6局)：** <span style='color:blue;'>{compare_result.get('pred6', '')}</span>", unsafe_allow_html=True)
    st.markdown(f"**正確率：** <span style='color:blue;'>{compare_result.get('rate6', '')}</span>", unsafe_allow_html=True)
    st.markdown("#### 牌局記錄區：")
    st.text_area('', st.session_state.round_log, height=300, key='round_log_show', disabled=True)
