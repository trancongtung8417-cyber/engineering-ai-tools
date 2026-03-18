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
    st.error("Lỗi cấu hình Secrets!")
    st.stop()

st.set_page_config(page_title="Spa Manager Pro", layout="wide", page_icon="🌿")

def format_vn_currency(amount):
    return "{:,.0f}".format(amount).replace(",", ".") + " VND"

def fetch_user(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def get_all_users():
    res = supabase.table("users").select("username, role, balance, status").execute()
    return pd.DataFrame(res.data)

def update_user_field(username, field, value):
    supabase.table("users").update({field: value}).eq("username", username).execute()

def get_history(username=None):
    query = supabase.table("history").select("*").order("created_at", desc=True)
    if username:
        query = query.eq("username", username)
    res = query.execute()
    return pd.DataFrame(res.data)

def add_history(username, amount, action_type, reason):
    supabase.table("history").insert({
        "username": username, "amount": amount, "action_type": action_type, "reason": reason
    }).execute()

# --- ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Hệ Thống Spa & Massage")
    u_input = st.text_input("Tên đăng nhập")
    p_input = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        user_data = fetch_user(u_input)
        if user_data and user_data['password'] == p_input:
            if user_data.get('status', 'Active') == 'Locked': st.error("Tài khoản bị khóa!")
            else:
                st.session_state.logged_in = True
                st.session_state.username = u_input
                st.session_state.role = user_data['role']
                st.rerun()
        else: st.error("Sai thông tin đăng nhập")

else:
    st.sidebar.header(f"👤 {st.session_state.username}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.role == "Owner":
        st.title("Bảng Quản Lý Chủ Shop")
        t1, t2, t3 = st.tabs(["👥 Thành viên", "💳 Giao dịch", "📊 Báo cáo"])

        with t1:
            df_all = get_all_users()
            st.dataframe(df_all, use_container_width=True)

        with t2:
            st.subheader("Nạp tiền hoặc Trừ tiền dịch vụ")
            df_cust = df_all[df_all['role'] == 'Customer']
            
            if not df_cust.empty:
                # Đưa các ô nhập liệu ra ngoài Form để cập nhật tức thì
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_target = st.selectbox("Chọn khách hàng", df_cust['username'])
                    m_amt = st.number_input("Số tiền (VND)", min_value=0, step=10000, format="%d")
                    
                    # Dòng này bây giờ sẽ nhảy số ngay khi anh gõ/thay đổi
                    st.info(f"💰 Số tiền đang nhập: **{format_vn_currency(m_amt)}**")
                            
                with col_m2:
                    m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                    m_reason = st.text_input("Nội dung (VD: Massage đá nóng, Nạp thẻ...)")
                
                # Nút xác nhận riêng biệt
                if st.button("Xác nhận Giao dịch", use_container_width=True, type="primary"):
                    if not m_reason: 
                        st.warning("Vui lòng nhập lý do/nội dung.")
                    elif m_amt <= 0:
                        st.warning("Vui lòng nhập số tiền lớn hơn 0.")
                    else:
                        u_now = fetch_user(m_target)
                        new_b = u_now['balance'] + m_amt if m_act == "Nạp tiền" else u_now['balance'] - m_amt
                        update_user_field(m_target, "balance", new_b)
                        add_history(m_target, m_amt, m_act, m_reason)
                        st.success(f"Thành công! Số dư mới: {format_vn_currency(new_b)}")
                        st.rerun()
            else: 
                st.write("Chưa có khách hàng nào.")

        with t3:
            df_h = get_history()
            st.dataframe(df_h, use_container_width=True)
    else:
        st.write("Giao diện khách hàng")