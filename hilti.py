import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import os
from datetime import datetime
import io

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hilti - Phiếu Xác Nhận", 
    page_icon="🛠️", 
    layout="centered" # Dùng centered để phiếu gom gọn khi chụp hình
)

# --- 2. KẾT NỐI SUPABASE ---
# Đảm bảo bạn đã điền đúng URL và KEY trong mục Secrets trên Streamlit Cloud
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Lỗi cấu hình Secrets: {e}. Vui lòng kiểm tra lại thiết lập trên Streamlit Cloud.")
    st.stop()

# --- 3. CSS GIAO DIỆN (MÀU ĐỎ HILTI & KHUNG VIỀN) ---
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
    
    /* Cấu hình khung chứa phiếu */
    .receipt-main-container {
        padding: 30px;
        background-color: #FFFFFF;
        margin-top: -30px; /* Kéo lên trên cùng */
    }

    /* Khung viền đỏ bo góc bao lấy tiêu đề */
    .receipt-header-box {
        border: 2px solid #DD2222;
        padding: 15px;
        border-radius: 20px; /* Bo góc */
        text-align: center;
        margin-bottom: 25px;
        margin-top: 15px;
    }
    
    .receipt-header-text {
        color: #DD2222;
        margin: 0;
        font-size: 1.8rem;
    }

    /* Chỉnh cỡ chữ lớn hơn cho phiếu chụp hình */
    .receipt-info-text {
        font-size: 1.1rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HÀM TẠO FILE PDF (DÙNG THƯ VIỆN FPDF) ---
# Dùng bytes(pdf.output()) để trả về dữ liệu PDF dạng bytes
def generate_pdf(data, timestamp):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Khai báo đường dẫn font Roboto-Regular.ttf bạn đang dùng
    # Đảm bảo file .ttf này đã được upload lên GitHub
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Roboto', '', font_path, uni=True)
        pdf.set_font('Roboto', '', 12)
    else:
        # Nếu chưa có font trên Github, dùng tạm font mặc định (không dấu)
        pdf.set_font('Helvetica', '', 12)

    # 1. Chèn Logo Hilti lên trên cùng
    logo_path = "hilti_logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
    
    # 2. Khung viền đỏ bo góc bao lấy tiêu đề PDF
    pdf.set_y(15)
    
    # Thiết lập màu viền đỏ
    pdf.set_draw_color(221, 34, 34) 
    # Thiết lập màu chữ đỏ
    pdf.set_text_color(221, 34, 34) 
    
    # Vị trí và kích thước khung
    box_x = 10
    box_y = 15
    box_w = 190
    box_h = 16
    r = 5 # Bán kính bo góc
    
    # Vẽ khung chữ nhật bo góc
    pdf.rounded_rect(x=box_x, y=box_y, w=box_w, h=box_h, r=r)
    
    # Viết chữ vào trong khung
    pdf.set_xy(box_x, box_y + 1)
    pdf.set_font('Roboto', '', 18)
    pdf.cell(box_w, box_h - 2, 'PHIẾU XÁC NHẬN NHẬN MÁY', ln=True, align='C')
    
    pdf.ln(10) # Khoảng cách xuống
    # Reset màu chữ về đen
    pdf.set_text_color(0, 0, 0) 
    pdf.set_font('Roboto', '', 12)
    
    # 3. Kẻ bảng nội dung
    col_label = 45
    col_value = 145 

    fields = [
        ("🏢 Đơn vị:", data['company_name']),
        ("📍 Địa chỉ:", data['address']),
        ("👤 Người gửi:", data['sender_name']),
        ("📞 Số điện thoại:", data['phone']),
        ("🛠️ Thiết bị:", data['device_name']),
        ("🔢 Số Seri:", data['serial_number']),
    ]
    
    for label, value in fields:
        # Vẽ ô nhãn
        pdf.cell(col_label, 10, label, border=1)
        # Vẽ ô giá trị
        pdf.cell(col_value, 10, str(value), border=1, ln=True)
        
    # Riêng phần Tình trạng máy dùng multi_cell nhưng phải xuống dòng mới
    pdf.cell(col_label, 10, "📋 Tình trạng:", border=1)
    pdf.multi_cell(col_value, 10, str(data['status']), border=1)
    
    pdf.ln(10)
    
    # 4. Phần chữ ký và thời gian
    pdf.set_font('Roboto', '', 10)
    pdf.cell(0, 5, f'Thời gian lập phiếu: {timestamp}', ln=True, align='R')
    
    pdf.ln(20)
    pdf.cell(95, 5, 'Chữ ký Người gửi', align='C')
    pdf.cell(95, 5, 'Chữ ký Nhân viên Hilti', align='C', ln=1)
    
    # Trả về bytes
    return bytes(pdf.output())

# ==========================================================
# --- 5. LOGIC GIAO DIỆN ---
# ==========================================================

# Khởi tạo Session State
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False
if 'submitted_data' not in st.session_state:
    st.session_state['submitted_data'] = {}
if 'receipt_time' not in st.session_state:
    st.session_state['receipt_time'] = ""

logo_path = "hilti_logo.png"

# --- MÀN HÌNH 2: CHỈ HIỂN THỊ PHIẾU ĐỂ CHỤP HÌNH & TẢI PDF ---
if st.session_state['form_submitted']:
    st.empty() # Xóa sạch các ô nhập liệu cũ
    
    # Lấy dữ liệu đã lưu
    data = st.session_state['submitted_data']
    timestamp = st.session_state['receipt_time']
    
    # TẠO CONTAINER SẠCH ĐỂ CHỤP MÀN HÌNH
    st.markdown('<div class="receipt-main-container">', unsafe_allow_html=True)
    
    # Logo Hilti lên trên cùng
    c_logo, _ = st.columns([1, 4])
    with c_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=110)
            
    # Khung viền đỏ bo góc bao lấy tiêu đề
    st.markdown('<div class="receipt-header-box">', unsafe_allow_html=True)
    st.markdown("<h1 class='receipt-header-text'>PHIẾU XÁC NHẬN NHẬN MÁY</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Nội dung hiển thị rõ ràng, cỡ chữ lớn để chụp ảnh
    cl1, cl2 = st.columns(2)
    with cl1:
        st.markdown(f"<p class='receipt-info-text'>🏢 **Đơn vị:** `{data['company_name']}`</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='receipt-info-text'>👤 **Người gửi:** `{data['sender_name']}`</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='receipt-info-text'>🛠️ **Thiết bị:** `{data['device_name']}`</p>", unsafe_allow_html=True)
    with cl2:
        st.markdown(f"<p class='receipt-info-text'>📍 **Địa chỉ:** `{data['address']}`</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='receipt-info-text'>📞 **SĐT:** `{data['phone']}`</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='receipt-info-text'>🔢 **Seri:** `{data['serial_number']}`</p>", unsafe_allow_html=True)
    
    st.markdown(f"<p class='receipt-info-text'>📋 **Tình trạng:** {data['status']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption(f"Ngày tạo: {timestamp}")
    st.caption("⚠️ Đây là phiếu xác nhận điện tử. Nhân viên Hilti sẽ liên hệ để xác nhận lại thông tin.")
    
    st.markdown('</div>', unsafe_allow_html=True) # Đóng main-container
    
    st.write("") # Khoảng trống

    # NÚT CHỨC NĂNG: TẢI PDF & TẠO PHIẾU MỚI
    col_pdf, col_new = st.columns(2)
    with col_pdf:
        with st.spinner('Đang tạo file PDF...'):
            try:
                pdf_bytes = generate_pdf(data, timestamp)
                file_name = f"Hilti_{data['serial_number']}.pdf"
                st.download_button(
                    label="📄 Tải File PDF",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    type="secondary"
                )
            except Exception as e:
                st.error(f"❌ Lỗi tạo PDF: {e}")
    
    with col_new:
        if st.button("➕ Tạo phiếu mới"):
            # Reset trạng thái
            st.session_state['form_submitted'] = False
            st.session_state['submitted_data'] = {}
            st.rerun()
            
    st.info("💡 Cách 1: Chụp màn hình khung phía trên và gửi Zalo. Cách 2: Tải file PDF.")
    st.stop() # Dừng, không hiển thị Form nhập liệu bên dưới


# --- MÀN HÌNH 1: FORM NHẬP THÔNG TIN (BAN ĐẦU) ---
col_form_logo, col_form_title = st.columns([1, 4])
with col_form_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.error("Missing file `hilti_logo.png` on GitHub.")
with col_form_title:
    st.title("Biên Bản Nhận Máy Hilti")
    st.write("Vui lòng điền thông tin chi tiết của thiết bị.")

# --- FORM NHẬP THÔNG TIN ---
with st.form("receipt_form", clear_on_submit=True):
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