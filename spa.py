import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import io

# --- KẾT NỐI SUPABASE & CẤU HÌNH ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    # Lấy tài khoản Master ẩn
    MASTER_USER = st.secrets["ADMIN_USER"]
    MASTER_PASS = st.secrets["ADMIN_PASS"]
    # Lấy thông tin liên hệ dành cho khách hàng
    C_LINK = st.secrets["CONTACT_LINK"]
    C_QR = st.secrets["CONTACT_QR_URL"]
except Exception as e:
    st.error("Lỗi cấu hình Secrets! Vui lòng kiểm tra đầy đủ các biến đã hướng dẫn.")
    st.stop()

st.set_page_config(page_title="Spa Manager Pro", layout="wide", page_icon="🌿")

# --- HÀM HỖ TRỢ ---
def format_vn_currency(amount):
    if amount is None: return "0 VND"
    return "{:,.0f}".format(amount).replace(",", ".") + " VND"

def fetch_user(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def update_user_field(username, field, value):
    supabase.table("users").update({field: value}).eq("username", username).execute()

def get_all_users():
    res = supabase.table("users").select("username, role, balance, status, phone, note").execute()
    return pd.DataFrame(res.data)

def get_history(username=None):
    query = supabase.table("history").select("*").order("created_at", desc=True)
    if username: query = query.eq("username", username)
    res = query.execute()
    return pd.DataFrame(res.data)

def add_history(username, amount, action_type, reason):
    supabase.table("history").insert({"username": username, "amount": amount, "action_type": action_type, "reason": reason}).execute()

# --- ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌿 Green Life Spa")
    u_in = st.text_input("Tên đăng nhập")
    p_in = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập", use_container_width=True, type="primary"):
        if u_in == MASTER_USER and p_in == MASTER_PASS:
            st.session_state.logged_in = True
            st.session_state.username = "ADMIN_HE_THONG"
            st.session_state.role = "Owner"
            st.rerun()
        user = fetch_user(u_in)
        if user and user['password'] == p_in:
            if user.get('status', 'Active') == 'Locked': st.error("Tài khoản bị khóa!")
            else:
                st.session_state.logged_in = True
                st.session_state.username = u_in
                st.session_state.role = user['role']
                st.rerun()
        else: st.error("Sai tài khoản hoặc mật khẩu!")
else:
    st.sidebar.header(f"👤 {st.session_state.username}")
    if st.sidebar.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # ==========================================
    # GIAO DIỆN CHỦ SHOP (OWNER) - GIỮ NGUYÊN
    # ==========================================
    if st.session_state.role == "Owner":
        st.title("🍀 Quản Lý Chủ Shop")
        tab1, tab2, tab3 = st.tabs(["👥 Thành viên", "💳 Giao dịch & Thống kê", "📊 Báo cáo tổng"])

        with tab1:
            if st.session_state.username == "ADMIN_HE_THONG":
                st.warning("⚡ CHẾ ĐỘ PHỤC HỒI")
                fix_u = st.text_input("Username khách cần mở khóa")
                if st.button("Mở khóa tức thì"):
                    update_user_field(fix_u, "status", "Active")
                    st.success(f"Đã mở khóa cho {fix_u}")

            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Tạo tài khoản mới")
                with st.form("new_user", clear_on_submit=True):
                    nu = st.text_input("Tên đăng nhập (Username) *")
                    np = st.text_input("Mật khẩu *")
                    n_phone = st.text_input("Số điện thoại")
                    n_note = st.text_area("Ghi chú khách hàng")
                    nr = st.selectbox("Vai trò", ["Customer", "Owner"])
                    if st.form_submit_button("Tạo ngay", use_container_width=True):
                        if not nu or not np: st.error("Vui lòng nhập Tên và Mật khẩu!")
                        elif fetch_user(nu): st.error("Tên này đã tồn tại!")
                        else:
                            supabase.table("users").insert({
                                "username": nu, "password": np, "role": nr, 
                                "balance": 0, "status": "Active",
                                "phone": n_phone, "note": n_note
                            }).execute()
                            st.rerun()
            with c2:
                all_u = get_all_users()
                disp_u = all_u.copy()
                disp_u['balance'] = disp_u['balance'].apply(format_vn_currency)
                st.dataframe(disp_u[['username', 'phone', 'balance', 'status', 'note']], use_container_width=True)
                t_lock = st.selectbox("Chọn tài khoản để Khóa/Mở", all_u['username'])
                col_l, col_r = st.columns(2)
                if col_l.button("🔒 Khóa", use_container_width=True):
                    update_user_field(t_lock, "status", "Locked"); st.rerun()
                if col_r.button("🔓 Mở khóa", use_container_width=True):
                    update_user_field(t_lock, "status", "Active"); st.rerun()

        with tab2:
            st.subheader("Thực hiện Giao dịch")
            custs = all_u[all_u['role'] == 'Customer']
            if not custs.empty:
                m_target = st.selectbox("Chọn khách", custs['username'])
                u_detail = fetch_user(m_target)
                st.write(f"📞 **SĐT:** {u_detail.get('phone', 'Chưa có')} | 📝 **Ghi chú:** {u_detail.get('note', 'Trống')}")
                history_target = get_history(m_target)
                total_in = history_target[history_target['action_type'] == 'Nạp tiền']['amount'].sum() if not history_target.empty else 0
                total_out = history_target[history_target['action_type'] == 'Trừ tiền']['amount'].sum() if not history_target.empty else 0
                current_bal = u_detail['balance']
                sk1, sk2, sk3 = st.columns(3)
                sk1.metric("Tổng nạp", format_vn_currency(total_in))
                sk2.metric("Tổng đã dùng", format_vn_currency(total_out))
                sk3.metric("Số dư hiện tại", format_vn_currency(current_bal))
                st.divider()
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_amt = st.number_input("Số tiền (VND)", min_value=0, step=10000, format="%d")
                    st.info(f"💰 Đang nhập: **{format_vn_currency(m_amt)}**")
                with col_m2:
                    m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                    m_reason = st.text_input("Nội dung dịch vụ")
                if st.button("Xác nhận Giao dịch", use_container_width=True, type="primary"):
                    if not m_reason: st.warning("Vui lòng nhập nội dung!")
                    elif m_amt <= 0: st.warning("Vui lòng nhập số tiền!")
                    else:
                        new_bal = current_bal + m_amt if m_act == "Nạp tiền" else current_bal - m_amt
                        update_user_field(m_target, "balance", new_bal)
                        add_history(m_target, m_amt, m_act, m_reason)
                        st.success(f"Đã cập nhật cho {m_target}!")
                        st.rerun()

        with tab3:
            st.subheader("Báo cáo tổng hợp")
            df_h = get_history()
            if not df_h.empty:
                st.write(f"📈 **Tổng nạp:** {format_vn_currency(df_h[df_h['action_type'] == 'Nạp tiền']['amount'].sum())} | 📉 **Tổng tiêu:** {format_vn_currency(df_h[df_h['action_type'] == 'Trừ tiền']['amount'].sum())}")
                df_h['created_at'] = pd.to_datetime(df_h['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                st.dataframe(df_h[['created_at', 'username', 'action_type', 'amount', 'reason']], use_container_width=True)

    # ==========================================
    # GIAO DIỆN KHÁCH HÀNG (CUSTOMER) - MỚI
    # ==========================================
    else:
        st.title(f"🌿 Xin chào, khách hàng {st.session_state.username}")
        # Lấy dữ liệu mới nhất
        u_info = fetch_user(st.session_state.username)
        
        if u_info:
            balance = u_info['balance']
            # Hiển thị số dư nổi bật
            st.metric("SỐ DƯ TÀI KHOẢN HIỆN TẠI", format_vn_currency(balance))
            
            # --- PHẦN CẢNH BÁO SỐ DƯ THẤP (< 100.000 VND) ---
            if balance < 100000:
                st.divider()
                # Tạo khung cảnh báo màu vàng
                with st.warning("⚠️ **THÔNG BÁO: Số dư tài khoản của quý khách hiện đang dưới 100.000 VND.**"):
                    st.write("Để tránh gián đoạn dịch vụ, vui lòng thực hiện nạp thêm tiền theo thông tin dưới đây:")
                    
                    # # Chia 2 cột để hiện Link và QR
                    # col_info1, col_info2 = st.columns([2, 1])
                    
                #     with col_info1:
                #         st.write("🔗 **Đường link nạp tiền:**")
                #         # Hiện link có thể nhấn được
                #         st.markdown(f"[{C_LINK}]({C_LINK})")
                #         st.caption("(Nhấn vào link để mở trang nạp tiền/liên hệ)")
                        
                #     with col_info2:
                #         st.write("📲 **Mã QR nạp tiền:**")
                #         # Hiện ảnh QR (Sử dụng use_container_width=True để ảnh vừa khung)
                #         if C_QR and C_QR.strip():
                #             st.image(C_QR, caption="Quét mã để nạp tiền", use_container_width=True)
                #         else:
                #             st.caption("(Chưa cấu hình mã QR)")
                # st.divider()
            
            # --- LỊCH SỬ DỊCH VỤ CỦA KHÁCH ---
            st.subheader("📜 Nhật ký sử dụng dịch vụ")
            df_p = get_history(st.session_state.username)
            if not df_p.empty:
                df_p['created_at'] = pd.to_datetime(df_p['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                df_p['amount'] = df_p['amount'].apply(format_vn_currency)
                st.table(df_p[['created_at', 'action_type', 'amount', 'reason']])
            else:
                st.info("Bạn chưa có lịch sử giao dịch nào.")