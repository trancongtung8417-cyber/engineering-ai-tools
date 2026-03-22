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
    
    # Khai báo đường dẫn font bạn đang dùng
    font_path = "Roboto-Regular.ttf"
    
    if os.path.exists(font_path):
        pdf.add_font('Roboto', '', font_path, uni=True)
        pdf.set_font('Roboto', '', 12)
    else:
        pdf.set_font('Arial', '', 12)

    # Logo
    if os.path.exists("hilti_logo.png"):
        pdf.image("hilti_logo.png", x=10, y=8, w=35)
    
    pdf.set_y(20)
    pdf.set_font('Roboto', '', 20)
    pdf.cell(0, 10, 'BIÊN BẢN NHẬN MÁY HILTI', ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font('Roboto', '', 12)
    # Nội dung bảng
    fields = [
        ("Đơn vị:", data['company_name']),
        ("Địa chỉ:", data['address']),
        ("Người gửi:", data['sender_name']),
        ("SĐT:", data['phone']),
        ("Thiết bị:", data['device_name']),
        ("Số Seri:", data['serial_number']),
        ("Tình trạng:", data['status'])
    ]
    
    for label, value in fields:
        pdf.cell(50, 10, label, border=1)
        pdf.multi_cell(0, 10, str(value), border=1)
        
    pdf.ln(10)
    pdf.cell(0, 10, f"Ngày tạo: {timestamp}", ln=1, align='R')
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