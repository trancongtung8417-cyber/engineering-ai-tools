import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# ====== CẤU HÌNH ======
SHEET_NAME = "Sheet1"

st.set_page_config(page_title="HILTI - Trà Trái Cây", layout="centered")

st.title("🍓 Quán Trà Trái Cây")
st.subheader("Hệ thống tích điểm khách hàng")

# ====== KẾT NỐI GOOGLE SHEETS ======
conn = st.connection("gsheets", type=GSheetsConnection)

# ====== LOAD DATA ======
@st.cache_data(ttl=5)
def load_data():
    df = conn.read(worksheet=SHEET_NAME)
    df["Số Điện Thoại"] = df["Số Điện Thoại"].astype(str)
    return df

df = load_data()

# ====== MENU ======
menu = ["🎯 Tích Điểm", "📝 Đăng Ký Khách Mới", "📋 Danh Sách Khách"]
choice = st.sidebar.selectbox("Menu", menu)

# ====================================================
# 🎯 TÍCH ĐIỂM
# ====================================================

if choice == "🎯 Tích Điểm":

    st.header("Tích điểm cho khách")

    sdt = st.text_input("Nhập số điện thoại")

    if sdt:

        customer = df[df["Số Điện Thoại"] == sdt]

        if not customer.empty:

            idx = customer.index[0]

            name = customer.iloc[0]["Tên Khách Hàng"]
            points = int(customer.iloc[0]["Điểm Tích Lũy"])

            st.success(f"Khách hàng: **{name}**")
            st.info(f"Điểm hiện tại: **{points}/5**")

            if st.button("➕ Cộng 1 điểm", use_container_width=True):

                new_points = points + 1

                if new_points >= 5:

                    st.balloons()

                    st.success("🎁 ĐỦ 5 ĐIỂM – TẶNG 1 LY MIỄN PHÍ!")

                    new_points = 0
                    wait = 3

                else:

                    st.toast(f"Đã cộng! Hiện có {new_points} điểm")
                    wait = 1

                df.at[idx, "Điểm Tích Lũy"] = new_points
                df.at[idx, "Ngày Cập Nhật"] = datetime.now().strftime("%d/%m/%Y %H:%M")

                conn.update(worksheet=SHEET_NAME, data=df)

                time.sleep(wait)
                st.rerun()

        else:

            st.error("Chưa có khách hàng này!")

# ====================================================
# 📝 ĐĂNG KÝ KHÁCH
# ====================================================

elif choice == "📝 Đăng Ký Khách Mới":

    st.header("Đăng ký khách hàng")

    with st.form("register_form"):

        name = st.text_input("Tên khách hàng")
        phone = st.text_input("Số điện thoại")

        submit = st.form_submit_button("Lưu")

        if submit:

            if phone in df["Số Điện Thoại"].values:

                st.warning("Số điện thoại đã tồn tại!")

            elif name and phone:

                new_row = pd.DataFrame(
                    [[name, phone, 0, datetime.now().strftime("%d/%m/%Y %H:%M")]],
                    columns=df.columns
                )

                df_new = pd.concat([df, new_row], ignore_index=True)

                conn.update(worksheet=SHEET_NAME, data=df_new)

                st.success("Đã thêm khách hàng!")

                time.sleep(1)
                st.rerun()

            else:

                st.warning("Vui lòng nhập đầy đủ thông tin")

# ====================================================
# 📋 DANH SÁCH KHÁCH
# ====================================================

elif choice == "📋 Danh Sách Khách":

    st.header("Danh sách khách hàng")

    st.dataframe(df, use_container_width=True)

    if st.button("🔄 Tải lại dữ liệu"):
        st.cache_data.clear()
        st.rerun()