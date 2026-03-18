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
    st.error("Lỗi cấu hình Secrets! Kiểm tra SUPABASE_URL và SUPABASE_KEY.")
    st.stop()

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Spa & Massage Manager", layout="wide", page_icon="🌿")

# --- HÀM HỖ TRỢ ---
def format_vn_currency(amount):
    """Định dạng số thành 1.000.000 VND"""
    if amount is None: return "0 VND"
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
        "username": username, "amount": amount, 
        "action_type": action_type, "reason": reason
    }).execute()

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='BaoCao_Spa')
    return output.getvalue()

# --- KIỂM TRA ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🌿 Hệ Thống Quản Lý Spa & Massage Trị Liệu")
    t_login, t_register = st.tabs(["Đăng nhập", "Đăng ký"])
    
    with t_login:
        u_in = st.text_input("Tên đăng nhập")
        p_in = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập hệ thống", use_container_width=True):
            user = fetch_user(u_in)
            if user and user['password'] == p_in:
                if user.get('status', 'Active') == 'Locked':
                    st.error("Tài khoản này đã bị khóa!")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = u_in
                    st.session_state.role = user['role']
                    st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu")
            
    with t_register:
        st.info("Dành cho khách hàng tự tạo tài khoản")
        reg_u = st.text_input("Tên tài khoản mới")
        reg_p = st.text_input("Mật khẩu mới", type="password")
        if st.button("Xác nhận đăng ký"):
            if fetch_user(reg_u): st.error("Tên này đã tồn tại")
            else:
                supabase.table("users").insert({"username": reg_u, "password": reg_p, "role": "Customer", "balance": 0, "status": "Active"}).execute()
                st.success("Đăng ký xong! Mời bạn qua tab Đăng nhập.")

# --- GIAO DIỆN SAU ĐĂNG NHẬP ---
else:
    st.sidebar.header(f"👤 {st.session_state.username}")
    st.sidebar.info(f"Quyền hạn: {st.session_state.role}")
    
    # Đổi mật khẩu trong Sidebar
    with st.sidebar.expander("🔑 Đổi mật khẩu"):
        old_pwd = st.text_input("Mật khẩu cũ", type="password")
        new_pwd = st.text_input("Mật khẩu mới", type="password")
        if st.button("Cập nhật"):
            u_data = fetch_user(st.session_state.username)
            if u_data['password'] == old_pwd:
                update_user_field(st.session_state.username, "password", new_pwd)
                st.sidebar.success("Đã đổi xong!")
            else: st.sidebar.error("Mật khẩu cũ sai")

    if st.sidebar.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- NỘI DUNG CHỦ SHOP (OWNER) ---
    if st.session_state.role == "Owner":
        st.title("🍀 Quản Lý Chủ Shop")
        tab1, tab2, tab3 = st.tabs(["👥 Thành viên", "💳 Giao dịch", "📊 Báo cáo"])

        with tab1:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Thêm tài khoản")
                with st.form("new_user", clear_on_submit=True):
                    nu = st.text_input("Username")
                    np = st.text_input("Password", type="password")
                    nr = st.selectbox("Vai trò", ["Customer", "Staff", "Owner"])
                    if st.form_submit_button("Tạo ngay"):
                        if fetch_user(nu): st.error("Đã tồn tại!")
                        else:
                            supabase.table("users").insert({"username": nu, "password": np, "role": nr, "balance": 0, "status": "Active"}).execute()
                            st.rerun()
            with c2:
                st.subheader("Danh sách")
                all_u = get_all_users()
                disp_u = all_u.copy()
                disp_u['balance'] = disp_u['balance'].apply(format_vn_currency)
                st.dataframe(disp_u, use_container_width=True)
                
                t_lock = st.selectbox("Chọn tài khoản để Khóa/Mở", all_u['username'])
                col_l, col_r = st.columns(2)
                if col_l.button("🔒 Khóa tài khoản", use_container_width=True):
                    update_user_field(t_lock, "status", "Locked")
                    st.rerun()
                if col_r.button("🔓 Mở khóa", use_container_width=True):
                    update_user_field(t_lock, "status", "Active")
                    st.rerun()

        with tab2:
            st.subheader("Nạp / Trừ tiền dịch vụ")
            cust_list = all_u[all_u['role'] == 'Customer']
            if not cust_list.empty:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_target = st.selectbox("Chọn khách hàng", cust_list['username'])
                    # Không để trong form để nhảy số tiền ngay lập tức
                    m_amt = st.number_input("Số tiền (VND)", min_value=0, step=10000, format="%d")
                    st.info(f"💰 Số tiền đang nhập: **{format_vn_currency(m_amt)}**")
                with col_m2:
                    m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                    m_reason = st.text_input("Nội dung (VD: Massage đá nóng, Nạp thẻ...)")
                
                if st.button("Xác nhận Giao dịch", use_container_width=True, type="primary"):
                    if not m_reason: st.warning("Vui lòng nhập nội dung!")
                    else:
                        u_now = fetch_user(m_target)
                        new_bal = u_now['balance'] + m_amt if m_act == "Nạp tiền" else u_now['balance'] - m_amt
                        update_user_field(m_target, "balance", new_bal)
                        add_history(m_target, m_amt, m_act, m_reason)
                        st.success(f"Thành công! Số dư mới: {format_vn_currency(new_bal)}")
                        st.rerun()

        with tab3:
            st.subheader("Lịch sử tổng hợp")
            df_h = get_history()
            if not df_h.empty:
                df_h['created_at'] = pd.to_datetime(df_h['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                st.download_button("📥 Tải Excel", to_excel(df_h), "bao_cao_spa.xlsx")
                df_h_disp = df_h.copy()
                df_h_disp['amount'] = df_h_disp['amount'].apply(format_vn_currency)
                st.dataframe(df_h_disp[['created_at', 'username', 'action_type', 'amount', 'reason']], use_container_width=True)

    # --- NỘI DUNG KHÁCH HÀNG ---
    else:
        st.title(f"🌿 Xin chào, {st.session_state.username}")
        u_info = fetch_user(st.session_state.username)
        if u_info:
            st.metric("SỐ DƯ TÀI KHOẢN", format_vn_currency(u_info['balance']))
            st.divider()
            st.subheader("📜 Nhật ký dịch vụ")
            df_p = get_history(st.session_state.username)
            if not df_p.empty:
                df_p['created_at'] = pd.to_datetime(df_p['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                df_p['amount'] = df_p['amount'].apply(format_vn_currency)
                st.table(df_p[['created_at', 'action_type', 'amount', 'reason']])
            else: st.info("Bạn chưa có giao dịch nào.")