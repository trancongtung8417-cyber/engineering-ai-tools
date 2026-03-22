import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import os
from datetime import datetime

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hilti - Phiếu Xác Nhận", page_icon="🛠️", layout="centered")

# --- 2. KẾT NỐI SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Lỗi cấu hình Secrets: {e}")
    st.stop()

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
    <style>
    div.stButton > button:first-child { background-color: #DD2222 !important; color: white !important; border: none; }
    .receipt-main-container { padding: 20px; background-color: #FFFFFF; }
    .receipt-header-box {
        border: 2px solid #DD2222;
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        margin: 15px 0;
    }
    .receipt-header-text { color: #DD2222; font-size: 1.6rem; font-weight: bold; }
    .receipt-info-text { font-size: 1.1rem; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HÀM TẠO PDF (BẢN AN TOÀN) ---
def generate_pdf(data, timestamp):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Roboto', '', font_path, uni=True)
        pdf.set_font('Roboto', '', 12)
    else:
        pdf.set_font('Helvetica', '', 12)

    # Logo trên cùng
    if os.path.exists("hilti_logo.png"):
        pdf.image("hilti_logo.png", x=10, y=8, w=30)
    
    # Tiêu đề trong khung
    pdf.set_y(20)
    pdf.set_draw_color(221, 34, 34)
    pdf.set_text_color(221, 34, 34)
    pdf.set_line_width(0.5)
    pdf.cell(150, 12, 'BIÊN BẢN NHẬN MÁY', border=1, ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Roboto', '', 11)
    
    # Nội dung
    col_label = 40
    col_value = 150
    fields = [
        ("Đơn vị:", data['company_name']),
        ("Địa chỉ:", data['address']),
        ("Người gửi:", data['sender_name']),
        ("SĐT:", data['phone']),
        ("Thiết bị:", data['device_name']),
        ("Số Seri:", data['serial_number']),
    ]
    
    for label, value in fields:
        pdf.cell(col_label, 9, label, border='B')
        pdf.cell(col_value, 9, str(value), border='B', ln=True)
        
    pdf.ln(5)
    pdf.cell(col_label, 9, "Tình trạng:", border=0)
    pdf.multi_cell(col_value, 9, str(data['status']), border=0)
    
    pdf.ln(10)
    pdf.set_font('Roboto', '', 9)
    pdf.cell(0, 5, f'Ngày lập: {timestamp}', ln=True, align='R')
    
    return bytes(pdf.output())

# --- 5. LOGIC GIAO DIỆN ---
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False

if st.session_state['form_submitted']:
    # MÀN HÌNH PHIẾU XÁC NHẬN
    data = st.session_state['submitted_data']
    time_now = st.session_state['receipt_time']
    
    st.markdown('<div class="receipt-main-container">', unsafe_allow_html=True)
    if os.path.exists("hilti_logo.png"):
        st.image("hilti_logo.png", width=100)
    
    st.markdown('<div class="receipt-header-box"><h1 class="receipt-header-text">PHIẾU XÁC NHẬN NHẬN MÁY</h1></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**🏢 Đơn vị:** {data['company_name']}")
        st.markdown(f"**👤 Người gửi:** {data['sender_name']}")
        st.markdown(f"**🛠️ Thiết bị:** {data['device_name']}")
    with c2:
        st.markdown(f"**📍 Địa chỉ:** {data['address']}")
        st.markdown(f"**📞 SĐT:** {data['phone']}")
        st.markdown(f"**🔢 Seri:** {data['serial_number']}")
    st.markdown(f"**📋 Tình trạng:** {data['status']}")
    st.caption(f"Thời gian: {time_now}")
    st.markdown('</div>', unsafe_allow_html=True)

    col_pdf, col_new = st.columns(2)
    with col_pdf:
        pdf_bytes = generate_pdf(data, time_now)
        st.download_button("📄 Tải PDF", data=pdf_bytes, file_name=f"Hilti_{data['serial_number']}.pdf", mime="application/pdf")
    with col_new:
        if st.button("➕ Tạo phiếu mới"):
            st.session_state['form_submitted'] = False
            st.rerun()
    st.stop()

# --- MÀN HÌNH NHẬP LIỆU ---
if os.path.exists("hilti_logo.png"):
    st.image("hilti_logo.png", width=120)
st.title("Biên Bản Nhận Máy")

with st.form("hilti_form"):
    col_a, col_b = st.columns(2)
    comp = col_a.text_input("Đơn vị *")
    addr = col_b.text_input("Địa chỉ")
    send = col_a.text_input("Người gửi")
    phon = col_b.text_input("Số điện thoại *")
    devi = col_a.text_input("Thiết bị *")
    seri = col_b.text_input("Số Seri *")
    stat = st.text_area("Tình trạng máy *")
    if st.form_submit_button("Gửi & Tạo biên bản"):
        if comp and phon and devi and seri and stat:
            d = {"company_name": comp, "address": addr, "sender_name": send, "phone": phon, "device_name": devi, "serial_number": seri, "status": stat}
            supabase.table("receipts").insert(d).execute()
            st.session_state['form_submitted'] = True
            st.session_state['submitted_data'] = d
            st.session_state['receipt_time'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.rerun()
        else:
            st.error("Vui lòng nhập đủ thông tin!")