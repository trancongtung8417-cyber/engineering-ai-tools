import streamlit as st
from streamlit_gsheets import GSheetsConnection
from groq import Groq
import pandas as pd

# -----------------------------
# CẤU HÌNH TRANG
# -----------------------------
st.set_page_config(
    page_title="Hệ thống Tiệm Trà AI",
    page_icon="🍹",
    layout="centered"
)

st.title("🍹 Quản Lý Tiệm Trà Thông Minh")

# -----------------------------
# KẾT NỐI GOOGLE SHEETS
# -----------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ggWWPxqe8zjM7Ydp0BE7KaUB1qG87qahq0EVJbCjGZM"

# -----------------------------
# HÀM LOAD DATA
# -----------------------------
def load_data():
    df = conn.read(
        spreadsheet=SPREADSHEET_URL,
        worksheet="Sheet1",
        ttl=5
    )
    return df

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()

# kiểm tra cột
required_cols = ["Tên", "Số điện thoại", "Số điểm"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Google Sheet thiếu cột: {col}")
        st.stop()

# -----------------------------
# TABS
# -----------------------------
tab_ops, tab_marketing, tab_admin = st.tabs([
    "⚡ Vận Hành (Tích Điểm)",
    "🪄 Marketing AI",
    "📈 Quản Lý & Báo Cáo"
])

# ====================================================
# TAB 1 - VẬN HÀNH
# ====================================================
with tab_ops:

    st.subheader("💳 Tích Điểm Khách Hàng")

    df = load_data()

    sdt = st.text_input("Nhập số điện thoại:", key="phone_ops")

    if sdt:

        khach = df[df["Số điện thoại"].astype(str) == sdt]

        if not khach.empty:

            idx = khach.index[0]

            name = khach.iloc[0]["Tên"]
            diem = int(khach.iloc[0]["Số điểm"])

            st.success(f"Khách: {name}")
            st.info(f"Số điểm hiện tại: {diem} ⭐")

            if st.button("➕ Cộng 1 điểm"):

                df.at[idx, "Số điểm"] = diem + 1

                conn.update(
                    worksheet="Sheet1",
                    data=df
                )

                st.success("Đã cộng điểm!")
                st.rerun()

        else:
            st.warning("Khách chưa tồn tại. Hãy thêm ở tab Quản Lý.")

# ====================================================
# TAB 2 - MARKETING AI
# ====================================================
with tab_marketing:

    st.subheader("🤖 AI Viết Nội Dung Marketing")

    topic = st.text_input("Nhập món mới hoặc khuyến mãi")

    if st.button("✨ Tạo nội dung quảng cáo"):

        if topic == "":
            st.warning("Hãy nhập nội dung")

        else:

            if "GROQ_API_KEY" not in st.secrets:
                st.error("Thiếu GROQ_API_KEY trong secrets")
            else:

                client = Groq(api_key=st.secrets["GROQ_API_KEY"])

                with st.spinner("AI đang viết bài..."):

                    res = client.chat.completions.create(

                        model="llama-3.3-70b-versatile",

                        messages=[
                            {
                                "role": "user",
                                "content": f"""
                                Viết bài quảng cáo hấp dẫn cho quán trà sữa.

                                Chủ đề: {topic}

                                Nội dung:
                                - hấp dẫn
                                - có emoji
                                - ngắn gọn
                                - phù hợp đăng Facebook
                                """
                            }
                        ]
                    )

                st.write(res.choices[0].message.content)

# ====================================================
# TAB 3 - QUẢN LÝ
# ====================================================
with tab_admin:

    st.subheader("📊 Quản Lý Khách Hàng")

    df_admin = load_data()

    # -----------------------------
    # THÊM KHÁCH
    # -----------------------------
    with st.expander("➕ Thêm khách hàng mới"):

        with st.form("add_user"):

            new_name = st.text_input("Tên khách")
            new_phone = st.text_input("Số điện thoại")

            submitted = st.form_submit_button("Lưu khách")

            if submitted:

                if new_name == "" or new_phone == "":
                    st.warning("Nhập đầy đủ thông tin")

                else:

                    new_row = pd.DataFrame(
                        [[new_name, new_phone, 1]],
                        columns=["Tên", "Số điện thoại", "Số điểm"]
                    )

                    df_updated = pd.concat(
                        [df_admin, new_row],
                        ignore_index=True
                    )

                    conn.update(
                        worksheet="Sheet1",
                        data=df_updated
                    )

                    st.success("Đã thêm khách!")
                    st.rerun()

    # -----------------------------
    # HIỂN THỊ DATA
    # -----------------------------
    st.write("### 📋 Danh sách khách")

    st.dataframe(
        df_admin,
        use_container_width=True
    )

    # -----------------------------
    # BIỂU ĐỒ
    # -----------------------------
    if not df_admin.empty:

        st.write("### 📊 Biểu đồ điểm khách")

        chart_df = df_admin.set_index("Tên")

        st.bar_chart(chart_df["Số điểm"])