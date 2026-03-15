import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="Trà Trái Cây - Tích Điểm", layout="centered")

# File lưu trữ dữ liệu
DATA_FILE = "customers.csv"

# Khởi tạo file nếu chưa có
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Tên Khách Hàng", "Số Điện Thoại", "Điểm Tích Lũy", "Ngày Cập Nhật"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE, dtype={"Số Điện Thoại": str})

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Giao diện chính
st.title("🍎 Quán Trà Trái Cây 🍓")
st.subheader("Hệ thống Quản lý & Tích điểm")

menu = ["Tích Điểm", "Đăng Ký Khách Mới", "Danh Sách Khách Hàng"]
choice = st.sidebar.selectbox("Menu Quản Lý", menu)

df = load_data()

# --- CHỨC NĂNG 1: TÍCH ĐIỂM ---
if choice == "Tích Điểm":
    st.header("🎯 Tích Điểm Nhanh")
    sdt_input = st.text_input("Nhập Số Điện Thoại khách hàng:")
    
    if sdt_input:
        user_row = df[df["Số Điện Thoại"] == sdt_input]
        
        if not user_row.empty:
            name = user_row.iloc[0]["Tên Khách Hàng"]
            current_points = user_row.iloc[0]["Điểm Tích Lũy"]
            
            st.success(f"Khách hàng: **{name}**")
            st.info(f"Số điểm hiện tại: **{current_points}**")
            
            if st.button("➕ Cộng 1 Điểm"):
                new_points = current_points + 1
                
                # Kiểm tra đủ 5 điểm chưa
                if new_points >= 5:
                    st.balloons()
                    st.warning("🎉 KHÁCH ĐÃ ĐỦ 5 ĐIỂM! TẶNG 1 LY MIỄN PHÍ VÀ RESET ĐIỂM.")
                    new_points = 0
                
                df.loc[df["Số Điện Thoại"] == sdt_input, "Điểm Tích Lũy"] = new_points
                df.loc[df["Số Điện Thoại"] == sdt_input, "Ngày Cập Nhật"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(df)
                st.rerun()
        else:
            st.error("Số điện thoại chưa có trong hệ thống. Vui lòng đăng ký mới!")

# --- CHỨC NĂNG 2: ĐĂNG KÝ MỚI ---
elif choice == "Đăng Ký Khách Mới":
    st.header("📝 Đăng Ký Thành Viên")
    with st.form("reg_form"):
        new_name = st.text_input("Họ và Tên:")
        new_sdt = st.text_input("Số Điện Thoại:")
        submit = st.form_submit_button("Lưu Thông Tin")
        
        if submit:
            if new_sdt in df["Số Điện Thoại"].values:
                st.warning("Số điện thoại này đã tồn tại!")
            elif new_name and new_sdt:
                new_data = pd.DataFrame([[new_name, new_sdt, 0, datetime.now().strftime("%d/%m/%Y %H:%M")]], 
                                        columns=df.columns)
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success("Đăng ký thành công!")
            else:
                st.error("Vui lòng nhập đủ thông tin.")

# --- CHỨC NĂNG 3: DANH SÁCH & XUẤT EXCEL ---
elif choice == "Danh Sách Khách Hàng":
    st.header("📋 Danh Sách Thành Viên")
    st.dataframe(df, use_container_width=True)
    
    # Xuất Excel
    if not df.empty:
        # Streamlit hỗ trợ xuất trực tiếp ra file Excel/CSV
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tải Danh Sách (File Excel/CSV)",
            data=csv,
            file_name=f'danh_sach_khach_hang_{datetime.now().strftime("%d%m%Y")}.csv',
            mime='text/csv',
        )