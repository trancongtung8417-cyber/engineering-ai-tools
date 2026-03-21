import streamlit as st
from supabase import create_client, Client

# Cấu hình Supabase (Lấy URL và Key trong phần Project Settings)
# url = "YOUR_SUPABASE_URL"
# key = "YOUR_SUPABASE_ANON_KEY"
# supabase: Client = create_client(url, key)

st.set_page_config(page_title="Hilti - Biên Bản Nhận Máy", page_icon="🛠️")

st.title("🛠️ Biên Bản Nhận Máy Hilti")
st.write("Vui lòng nhập đầy đủ thông tin thiết bị bên dưới.")

with st.form("receipt_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        company = st.text_input("Tên đơn vị/Công ty:")
        sender = st.text_input("Người gửi:")
        device = st.text_input("Thiết bị (Model):")
        
    with col2:
        address = st.text_input("Địa chỉ giao nhận:")
        phone = st.text_input("Số điện thoại:")
        serial = st.text_input("Số Seri:")

    status = st.text_area("Tình trạng máy (ví dụ: không hoạt động, không khoan...):")
    
    submitted = st.form_submit_button("Gửi thông tin & Tạo biên bản", type="primary")

if submitted:
    if not company or not phone or not device:
        st.error("Vui lòng điền các thông tin quan trọng (Tên, SĐT, Thiết bị)!")
    else:
        # 1. Lưu dữ liệu vào Supabase
        data = {
            "company_name": company,
            "address": address,
            "sender_name": sender,
            "phone": phone,
            "device_name": device,
            "serial_number": serial,
            "status": status
        }
        
        try:
            response = supabase.table("receipts").insert(data).execute()
            
            # 2. Hiển thị phiếu tổng hợp để khách chụp màn hình
            st.success("✅ Đã gửi thông tin thành công!")
            st.markdown("---")
            st.subheader("PHIẾU XÁC NHẬN NHẬN MÁY")
            
            container = st.container(border=True)
            container.write(f"**Đơn vị:** {company}")
            container.write(f"**Địa chỉ:** {address}")
            container.write(f"**Người gửi:** {sender} - **SĐT:** {phone}")
            container.write(f"**Thiết bị:** {device} - **Seri:** {serial}")
            container.write(f"**Tình trạng:** {status}")
            container.info("Vui lòng chụp màn hình phiếu này gửi qua Zalo.")
            
        except Exception as e:
            st.error(f"Lỗi kết nối database: {e}")

# Phần dành cho Admin xem dữ liệu (Có thể đặt password đơn giản)
if st.checkbox("Xem lịch sử nhận máy (Admin)"):
    pwd = st.text_input("Nhập mật khẩu:", type="password")
    if pwd == "hilti2026":
        res = supabase.table("receipts").select("*").order("created_at", desc=True).execute()
        st.dataframe(res.data)