import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import os
from datetime import datetime

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hilti - Biên Bản Nhận Máy", page_icon="🛠️", layout="centered")

# --- 2. KẾT NỐI SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Lỗi Secrets: {e}")
    st.stop()

# --- 3. CSS GIAO DIỆN (MÀU ĐỎ HILTI) ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #DD2222 !important;
        color: white !important;
        border-radius: 5px;
    }
    .receipt-container {
        border: 3px solid #DD2222;
        padding: 25px;
        border-radius: 15px;
        background-color: white;
    }
    h1, h2, h3 { color: #DD2222; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HÀM TẠO PDF ---
def generate_pdf(data, timestamp):
    pdf = FPDF()
    pdf.add_page()
    
    # Khai báo đường dẫn font
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Roboto', '', font_path, uni=True)
        pdf.set_font('Roboto', '', 12)
    else:
        pdf.set_font('Arial', '', 12)

    # 1. Chèn Logo
    if os.path.exists("hilti_logo.png"):
        pdf.image("hilti_logo.png", x=10, y=8, w=35)
    
    # 2. Tiêu đề
    pdf.set_y(25)
    pdf.set_font('Roboto', '', 18)
    pdf.cell(0, 10, 'BIÊN BẢN NHẬN MÁY HILTI', ln=True, align='C')
    pdf.ln(10)
    
    # 3. Nội dung (Sửa lỗi multi_cell ở đây)
    pdf.set_font('Roboto', '', 11)
    
    # Định nghĩa độ rộng cột cụ thể (Tổng A4 khoảng 190mm)
    col_label = 45
    col_value = 145 

    fields = [
        ("Tên đơn vị:", data['company_name']),
        ("Địa chỉ:", data['address']),
        ("Người gửi:", data['sender_name']),
        ("Số điện thoại:", data['phone']),
        ("Thiết bị:", data['device_name']),
        ("Số Seri:", data['serial_number']),
    ]
    
    for label, value in fields:
        # Vẽ ô nhãn
        pdf.cell(col_label, 10, label, border=1)
        # Vẽ ô giá trị (Dùng cell thay vì multi_cell cho các dòng ngắn để an toàn)
        pdf.cell(col_value, 10, str(value), border=1, ln=True)
        
    # Riêng phần Tình trạng máy dùng multi_cell nhưng phải xuống dòng mới
    pdf.cell(col_label, 10, "Tình trạng máy:", border=1)
    # Xuống dòng rồi mới vẽ Multi-cell để tránh lỗi "Not enough space"
    pdf.multi_cell(col_value, 10, str(data['status']), border=1)
        
    pdf.ln(10)
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 10, f"Thời gian lập phiếu: {timestamp}", ln=True, align='R')
    
    # Ký tên
    pdf.ln(10)
    pdf.cell(95, 10, "Chữ ký khách hàng", align='C')
    pdf.cell(95, 10, "Nhân viên nhận máy", align='C')

    # Trả về bytes - Dùng latin-1 replace để tránh lỗi ký tự đặc biệt
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. LOGIC GIAO DIỆN ---
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    # HIỂN THỊ FORM NHẬP LIỆU
    col_l, col_r = st.columns([1, 4])
    with col_l:
        if os.path.exists("hilti_logo.png"): st.image("hilti_logo.png", width=120)
    with col_r:
        st.title("Biên Bản Nhận Máy")

    with st.form("hilti_form"):
        c1, c2 = st.columns(2)
        company = c1.text_input("Tên đơn vị/Công ty *")
        address = c2.text_input("Địa chỉ giao nhận")
        sender = c1.text_input("Người gửi")
        phone = c2.text_input("Số điện thoại *")
        device = c1.text_input("Thiết bị *")
        serial = c2.text_input("Số Seri *")
        status = st.text_area("Tình trạng máy *")
        
        btn_submit = st.form_submit_button("Gửi thông tin & Tạo biên bản")

    if btn_submit:
        if not (company and phone and device and serial and status):
            st.error("Vui lòng điền đủ các mục có dấu *")
        else:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data = {
                "company_name": company, "address": address, "sender_name": sender,
                "phone": phone, "device_name": device, "serial_number": serial, "status": status
            }
            # Lưu Supabase
            supabase.table("receipts").insert(data).execute()
            # Chuyển trạng thái
            st.session_state.submitted = True
            st.session_state.data = data
            st.session_state.time = now
            st.rerun()

else:
    # HIỂN THỊ PHIẾU SẠCH ĐỂ CHỤP HÌNH
    st.empty()
    data = st.session_state.data
    time_str = st.session_state.time

    st.markdown('<div class="receipt-container">', unsafe_allow_html=True)
    cl1, cl2 = st.columns([1, 3])
    with cl1:
        if os.path.exists("hilti_logo.png"): st.image("hilti_logo.png", width=100)
    with cl2:
        st.markdown("<h2 style='text-align:center;'>PHIẾU XÁC NHẬN</h2>", unsafe_allow_html=True)
    
    st.write(f"**🏢 Đơn vị:** {data['company_name']}")
    st.write(f"**📍 Địa chỉ:** {data['address']}")
    st.write(f"**👤 Người gửi:** {data['sender_name']} - **📞 SĐT:** {data['phone']}")
    st.write(f"**🛠️ Thiết bị:** {data['device_name']} - **🔢 Seri:** {data['serial_number']}")
    st.write(f"**📋 Tình trạng:** {data['status']}")
    st.caption(f"Thời gian: {time_str}")
    st.markdown('</div>', unsafe_allow_html=True)

    # NÚT PDF VÀ QUAY LẠI
    st.write("")
    col_pdf, col_back = st.columns(2)
    
    with col_pdf:
        pdf_data = generate_pdf(data, time_str)
        st.download_button("📄 Tải PDF", data=pdf_data, file_name="Hilti_Receipt.pdf", mime="application/pdf")
    
    with col_back:
        if st.button("➕ Tạo phiếu mới"):
            st.session_state.submitted = False
            st.rerun()