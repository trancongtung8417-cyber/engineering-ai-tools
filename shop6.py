import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# Cấu hình trang
st.set_page_config(page_title="HILTI - Trà Trái Cây", layout="centered")

st.title("🍎 Quán Trà Trái Cây 🍓")
st.subheader("Hệ thống Tích điểm trực tuyến")

# Khởi tạo kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Hàm đọc dữ liệu từ Sheets
def load_data():
    return conn.read(ttl="0") # ttl="0" để luôn lấy dữ liệu mới nhất

# Load dữ liệu hiện tại
df = load_data()

menu = ["Tích Điểm", "Đăng Ký Khách Mới", "Danh Sách Khách Hàng"]
choice = st.sidebar.selectbox("Menu Quản Lý", menu)

# --- CHỨC NĂNG 1: TÍCH ĐIỂM ---
if choice == "Tích Điểm":
    st.header("🎯 Tích Điểm Nhanh")
    sdt_input = st.text_input("Nhập Số Điện Thoại khách hàng:")
    
    if sdt_input:
        # Tìm khách hàng (ép kiểu SDT về string để so sánh)
        df['Số Điện Thoại'] = df['Số Điện Thoại'].astype(str)
        user_index = df.index[df["Số Điện Thoại"] == sdt_input].tolist()
        
        if user_index:
            idx = user_index[0]
            name = df.at[idx, "Tên Khách Hàng"]
            current_points = int(df.at[idx, "Điểm Tích Lũy"])
            
            st.success(f"Khách hàng: **{name}**")
            st.info(f"Số điểm hiện tại: **{current_points}/5**")
            
            if st.button("➕ Cộng 1 Điểm", use_container_width=True):
                new_points = current_points + 1
                
                if new_points >= 5:
                    st.balloons()
                    st.markdown("""
                        <div style="background-color: #FF4B4B; padding: 20px; border-radius: 10px; border: 5px solid yellow; text-align: center;">
                            <h1 style="color: white; margin: 0;">🎁 ĐỦ 5 ĐIỂM RỒI! 🎁</h1>
                            <h2 style="color: yellow; margin: 10px 0;">TẶNG KHÁCH 1 LY MIỄN PHÍ</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    new_points = 0
                    time_to_wait = 3
                else:
                    st.toast(f"Đã cộng! Hiện có {new_points} điểm", icon="✅")
                    time_to_wait = 1

                # Cập nhật DataFrame và ghi đè lên Google Sheets
                df.at[idx, "Điểm Tích Lũy"] = new_points
                df.at[idx, "Ngày Cập Nhật"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                conn.update(data=df)
                
                time.sleep(time_to_wait)
                st.rerun()
        else:
            st.error("Chưa có khách này. Vui lòng qua mục Đăng Ký!")

# --- CHỨC NĂNG 2: ĐĂNG KÝ MỚI ---
elif choice == "Đăng Ký Khách Mới":
    st.header("📝 Đăng Ký Thành Viên")
    with st.form("reg_form"):
        new_name = st.text_input("Họ và Tên:")
        new_sdt = st.text_input("Số Điện Thoại:")
        submit = st.form_submit_button("Lưu lên hệ thống")
        
        if submit:
            if new_sdt in df["Số Điện Thoại"].astype(str).values:
                st.warning("Số điện thoại này đã có rồi!")
            elif new_name and new_sdt:
                new_row = pd.DataFrame([[new_name, new_sdt, 0, datetime.now().strftime("%d/%m/%Y %H:%M")]], 
                                       columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.success("Đã lưu vào Google Sheets!")
                time.sleep(1)
                st.rerun()

# --- CHỨC NĂNG 3: XEM DANH SÁCH ---
elif choice == "Danh Sách Khách Hàng":
    st.header("📋 Dữ liệu từ Google Sheets")
    st.dataframe(df, use_container_width=True)
    
    # Nút làm mới dữ liệu
    if st.button("🔄 Tải lại dữ liệu"):
        st.rerun()