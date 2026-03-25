import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import os

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hilti - Biên Bản", page_icon="🛠️", layout="centered")

# --- 2. KẾT NỐI SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Lỗi cấu hình Secrets: {e}")
    st.stop()

# --- 3. CSS GIAO DIỆN (CĂN ĐẦU HÀNG, BỎ KHUNG MỜ) ---
st.markdown("""
    <style>
    
    /* 1. Ẩn thanh Header (Fork, GitHub, Menu) */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 2. Ẩn nút Deploy (Vương miện đỏ) */
    .stAppDeployButton {
        display: none !important;
    }

    /* 3. Ẩn Toolbar góc dưới bên phải (Logo Streamlit & Status) */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* 4. Ẩn Footer 'Made with Streamlit' */
    footer {
        display: none !important;
    }

    /* 5. Xóa khoảng trắng thừa do header để lại */
    .main .block-container {
        padding-top: 0rem;
        margin-top: -2rem;
    }



    div.stButton > button[kind="primaryFormSubmit"] {
        background-color: #DD2222 !important;
        color: white !important;
        border: none !important;
    }
    
    .receipt-container { padding: 30px; background-color: #FFFFFF; }

    .header-box-gray {
        border: 2px solid #808080; 
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 60px; 
        margin-bottom: 40px;
    }
    
    .header-text-red { color: #DD2222; font-size: 2rem; font-weight: bold; margin: 0; }

    .info-row {
        border-bottom: 1px solid #E0E0E0;
        padding: 12px 0;
        display: flex;
    }
    .info-label {
        width: 120px; 
        font-weight: bold;
        color: #333;
        flex-shrink: 0;
    }
    .info-value {
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HÀM TẠO PDF (ĐÃ SỬA LỖI SET_FONT) ---
def generate_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Roboto', '', font_path, uni=True)
        pdf.set_font('Roboto', '', 12)
    else:
        pdf.set_font('Helvetica', '', 12)

    if os.path.exists("hilti_logo.png"):
        pdf.image("hilti_logo.png", x=15, y=15, w=40)
    
    # Tiêu đề
    pdf.set_y(50) 
    pdf.set_draw_color(128, 128, 128) 
    pdf.rect(10, 50, 190, 18)
    pdf.set_text_color(221, 34, 34) 
    pdf.set_xy(10, 54)
    pdf.set_font('Roboto', '', 20)
    pdf.cell(190, 10, 'BIÊN BẢN NHẬN MÁY', ln=True, align='C')
    
    # Nội dung PDF
    pdf.ln(25)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Roboto', '', 12)
    pdf.set_draw_color(224, 224, 224) 
    
    fields = [
        ("Đơn vị:", data['company_name']),
        ("Địa chỉ:", data['address']),
        ("Người gửi:", data['sender_name']),
        ("SĐT:", data['phone']),
        ("Thiết bị:", data['device_name']),
        ("Số Seri:", data['serial_number']),
    ]
    
    for label, value in fields:
        pdf.set_font('Roboto', '', 12) # Đảm bảo font style đúng
        pdf.cell(35, 12, label, border='B')
        pdf.cell(155, 12, str(value), border='B', ln=True)
        
    pdf.ln(10)
    # SỬA LỖI TẠI ĐÂY: Không dùng tham số thứ 4, dùng style ở tham số thứ 2
    # Nếu bạn chỉ có file Regular, hãy để style là '' để tránh lỗi
    pdf.set_font('Roboto', '', 12) 
    pdf.cell(0, 10, "Tình trạng máy:", ln=True)
    pdf.multi_cell(0, 10, str(data['status']))
    
    return bytes(pdf.output())

# --- 5. LOGIC HIỂN THỊ ---
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False

if st.session_state['form_submitted']:
    d = st.session_state['submitted_data']
    
    st.markdown('<div class="receipt-container">', unsafe_allow_html=True)
    if os.path.exists("hilti_logo.png"):
        st.image("hilti_logo.png", width=150)
    
    st.markdown(f'<div class="header-box-gray"><h1 class="header-text-red">BIÊN BẢN NHẬN MÁY</h1></div>', unsafe_allow_html=True)
    
    # Thông tin hiển thị bám đầu hàng
    st.markdown(f'<div class="info-row"><div class="info-label">🏢 Đơn vị:</div><div class="info-value">{d["company_name"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-row"><div class="info-label">📍 Địa chỉ:</div><div class="info-value">{d["address"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-row"><div class="info-label">👤 Người gửi:</div><div class="info-value">{d["sender_name"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-row"><div class="info-label">📞 SĐT:</div><div class="info-value">{d["phone"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-row"><div class="info-label">🛠️ Thiết bị:</div><div class="info-value">{d["device_name"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-row"><div class="info-label">🔢 Số Seri:</div><div class="info-value">{d["serial_number"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="padding: 20px 0;"><b>📋 Tình trạng:</b><br>{d["status"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    col_pdf, col_new = st.columns(2)
    with col_pdf:
        pdf_bytes = generate_pdf(d)
        st.download_button("📄 Tải PDF", data=pdf_bytes, file_name=f"Hilti_{d['serial_number']}.pdf", mime="application/pdf", use_container_width=True)
    with col_new:
        # Nút này bây giờ sẽ tự động có màu trắng viền xám giống nút Tải PDF
        if st.button("➕ Tạo phiếu mới", use_container_width=True):
            st.session_state['form_submitted'] = False
            st.rerun()
    # col_pdf, col_new = st.columns(2)
    # with col_pdf:
    #     pdf_bytes = generate_pdf(d)
    #     st.download_button("📄 Tải PDF", data=pdf_bytes, file_name=f"Hilti_{d['serial_number']}.pdf", mime="application/pdf")
    # with col_new:
    #     if st.button("➕ Tạo phiếu mới"):
    #         st.session_state['form_submitted'] = False
    #         st.rerun()
    
    st.stop()

# --- MÀN HÌNH NHẬP LIỆU ---

if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.title("🔴 HILTI TOOL SERVICE CENTER")
st.subheader("BIÊN BẢN NHẬN MÁY")
st.write("Vui lòng điền thông tin máy cần bảo hành/sửa chữa.")

with st.form("input_form"):
    c1, c2 = st.columns(2)
    comp = c1.text_input("Đơn vị *")
    addr = c1.text_input("Địa chỉ")
    send = c1.text_input("Người gửi")
    phon = c2.text_input("Số điện thoại *")
    devi = c2.text_input("Thiết bị *")
    seri = c2.text_input("Số Seri *")
    stat = st.text_area("Tình trạng máy *")
    
    if st.form_submit_button("Gửi & Tạo biên bản"):
        if all([comp, phon, devi, seri, stat]):
            data_to_save = {"company_name": comp, "address": addr, "sender_name": send, "phone": phon, "device_name": devi, "serial_number": seri, "status": stat}
            supabase.table("receipts").insert(data_to_save).execute()
            st.session_state['form_submitted'] = True
            st.session_state['submitted_data'] = data_to_save
            st.rerun()
        else:
            st.error("Vui lòng điền đủ các mục có dấu *")