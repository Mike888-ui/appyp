import streamlit as st
import pandas as pd
import os
from collections import Counter

csv_file = "ai_train_history.csv"

# 自動建立或修正csv表頭
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["result", "note"])
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
else:
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    # 修正欄位
    if "result" not in df.columns:
        if len(df.columns) == 1:
            df["note"] = ""
            df.rename(columns={df.columns[0]: "result"}, inplace=True)
        else:
            df = pd.DataFrame(columns=["result", "note"])
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    if "note" not in df.columns:
        df["note"] = ""
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="百家樂 Web 比對分析", layout="centered")
st.title("百家樂 Web 比對分析")

# ===== 操作區塊 =====
col1, col2, col3 = st.columns([3,2,2])
with col1:
    result = st.selectbox("請選擇當局結果", ["", "莊", "閒", "和"], key="resultbox")
    note = st.text_input("備註 (可選)", key="note_box", placeholder="例如：路單/事件/特別說明...")

with col2:
    add_btn = st.button("送出", key="add_btn")
with col3:
    del_btn = st.button("刪除上一筆", key="del_btn")

# ===== 新增/刪除功能 =====
msg = ""
if add_btn:
    if result:
        df = pd.concat([df, pd.DataFrame({"result":[result], "note":[note]})], ignore_index=True)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        msg = f"✅ 已記錄：{result}（備註：{note}）"
    else:
        msg = "❌ 請先選擇本局結果！"

if del_btn:
    if len(df) > 0:
        deleted = df.iloc[-1]["result"]
        deleted_note = df.iloc[-1]["note"] if "note" in df.columns else ""
        df = df.iloc[:-1]
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        msg = f"🗑️ 已刪除上一筆紀錄：{deleted}（備註：{deleted_note}）"
    else:
        msg = "⚠️ 沒有資料可以刪除"

if msg:
    st.info(msg)

# ===== 比對預測 =====
def ai_predict_next_adviceN_only(df, N=3):
    advs = df['result'].astype(str).tolist()
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

st.divider()
st.subheader("比對預測區")

pred_3, rate_3 = ai_predict_next_adviceN_only(df, N=3)
pred_6, rate_6 = ai_predict_next_adviceN_only(df, N=6)

st.write("比對預測 (3局)：", pred_3)
st.write("比對預測 (6局)：", pred_6)
st.write("比對正確率：", rate_6)

# ===== 儲存紀錄 =====
colx1, colx2 = st.columns(2)
with colx1:
    if st.button("匯出Excel", key="save_btn"):
        excel_out = csv_file.replace('.csv', '.xlsx')
        df.to_excel(excel_out, index=False)
        st.success(f"已將本次紀錄存為 {excel_out}")

with colx2:
    if st.button("匯出純文字", key="export_txt"):
        txt_out = csv_file.replace('.csv', '.txt')
        # 以「流水號. 結果（備註）」格式儲存
        with open(txt_out, "w", encoding="utf-8-sig") as f:
            for i, row in df.iterrows():
                line = f"{i+1}. {row['result']}"
                if row["note"]:
                    line += f"（{row['note']}）"
                f.write(line + "\n")
        st.success(f"已匯出純文字紀錄：{txt_out}")

# ===== 歷史紀錄區 =====
st.divider()
st.subheader("歷史記錄")
if len(df) == 0:
    st.write("尚無紀錄")
else:
    for i, row in df.iterrows():
        if row["note"]:
            st.write(f"{i+1}. {row['result']}（{row['note']}）")
        else:
            st.write(f"{i+1}. {row['result']}")
