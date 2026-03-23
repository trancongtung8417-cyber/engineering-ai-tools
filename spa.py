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
    
    # Tài khoản quản trị
    MASTER_USER = st.secrets["ADMIN_USER"]
    MASTER_PASS = st.secrets["ADMIN_PASS"]
    
    # Thông tin liên hệ và hình ảnh (Lấy từ Secrets anh vừa cập nhật)
    C_LINK = st.secrets.get("CONTACT_LINK", "")
    C_QR = st.secrets.get("CONTACT_QR_URL", "")
    SPA_LOGO = st.secrets.get("SPA_LOGO_URL", "") # Dòng này để đọc Logo mới
    
except Exception as e:
    st.error("Lỗi cấu hình Secrets! Vui lòng kiểm tra lại các biến trong Settings.")
    st.stop()

# Cấu hình biểu tượng trên Tab trình duyệt (Favicon)
st.set_page_config(
    page_title="Spa Manager Pro", 
    layout="wide", 
    page_icon=SPA_LOGO if SPA_LOGO else "🌿"
)

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
    res = supabase.table("users").select("*").execute()
    return pd.DataFrame(res.data)

def get_history(username=None):
    query = supabase.table("history").select("*").order("created_at", desc=True)
    if username: query = query.eq("username", username)
    res = query.execute()
    return pd.DataFrame(res.data)

def add_history(username, amount, action_type, reason):
    supabase.table("history").insert({
        "username": username, 
        "amount": amount, 
        "action_type": action_type, 
        "reason": reason
    }).execute()

# --- ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Hiển thị Logo tại màn hình đăng nhập
    if SPA_LOGO:
        st.image(SPA_LOGO, width=150)
    st.title("🌿 Hệ Thống Quản Lý Spa")
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
    # GIAO DIỆN CHỦ SHOP (OWNER)
    # ==========================================
    if st.session_state.role == "Owner":
        # HIỂN THỊ LOGO VÀ TIÊU ĐỀ
        col_l, col_t = st.columns([1, 6])
        with col_l:
            if SPA_LOGO: st.image(SPA_LOGO, width=80)
        with col_t:
            st.title("Quản Lý Hệ Thống Spa")

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
                col_lock1, col_lock2 = st.columns(2)
                if col_lock1.button("🔒 Khóa", use_container_width=True):
                    update_user_field(t_lock, "status", "Locked"); st.rerun()
                if col_lock2.button("🔓 Mở khóa", use_container_width=True):
                    update_user_field(t_lock, "status", "Active"); st.rerun()

        with tab2:
            st.subheader("Thực hiện Giao dịch & Chi tiết khách")
            custs = all_u[all_u['role'] == 'Customer']
            if not custs.empty:
                m_target = st.selectbox("Chọn khách hàng", custs['username'])
                u_detail = fetch_user(m_target)
                history_target = get_history(m_target)
                
                try:
                    created_dt = pd.to_datetime(u_detail['created_at']).tz_convert('Asia/Ho_Chi_Minh').strftime('%d/%m/%Y')
                except:
                    created_dt = "Chưa rõ"
                
                st.write(f"📞 **SĐT:** {u_detail.get('phone', 'Trống')} | 📝 **Ghi chú:** {u_detail.get('note', 'Trống')} | 📅 **Ngày tham gia:** {created_dt}")
                
                total_in = history_target[history_target['action_type'] == 'Nạp tiền']['amount'].sum() if not history_target.empty else 0
                total_out = history_target[history_target['action_type'] == 'Trừ tiền']['amount'].sum() if not history_target.empty else 0
                current_bal = float(u_detail['balance'])
                
                sk1, sk2, sk3 = st.columns(3)
                sk1.metric("Tổng nạp", format_vn_currency(total_in))
                sk2.metric("Tổng đã dùng", format_vn_currency(total_out))
                sk3.metric("Số dư hiện tại", format_vn_currency(current_bal))
                
                with st.expander(f"📜 Xem lịch sử giao dịch của {m_target}"):
                    if not history_target.empty:
                        df_mini = history_target.copy()
                        df_mini['Thời gian'] = pd.to_datetime(df_mini['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                        df_mini['Số tiền'] = df_mini['amount'].apply(format_vn_currency)
                        st.dataframe(df_mini[['Thời gian', 'action_type', 'Số tiền', 'reason']], use_container_width=True, hide_index=True)

                st.divider()
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_amt = st.number_input("Số tiền (VND)", min_value=0, step=10000, format="%d")
                with col_m2:
                    m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                    m_reason = st.text_input("Nội dung dịch vụ")
                
                if st.button("Xác nhận Giao dịch", use_container_width=True, type="primary"):
                    if not m_reason: st.warning("Vui lòng nhập nội dung!")
                    elif m_amt <= 0: st.warning("Số tiền không hợp lệ!")
                    else:
                        final_amt = m_amt
                        bonus_text = ""
                        if m_act == "Nạp tiền":
                            
                            # if m_amt >= 5000000:
                            #     bonus = m_amt * 0.1
                            #     final_amt = m_amt + bonus
                            #     bonus_text = f" (Tặng 10%: {format_vn_currency(bonus)})"
                            # elif m_amt >= 2000000:
                            #     bonus = m_amt * 0.05
                            #     final_amt = m_amt + bonus
                            #     bonus_text = f" (Tặng 5%: {format_vn_currency(bonus)})"
                        
                        new_bal = current_bal + final_amt if m_act == "Nạp tiền" else current_bal - m_amt
                        update_user_field(m_target, "balance", new_bal)
                        add_history(m_target, final_amt if m_act == "Nạp tiền" else m_amt, m_act, f"{m_reason}{bonus_text}")
                        st.success("Thành công!"); st.balloons() if bonus_text else None; st.rerun()

        with tab3:
            st.subheader("📊 Báo cáo tổng hợp")
            df_all_h = get_history()
            if not df_all_h.empty:
                t_n = df_all_h[df_all_h['action_type'] == 'Nạp tiền']['amount'].sum()
                t_t = df_all_h[df_all_h['action_type'] == 'Trừ tiền']['amount'].sum()
                st.write(f"📈 **Tổng nạp:** {format_vn_currency(t_n)} | 📉 **Tổng tiêu:** {format_vn_currency(t_t)}")
                
                df_c = all_u[all_u['role'] == 'Customer'].copy()
                st.markdown("### Danh sách khách hàng")
                st.dataframe(df_c[['username', 'phone', 'balance', 'note']], use_container_width=True)
                
                csv = df_c.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải báo cáo CSV", data=csv, file_name="bao_cao_spa.csv", mime="text/csv")

    # ==========================================
    # GIAO DIỆN KHÁCH HÀNG (CUSTOMER)
    # ==========================================
    else:
        # Hiển thị Logo cho khách hàng
        if SPA_LOGO: st.image(SPA_LOGO, width=100)
        st.title(f"🌿 Xin chào, {st.session_state.username}")
        
        u_info = fetch_user(st.session_state.username)
        if u_info:
            balance = float(u_info['balance'])
            st.metric("SỐ DƯ TÀI KHOẢN", format_vn_currency(balance))
            st.info("✨ Ưu đãi: Nạp từ 2tr tặng 5% | Nạp từ 5tr tặng 10%")
            
            if balance < 100000:
                with st.warning("⚠️ **Số dư của quý khách hiện dưới 100.000 VND**"):
                    c_c1, c_c2 = st.columns([2, 1])
                    with c_c1:
                        st.write(f"🔗 **Liên hệ nạp tiền:** [Nhấn vào đây]({C_LINK})")
                    with c_c2:
                        if C_QR: st.image(C_QR, caption="QR Nạp tiền", use_container_width=True)

            st.subheader("📜 Nhật ký dịch vụ")
            df_p = get_history(st.session_state.username)
            if not df_p.empty:
                df_p['Thời gian'] = pd.to_datetime(df_p['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                df_p['Số tiền'] = df_p['amount'].apply(format_vn_currency)
                st.table(df_p[['Thời gian', 'action_type', 'Số tiền', 'reason']])