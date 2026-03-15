import streamlit as st
from groq import Groq
import pandas as pd
import os

# 1. Cấu hình giao diện (Mobile Friendly)
st.set_page_config(page_title="Tiệm Trà AI", page_icon="🍹", layout="centered")

# CSS tùy chỉnh để làm đẹp giao diện
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 15px; }
    .status-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "danh_sach_khach.csv"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Tên", "Số điện thoại", "Số điểm", "Ghi chú"])
    df.to_csv(DATA_FILE, index=False)

# 2. Header
st.title("🍹 Tiệm Trà AI")
st.caption("Giải pháp quản lý thông minh của Trần Công Tùng")

# 3. Chia Tab
tab1, tab2, tab3 = st.tabs(["✨ Marketing", "💳 Tích Điểm", "👥 Khách Hàng"])

# --- TAB 1: MARKETING (Tạo nội dung nhanh) ---
with tab1:
    st.subheader("📢 Sáng tạo bài đăng")
    mon_an = st.text_input("Món mới/Ưu đãi hôm nay:", placeholder="Trà Đào Cam Sả...")
    if st.button("🪄 Tạo Content & Concept Ảnh"):
        if st.sidebar.get("api_key"): # Giả định anh để Key trong Sidebar
            # (Phần xử lý Groq giữ nguyên như cũ)
            st.success("Đã tạo xong! Xem bên dưới 👇")
        else: st.warning("Vui lòng nhập API Key ở Sidebar!")

# --- TAB 2: TÍCH ĐIỂM (Dành cho nhân viên thao tác nhanh) ---
with tab2:
    st.subheader("💳 Thẻ Thành Viên")
    sdt_input = st.text_input("🔍 Nhập Số điện thoại khách:", placeholder="090...")
    
    if sdt_input:
        df_all = pd.read_csv(DATA_FILE)
        df_all['Số điện thoại'] = df_all['Số điện thoại'].astype(str)
        khach = df_all[df_all['Số điện thoại'] == sdt_input]
        
        if not khach.empty:
            ki = khach.iloc[0]
            # Hiển thị dạng thẻ (Card)
            st.markdown(f"""
            <div class="status-card">
                <h3>Chào, {ki['Tên']}! 👋</h3>
                <p>Món hay dùng: {ki.get('Ghi chú', 'Chưa có')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Hiển thị số điểm bằng Widget Metric
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Điểm tích lũy", f"{int(ki['Số điểm'])} 🌟")
            col_m2.metric("Còn thiếu", f"{max(0, 5 - int(ki['Số điểm']))} ly")
            
            # Thanh tiến trình (Progress Bar)
            progress = min(int(ki['Số điểm']) / 5, 1.0)
            st.progress(progress)
            
            # Nút thao tác
            c1, c2 = st.columns(2)
            if c1.button("➕ Tặng 1 Điểm"):
                df_all.loc[df_all['Số điện thoại'] == sdt_input, 'Số điểm'] += 1
                df_all.to_csv(DATA_FILE, index=False)
                st.rerun()
            
            if ki['Số điểm'] >= 5:
                st.balloons()
                if c2.button("🎁 Đổi Ly Miễn Phí"):
                    df_all.loc[df_all['Số điện thoại'] == sdt_input, 'Số điểm'] -= 5
                    df_all.to_csv(DATA_FILE, index=False)
                    st.rerun()
        else:
            st.warning("Khách mới! Qua Tab 'Khách Hàng' để thêm nhé.")

# --- TAB 3: QUẢN LÝ ---
with tab3:
    st.subheader("👥 Danh sách thành viên")
    df_view = pd.read_csv(DATA_FILE)
    st.dataframe(df_view, use_container_width=True)
    # Thêm form đăng ký khách mới ở đây (như bản code trước)

# Thêm Tab 4 vào danh sách tabs
tab1, tab2, tab3, tab4 = st.tabs(["✨ Marketing", "💳 Tích Điểm", "👥 Khách Hàng", "📊 Báo Cáo"])

with tab4:
    st.subheader("📈 Hiệu quả kinh doanh")
    df_report = pd.read_csv(DATA_FILE)
    
    if not df_report.empty:
        col_r1, col_r2 = st.columns(2)
        
        # 1. Thống kê tổng quan
        total_customers = len(df_report)
        total_points = df_report['Số điểm'].sum()
        
        col_r1.metric("Tổng số khách", f"{total_customers} người")
        col_r2.metric("Tổng điểm đã tích", f"{int(total_points)} 🌟")
        
        # 2. Biểu đồ món uống được yêu thích nhất
        st.write("---")
        st.subheader("🍹 Top món uống khách yêu thích")
        # Đếm số lượng món uống trong cột 'Món hay uống'
        top_drinks = df_report['Món hay uống'].value_counts()
        st.bar_chart(top_drinks)
        
        st.info("💡 Mẹo: Nhìn vào biểu đồ này để biết nên nhập thêm nguyên liệu cho món nào anh nhé!")
    else:
        st.write("Chưa có dữ liệu để phân tích. Anh hãy thêm khách hàng trước nhé!")    