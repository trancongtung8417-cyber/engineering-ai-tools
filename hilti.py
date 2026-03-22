import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import os
from datetime import datetime
import io

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hilti - Biên Bản Nhận Máy", 
    page_icon="🛠️", 
    layout="centered" # Dùng centered để phiếu gom gọn khi chụp hình
)

# --- CẤU HÌNH SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Lỗi cấu hình Secrets: {e}. Vui lòng kiểm tra lại thiết lập trên Streamlit Cloud.")
    st.stop()

# --- CSS ĐỂ TÙY CHỈNH MÀU SẮC & GIAO DIỆN PHIẾU ---
st.markdown("""
    <style>
    /* Màu đỏ Hilti cho các nút và tiêu đề */
    div.stButton > button:first-child {
        background-color: #DD2222 !important;
        color: white !important;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #A01A1A !important;
        color: white !important;
    }
    /* Khung chứa phiếu xác nhận khi chụp màn hình */
    .receipt-container {
        border: 3px solid #DD2222;
        padding: 30px;
        border-radius: 15px;
        background-color: #FFFFFF;
        margin-top: -30px; /* Kéo lên trên cùng */
    }
    .receipt-header {
        color: #DD2222;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Chỉnh cỡ chữ lớn hơn cho phiếu chụp hình */
    .receipt-text {
        font-size: 1.2rem;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_key=True)

# --- KHỞI TẠO BIẾN TRẠNG THÁI SESSION STATE ---
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False
if 'submitted_data' not in st.session_state:
    st.session_state['submitted_data'] = {}
if 'receipt_time' not in st.session_state:
    st.session_state['receipt_time'] = ""

logo_path = "hilti_logo.png"

# ==========================================================
# --- HÀM TẠO FILE PDF (DÙNG THƯ VIỆN FPDF) ---
# ==========================================================
def generate_pdf(data, timestamp):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. Thêm Font hỗ trợ tiếng Việt (Quan trọng!)
    # Bạn cần tải 2 file font dejavu-sans-condensed.ttf và dejavu-sans-condensed-bold.ttf lên Github
    # Link tải font: https://github.com/reingart/pyfpdf/raw/master/font/dejavu-sans-condensed.ttf
    # Nếu không có font này, tiếng Việt sẽ bị lỗi ô vuông.
    font_path = "dejavu-sans-condensed.ttf"
    font_bold_path = "dejavu-sans-condensed-bold.ttf"
    
    if os.path.exists(font_path) and os.path.exists(font_bold_path):
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.add_font('DejaVu', 'B', font_bold_path, uni=True)
        pdf.set_font('DejaVu', '', 12)
    else:
        # Nếu không có font, dùng helvetica (nhưng sẽ lỗi tiếng Việt)
        pdf.set_font('Helvetica', '', 12)
        st.warning("⚠️ Thiếu file Font Tiếng Việt trên GitHub. PDF có thể bị lỗi font.")

    # 2. Chèn Logo
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=40)
    
    # 3. Tiêu đề PDF
    pdf.set_xy(0, 15)
    pdf.set_font('DejaVu', 'B', 20)
    pdf.set_text_color(221, 34, 34) # Màu đỏ Hilti
    pdf.cell(0, 10, 'BIÊN BẢN NHẬN MÁY HILTI', ln=1, align='C')
    
    pdf.ln(15) # Khoảng cách xuống
    pdf.set_text_color(0, 0, 0) # Về màu đen
    pdf.set_font('DejaVu', '', 12)
    
    # 4. Kẻ bảng nội dung
    col_width = 90
    row_height = 8
    
    # Dữ liệu dạng danh sách để vẽ bảng
    table_data = [
        ("Tên đơn vị/Công ty:", data['company_name']),
        ("Địa chỉ giao nhận:", data['address']),
        ("Người gửi:", data['sender_name']),
        ("Số điện thoại:", data['phone']),
        ("Thiết bị (Model):", data['device_name']),
        ("Số Seri:", data['serial_number'])
    ]
    
    # Vẽ các dòng thông thường
    for item in table_data:
        pdf.cell(col_width, row_height, item[0], border=1)
        pdf.cell(col_width, row_height, item[1], border=1, ln=1)
        
    # Dòng Tình trạng máy (Multi-line)
    pdf.cell(col_width, row_height, "Tình trạng máy:", border=1)
    pdf.multi_cell(col_width, row_height, data['status'], border=1)
    
    pdf.ln(10)
    
    # 5. Phần chữ ký và thời gian
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(0, 5, f'Thời gian lập phiếu: {timestamp}', ln=1, align='R')
    
    pdf.ln(20)
    pdf.cell(col_width, 5, 'Chữ ký Người gửi', align='C')
    pdf.cell(col_width, 5, 'Chữ ký Nhân viên Hilti', align='C', ln=1)
    
    # Trả về dữ liệu PDF dạng bytes
    return pdf.output(dest='S').encode('latin-1')

# ==========================================================
# --- GIAO DIỆN CHÍNH ---
# ==========================================================

# MÀN HÌNH 2: CHỈ HIỂN THỊ PHIẾU ĐỂ CHỤP HÌNH & TẢI PDF
if st.session_state['form_submitted']:
    st.empty() # Xóa sạch các ô nhập liệu cũ
    
    # Lấy dữ liệu đã lưu
    data = st.session_state['submitted_data']
    timestamp = st.session_state['receipt_time']
    
    # TẠO CONTAINER SẠCH ĐỂ CHỤP MÀN HÌNH
    # Bạn nhắc khách: "Kéo trọn cái khung đỏ này vào màn hình rồi chụp"
    st.markdown('<div class="receipt-container">', unsafe_allow_key=True)
    
    # Logo và tiêu đề trong phiếu
    r_col_l, r_col_r = st.columns([1, 4])
    with r_col_l:
        if os.path.exists(logo_path):
            st.image(logo_path, width=130)
    with r_col_r:
        st.markdown("<h1 class='receipt-header'>BIÊN BẢN NHẬN MÁY</h1>", unsafe_allow_key=True)
    
    st.markdown("---")
    
    # Nội dung hiển thị rõ ràng, cỡ chữ lớn để chụp ảnh
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<p class='receipt-text'>🏢 **Đơn vị:** `{data['company_name']}`</p>", unsafe_allow_key=True)
        st.markdown(f"<p class='receipt-text'>👤 **Người gửi:** `{data['sender_name']}`</p>", unsafe_allow_key=True)
        st.markdown(f"<p class='receipt-text'>🛠️ **Thiết bị:** `{data['device_name']}`</p>", unsafe_allow_key=True)
    with c2:
        st.markdown(f"<p class='receipt-text'>📍 **Địa chỉ:** `{data['address']}`</p>", unsafe_allow_key=True)
        st.markdown(f"<p class='receipt-text'>📞 **SĐT:** `{data['phone']}`</p>", unsafe_allow_key=True)
        st.markdown(f"<p class='receipt-text'>🔢 **Seri:** `{data['serial_number']}`</p>", unsafe_allow_key=True)
    
    st.markdown(f"<p class='receipt-text'>📋 **Tình trạng:** {data['status']}</p>", unsafe_allow_key=True)
    st.markdown("---")
    st.caption(f"Ngày tạo: {timestamp}")
    st.caption("⚠️ Đây là phiếu xác nhận điện tử. Nhân viên Hilti sẽ liên hệ để xác nhận lại thông tin.")
    
    st.markdown('</div>', unsafe_allow_key=True) # Đóng container
    
    st.write("") # Khoảng trống

    # NÚT CHỨC NĂNG: TẢI PDF & TẠO PHIẾU MỚI
    col_pdf, col_new = st.columns(2)
    with col_pdf:
        # Tạo dữ liệu PDF khi người dùng nhấn nút
        with st.spinner('Đang tạo file PDF...'):
            pdf_bytes = generate_pdf(data, timestamp)
            
        # Nút Download PDF
        file_name = f"Hilti_BienBan_{data['serial_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        st.download_button(
            label="📄 Tải File PDF Chuyên Nghiệp",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            type="secondary"
        )
    
    with col_new:
        if st.button("➕ Tạo phiếu mới"):
            # Reset trạng thái
            st.session_state['form_submitted'] = False
            st.session_state['submitted_data'] = {}
            st.rerun()
            
    st.info("💡 Cách 1: Chụp màn hình khung đỏ phía trên và gửi Zalo. Cách 2: Tải file PDF.")
    st.stop() # Dừng, không hiển thị Form nhập liệu bên dưới


# MÀN HÌNH 1: FORM NHẬP THÔNG TIN (BAN ĐẦU)
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.error("Missing file `hilti_logo.png` on GitHub.")
with col_title:
    st.title("Biên Bản Nhận Máy Hilti")
    st.write("Vui lòng điền thông tin chi tiết của thiết bị.")

# --- FORM NHẬP THÔNG TIN ---
with st.form("receipt_form", clear_on_submit=True):
    # Dùng nested columns để layout đẹp hơn trên cả mobile/desktop
    col_l, col_r = st.columns(2)
    with col_l:
        company = st.text_input("🏢 Tên đơn vị/Công ty *", placeholder="Nhập tên công ty...")
        sender = st.text_input("👤 Người gửi", placeholder="Nhập tên người gửi...")
        device = st.text_input("🛠️ Thiết bị (Model) *", placeholder="Ví dụ: TE 700-AVR")
    with col_r:
        address = st.text_input("📍 Địa chỉ giao nhận", placeholder="Nhập địa chỉ chi tiết...")
        phone = st.text_input("📞 Số điện thoại *", placeholder="Ví dụ: 090xxxxxxx")
        serial = st.text_input("🔢 Số Seri *", placeholder="Nhập số seri máy...")

    status = st.text_area("📋 Tình trạng máy *", placeholder="Mô tả lỗi (ví dụ: không hoạt động, không khoan, không đục...)")
    
    st.caption("Các trường có dấu (*) là bắt buộc.")
    submitted = st.form_submit_button("Gửi thông tin & Tạo biên bản", type="primary")

# --- XỬ LÝ SAU KHI GỬI FORM ---
if submitted:
    if not company or not phone or not device or not serial or not status:
        st.error("⚠️ Vui lòng điền đầy đủ các thông tin bắt buộc!")
    else:
        # Chuẩn bị dữ liệu
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data = {
            "company_name": company, "address": address, "sender_name": sender,
            "phone": phone, "device_name": device, "serial_number": serial, "status": status
        }
        
        with st.spinner('Đang gửi dữ liệu đến Database...'):
            try:
                # 1. Lưu dữ liệu vào Supabase
                supabase.table("receipts").insert(data).execute()
                
                # 2. Cập nhật Session State để chuyển sang màn hình Phiếu xác nhận
                st.session_state['form_submitted'] = True
                st.session_state['submitted_data'] = data
                st.session_state['receipt_time'] = timestamp
                st.rerun() # Load lại trang để chuyển sang MÀN HÌNH 2

            except Exception as e:
                st.error(f"❌ Lỗi kết nối database: {e}")