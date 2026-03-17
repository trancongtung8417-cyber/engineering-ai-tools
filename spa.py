import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import io

# --- KẾT NỐI SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Chưa cấu hình Secrets trên Streamlit Cloud!")
    st.stop()

st.set_page_config(page_title="Spa & Massage Manager", layout="wide", page_icon="🌿")

# --- HÀM HỖ TRỢ DỮ LIỆU ---
def fetch_user(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def get_history(username=None):
    query = supabase.table("history").select("*").order("created_at", desc=True)
    if username:
        query = query.eq("username", username)
    res = query.execute()
    return pd.DataFrame(res.data)

def add_history(username, amount, action_type):
    supabase.table("history").insert({
        "username": username,
        "amount": amount,
        "action_type": action_type
    }).execute()

# --- HÀM XUẤT EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    # Sử dụng XlsxWriter làm engine để định dạng file
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='LichSuGiaoDich')
    return output.getvalue()

# --- GIAO DIỆN ĐĂNG NHẬP (Giữ nguyên như cũ) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Hệ Thống Spa & Massage Trị Liệu")
    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
    with tab1:
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            user_data = fetch_user(u)
            if user_data and user_data['password'] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.role = user_data['role']
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu")
    with tab2:
        new_u = st.text_input("Tên tài khoản mới")
        new_p = st.text_input("Mật khẩu mới", type="password")
        if st.button("Đăng ký ngay"):
            if fetch_user(new_u): st.error("Tên đã tồn tại")
            else:
                supabase.table("users").insert({"username": new_u, "password": new_p, "role": "Customer", "balance": 0}).execute()
                st.success("Đăng ký thành công!")

# --- GIAO DIỆN SAU ĐĂNG NHẬP ---
else:
    st.sidebar.header(f"👤 {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.role == "Owner":
        st.title("Bảng Quản Lý Chủ Shop")
        
        # 1. Quản lý số dư (Giữ nguyên tính năng cũ)
        res_c = supabase.table("users").select("username, balance").eq("role", "Customer").execute()
        df_c = pd.DataFrame(res_c.data)
        
        st.subheader("📋 Danh sách khách hàng")
        st.dataframe(df_c, use_container_width=True)

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            target = st.selectbox("Chọn khách hàng", df_c['username'] if not df_c.empty else [])
        with col2:
            amt = st.number_input("Số tiền (VND)", step=10000)
        with col3:
            act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])

        if st.button("Xác nhận & Ghi lịch sử"):
            user_now = fetch_user(target)
            new_bal = user_now['balance'] + amt if act == "Nạp tiền" else user_now['balance'] - amt
            supabase.table("users").update({"balance": new_bal}).eq("username", target).execute()
            add_history(target, amt, act)
            st.success(f"Đã cập nhật số dư cho {target}!")
            st.rerun()

        st.divider()

        # 2. Lịch sử và Xuất báo cáo
        st.subheader("📜 Lịch sử giao dịch & Báo cáo")
        df_history = get_history()
        
        if not df_history.empty:
            # Chuyển múi giờ về VN cho dễ nhìn
            df_history['created_at'] = pd.to_datetime(df_history['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
            
            # Nút tải file Excel
            excel_data = to_excel(df_history)
            st.download_button(
                label="📥 Tải báo cáo Excel (Tất cả lịch sử)",
                data=excel_data,
                file_name=f"bao_cao_spa_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.dataframe(df_history, use_container_width=True)
        else:
            st.write("Chưa có lịch sử giao dịch.")

    else:
        # --- GIAO DIỆN KHÁCH HÀNG (Giữ nguyên) ---
        st.title("🍀 Tài khoản Thành Viên")
        info = fetch_user(st.session_state.username)
        st.metric("SỐ DƯ CỦA BẠN", f"{info['balance']:,.0f} VND")
        
        st.subheader("📜 Lịch sử của bạn")
        df_his = get_history(st.session_state.username)
        if not df_his.empty:
            df_his['created_at'] = pd.to_datetime(df_his['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
            st.table(df_his[['created_at', 'action_type', 'amount']])
        else:
            st.write("Bạn chưa có giao dịch nào.")