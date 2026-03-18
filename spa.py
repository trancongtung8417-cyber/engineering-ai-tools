import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import io

# --- KẾT NỐI SUPABASE ---
# Lưu ý: Cấu hình SUPABASE_URL và SUPABASE_KEY trong mục Settings -> Secrets của Streamlit Cloud
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Lỗi: Chưa cấu hình Secrets (URL/Key) trên Streamlit Cloud!")
    st.stop()

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Spa & Massage Manager Pro", layout="wide", page_icon="🌿")

# --- HÀM HỖ TRỢ ĐỊNH DẠNG & DỮ LIỆU ---
def format_vn_currency(amount):
    """Định dạng số thành 1.000.000 VND"""
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

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='BaoCao_Spa')
    return output.getvalue()

# --- KIỂM TRA TRẠNG THÁI ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🌿 Hệ Thống Quản Lý Spa & Massage")
    tab_lg, tab_reg = st.tabs(["Đăng nhập", "Đăng ký khách mới"])
    
    with tab_lg:
        u_input = st.text_input("Tên đăng nhập")
        p_input = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập hệ thống", use_container_width=True):
            user_data = fetch_user(u_input)
            if user_data:
                if user_data['status'] == 'Locked':
                    st.error("Tài khoản này đã bị khóa. Vui lòng liên hệ chủ tiệm.")
                elif user_data['password'] == p_input:
                    st.session_state.logged_in = True
                    st.session_state.username = u_input
                    st.session_state.role = user_data['role']
                    st.rerun()
                else: st.error("Mật khẩu không chính xác.")
            else: st.error("Tài khoản không tồn tại.")
            
    with tab_reg:
        st.info("Khách hàng có thể tự tạo tài khoản thành viên tại đây.")
        reg_u = st.text_input("Tên đăng nhập mới (viết liền không dấu)")
        reg_p = st.text_input("Mật khẩu mới", type="password")
        if st.button("Xác nhận đăng ký"):
            if not reg_u or not reg_p: st.warning("Vui lòng điền đủ thông tin.")
            elif fetch_user(reg_u): st.error("Tên đăng nhập đã tồn tại.")
            else:
                supabase.table("users").insert({"username": reg_u, "password": reg_p, "role": "Customer", "balance": 0, "status": "Active"}).execute()
                st.success("Đăng ký thành công! Mời bạn quay lại tab Đăng nhập.")

# --- GIAO DIỆN SAU KHI ĐĂNG NHẬP ---
else:
    # THANH BÊN (SIDEBAR)
    st.sidebar.header(f"👤 {st.session_state.username}")
    st.sidebar.write(f"Quyền hạn: **{st.session_state.role}**")
    
    with st.sidebar.expander("🔑 Đổi mật khẩu"):
        old_p = st.text_input("Mật khẩu hiện tại", type="password")
        new_p = st.text_input("Mật khẩu mới", type="password")
        if st.button("Cập nhật mật khẩu"):
            curr = fetch_user(st.session_state.username)
            if curr['password'] == old_p:
                update_user_field(st.session_state.username, "password", new_p)
                st.sidebar.success("Đã đổi mật khẩu!")
            else: st.sidebar.error("Mật khẩu cũ sai.")

    if st.sidebar.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # --- NỘI DUNG CHÍNH CHO CHỦ SHOP ---
    if st.session_state.role == "Owner":
        st.title("🍀 Bảng Điều Khiển Chủ Shop")
        t1, t2, t3 = st.tabs(["👥 Quản lý Thành viên", "💳 Giao dịch Tiền", "📊 Báo cáo & Lịch sử"])

        # TAB 1: THÀNH VIÊN
        with t1:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Thêm tài khoản mới")
                with st.form("add_user_form", clear_on_submit=True):
                    au = st.text_input("Tên đăng nhập")
                    ap = st.text_input("Mật khẩu", type="password")
                    ar = st.selectbox("Vai trò", ["Customer", "Staff", "Owner"])
                    if st.form_submit_button("Tạo ngay"):
                        if fetch_user(au): st.error("Đã tồn tại!")
                        else:
                            supabase.table("users").insert({"username": au, "password": ap, "role": ar, "balance": 0, "status": "Active"}).execute()
                            st.success(f"Đã tạo {au}")
                            st.rerun()
            with c2:
                st.subheader("Danh sách tài khoản")
                df_all = get_all_users()
                # Định dạng hiển thị tiền trong bảng
                df_view = df_all.copy()
                df_view['balance'] = df_view['balance'].apply(lambda x: "{:,.0f}".format(x).replace(",", "."))
                st.dataframe(df_view, use_container_width=True)
                
                target_u = st.selectbox("Chọn tài khoản để xử lý trạng thái", df_all['username'])
                col_b1, col_b2 = st.columns(2)
                if col_b1.button("🔒 Khóa tài khoản", use_container_width=True):
                    update_user_field(target_u, "status", "Locked")
                    st.rerun()
                if col_b2.button("🔓 Mở khóa tài khoản", use_container_width=True):
                    update_user_field(target_u, "status", "Active")
                    st.rerun()

        # TAB 2: GIAO DỊCH
        with t2:
            st.subheader("Nạp tiền hoặc Trừ tiền dịch vụ")
            df_cust = df_all[df_all['role'] == 'Customer']
            if not df_cust.empty:
                with st.form("money_form", clear_on_submit=True):
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        m_target = st.selectbox("Chọn khách hàng", df_cust['username'])
                        m_amt = st.number_input("Số tiền (VND)", min_value=0, step=10000, format="%d")
                        st.caption(f"Kiểm tra số tiền: **{format_vn_currency(m_amt)}**")
                    with col_m2:
                        m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                        m_reason = st.text_input("Nội dung (VD: Massage đá nóng, Nạp thẻ...)")
                    
                    if st.form_submit_button("Xác nhận Giao dịch", use_container_width=True):
                        if not m_reason: st.warning("Vui lòng nhập lý do/nội dung.")
                        else:
                            u_now = fetch_user(m_target)
                            new_b = u_now['balance'] + m_amt if m_act == "Nạp tiền" else u_now['balance'] - m_amt
                            update_user_field(m_target, "balance", new_b)
                            add_history(m_target, m_amt, m_act, m_reason)
                            st.success(f"Thành công! Số dư mới: {format_vn_currency(new_b)}")
                            st.rerun()
            else: st.write("Chưa có khách hàng nào.")

        # TAB 3: BÁO CÁO
        with t3:
            st.subheader("Lịch sử giao dịch hệ thống")
            df_h = get_history()
            if not df_h.empty:
                df_h['created_at'] = pd.to_datetime(df_h['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                st.download_button("📥 Tải báo cáo Excel", to_excel(df_h), f"spa_report_{datetime.now().strftime('%d%m%Y')}.xlsx")
                # Định dạng tiền trong lịch sử
                df_h_view = df_h.copy()
                df_h_view['amount'] = df_h_view['amount'].apply(lambda x: "{:,.0f}".format(x).replace(",", "."))
                st.dataframe(df_h_view[['created_at', 'username', 'action_type', 'amount', 'reason']], use_container_width=True)

    # --- NỘI DUNG CHO KHÁCH HÀNG ---
    else:
        st.title(f"Xin chào, {st.session_state.username}")
        user_info = fetch_user(st.session_state.username)
        st.metric("SỐ DƯ TÀI KHOẢN HIỆN TẠI", format_vn_currency(user_info['balance']))
        
        st.divider()
        st.subheader("📜 Nhật ký sử dụng dịch vụ")
        df_p = get_history(st.session_state.username)
        if not df_p.empty:
            df_p['created_at'] = pd.to_datetime(df_p['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
            df_p['amount'] = df_p['amount'].apply(lambda x: "{:,.0f}".format(x).replace(",", "."))
            st.table(df_p[['created_at', 'action_type', 'amount', 'reason']])
        else:
            st.write("Bạn chưa có lịch sử giao dịch nào.")