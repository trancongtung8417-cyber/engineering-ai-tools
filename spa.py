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
    st.error("Lỗi cấu hình Secrets! Vui lòng kiểm tra các biến: SUPABASE_URL, SUPABASE_KEY, ADMIN_USER, ADMIN_PASS, CONTACT_LINK, CONTACT_QR_URL.")
    st.stop()

st.set_page_config(page_title="Spa Manager Pro", layout="wide", page_icon="🌿")

# --- HÀM HỖ TRỢ ---
def format_vn_currency(amount):
    if amount is None: return "0 VND"
    return "{:,.0f}".format(amount).replace(",", ".") + " VND"

def fetch_user(username):
    # Lấy toàn bộ thông tin bao gồm cả created_at
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def update_user_field(username, field, value):
    supabase.table("users").update({field: value}).eq("username", username).execute()

def get_all_users():
    res = supabase.table("users").select("username, role, balance, status, phone, note, created_at").execute()
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
    # GIAO DIỆN CHỦ SHOP (OWNER)
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
            st.subheader("Thực hiện Giao dịch & Chi tiết khách")
            custs = all_u[all_u['role'] == 'Customer']
            if not custs.empty:
                m_target = st.selectbox("Chọn khách hàng", custs['username'])
                
                u_detail = fetch_user(m_target)
                history_target = get_history(m_target)
                
                # --- THÔNG TIN CƠ BẢN ---
                try:
                    created_dt = pd.to_datetime(u_detail['created_at']).tz_convert('Asia/Ho_Chi_Minh').strftime('%d/%m/%Y')
                except:
                    created_dt = "N/A"
                
                st.write(f"📞 **SĐT:** {u_detail.get('phone', 'Chưa có')} | 📝 **Ghi chú:** {u_detail.get('note', 'Trống')} | 📅 **Ngày tham gia:** {created_dt}")
                
                # --- CHỈ SỐ TÀI CHÍNH ---
                total_in = history_target[history_target['action_type'] == 'Nạp tiền']['amount'].sum() if not history_target.empty else 0
                total_out = history_target[history_target['action_type'] == 'Trừ tiền']['amount'].sum() if not history_target.empty else 0
                current_bal = float(u_detail['balance'])
                
                sk1, sk2, sk3 = st.columns(3)
                sk1.metric("Tổng nạp", format_vn_currency(total_in))
                sk2.metric("Tổng đã dùng", format_vn_currency(total_out))
                sk3.metric("Số dư hiện tại", format_vn_currency(current_bal))
                
                with st.expander(f"📜 Xem lịch sử giao dịch của {m_target}", expanded=False):
                    if not history_target.empty:
                        df_mini = history_target.copy()
                        df_mini['Thời gian'] = pd.to_datetime(df_mini['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                        df_mini['Số tiền'] = df_mini['amount'].apply(format_vn_currency)
                        st.dataframe(df_mini[['Thời gian', 'action_type', 'Số tiền', 'reason']], use_container_width=True, hide_index=True)
                    else:
                        st.info("Khách hàng này chưa có giao dịch nào.")

                st.divider()

                # --- FORM NHẬP GIAO DỊCH VỚI LOGIC KHUYẾN MÃI ---
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_amt = st.number_input("Số tiền giao dịch (VND)", min_value=0, step=10000, format="%d")
                    st.info(f"💰 Đang nhập: **{format_vn_currency(m_amt)}**")
                with col_m2:
                    m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                    m_reason = st.text_input("Nội dung dịch vụ", placeholder="Ví dụ: Massage body, Nạp thẻ VIP...")
                
                if st.button("Xác nhận Giao dịch", use_container_width=True, type="primary"):
                    if not m_reason: st.warning("Vui lòng nhập nội dung!")
                    elif m_amt <= 0: st.warning("Vui lòng nhập số tiền!")
                    else:
                        final_amt = m_amt
                        bonus_text = ""
                        
                        # --- LOGIC KHUYẾN MÃI NẠP TIỀN ---
                        if m_act == "Nạp tiền":
                            if m_amt >= 5000000:
                                bonus = m_amt * 0.1
                                final_amt = m_amt + bonus
                                bonus_text = f" (Tặng 10%: {format_vn_currency(bonus)})"
                            elif m_amt >= 2000000:
                                bonus = m_amt * 0.05
                                final_amt = m_amt + bonus
                                bonus_text = f" (Tặng 5%: {format_vn_currency(bonus)})"
                        
                        # Tính số dư mới
                        new_bal = current_bal + final_amt if m_act == "Nạp tiền" else current_bal - m_amt
                        display_reason = f"{m_reason}{bonus_text}"
                        
                        update_user_field(m_target, "balance", new_bal)
                        add_history(m_target, final_amt if m_act == "Nạp tiền" else m_amt, m_act, display_reason)
                        
                        st.success(f"Đã cập nhật thành công cho khách {m_target}!")
                        if bonus_text: st.balloons()
                        st.rerun()
            else:
                st.info("Chưa có tài khoản khách hàng nào.")

        with tab3:
            st.subheader("📊 Báo cáo tổng hợp hệ thống")
            df_all_h = get_history()
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            if not df_all_h.empty:
                total_nạp = df_all_h[df_all_h['action_type'] == 'Nạp tiền']['amount'].sum()
                total_tiêu = df_all_h[df_all_h['action_type'] == 'Trừ tiền']['amount'].sum()
                col_stat1.metric("Tổng doanh thu (Nạp)", format_vn_currency(total_nạp))
                col_stat2.metric("Tổng dịch vụ cung cấp", format_vn_currency(total_tiêu), delta_color="inverse")
                col_stat3.metric("Số dư khách còn giữ", format_vn_currency(total_nạp - total_tiêu))
            
            st.divider()
            st.markdown("### 👥 Danh sách chi tiết khách hàng")
            df_customers = all_u[all_u['role'] == 'Customer'].copy()
            if not df_customers.empty:
                df_report = df_customers.rename(columns={'username':'Tên khách', 'phone':'SĐT', 'balance':'Số dư', 'status':'Trạng thái', 'note':'Ghi chú'})
                df_report_display = df_report.copy()
                df_report_display['Số dư'] = df_report_display['Số dư'].apply(format_vn_currency)
                st.dataframe(df_report_display[['Tên khách', 'SĐT', 'Số dư', 'Trạng thái', 'Ghi chú']], use_container_width=True, hide_index=True)
                
                csv = df_report.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 Tải về báo cáo khách hàng (CSV)", data=csv, file_name=f"bao_cao_spa_{datetime.now().strftime('%d_%m_%Y')}.csv", mime="text/csv", use_container_width=True)
            
            st.divider()
            st.markdown("### 📜 Toàn bộ lịch sử giao dịch")
            if not df_all_h.empty:
                df_all_h['Thời gian'] = pd.to_datetime(df_all_h['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                df_all_h_disp = df_all_h.copy()
                df_all_h_disp['Số tiền'] = df_all_h_disp['amount'].apply(format_vn_currency)
                st.dataframe(df_all_h_disp[['Thời gian', 'username', 'action_type', 'Số tiền', 'reason']].rename(columns={'username':'Khách','action_type':'Loại'}), use_container_width=True, hide_index=True)

    # ==========================================
    # GIAO DIỆN KHÁCH HÀNG (CUSTOMER)
    # ==========================================
    else:
        st.title(f"🌿 Xin chào, khách hàng {st.session_state.username}")
        u_info = fetch_user(st.session_state.username)
        
        if u_info:
            balance = float(u_info['balance'])
            st.metric("SỐ DƯ TÀI KHOẢN HIỆN TẠI", format_vn_currency(balance))
            
            # Khuyến mãi hiện có để khách biết
            st.info("✨ Chương trình ưu đãi: Nạp từ 2tr tặng 5% | Nạp từ 5tr tặng 10%")
            
            if balance < 100000:
                st.warning(f"⚠️ **Số dư tài khoản của quý khách hiện dưới 100.000 VND.**")
                with st.container(border=True):
                    st.write("Vui lòng nạp thêm tiền để tiếp tục sử dụng dịch vụ:")
                    col_info1, col_info2 = st.columns([2, 1])
                    with col_info1:
                        st.write(f"🔗 **Link nạp tiền:** [Nhấn vào đây]({C_LINK})")
                    with col_info2:
                        if C_QR: st.image(C_QR, caption="Quét mã nạp tiền", use_container_width=True)
                st.divider()
            
            st.subheader("📜 Nhật ký sử dụng dịch vụ")
            df_p = get_history(st.session_state.username)
            if not df_p.empty:
                df_p['Thời gian'] = pd.to_datetime(df_p['created_at']).dt.tz_convert('Asia/Ho_Chi_Minh').dt.strftime('%d/%m/%Y %H:%M')
                df_p['Số tiền'] = df_p['amount'].apply(format_vn_currency)
                st.table(df_p[['Thời gian', 'action_type', 'Số tiền', 'reason']])