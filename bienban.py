import streamlit as st
from fpdf import FPDF
import os
import requests
import base64

# --- 1. CẤU HÌNH THÔNG TIN QUẢN LÝ ---
ZALO_PHONE = "0908080163"  
TELEGRAM_TOKEN = "8647065958:AAEt8IxfNG_zH5POVxf02_DacVdzuGyHaKE" 
TELEGRAM_CHAT_ID = "1855505540"

# --- 2. HÀM GỬI FILE QUA TELEGRAM ---
def send_to_telegram(file_data, filename, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {'document': (filename, file_data)}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
    try:
        requests.post(url, data=data, files=files, timeout=10)
    except:
        pass

# --- 3. HÀM TẠO PDF CHUYÊN NGHIỆP ---
def create_pdf(company, add, name_phone, tool, note):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Vẽ khung viền trang trí
    pdf.set_line_width(0.5)
    pdf.set_draw_color(150, 150, 150) 
    pdf.rect(7, 7, 196, 283) 
    pdf.set_line_width(0.2)
    pdf.rect(8, 8, 194, 281) 

    # Cài đặt Font Unicode (Yêu cầu file Roboto-Regular.ttf trên GitHub)
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Vietnamese', '', font_path)
        pdf.set_font('Vietnamese', size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    # Tiêu đề màu đỏ Hilti
    pdf.ln(10)
    pdf.set_text_color(220, 0, 0)
    pdf.set_font('Vietnamese', size=22)
    pdf.cell(0, 15, txt="BIÊN BẢN NHẬN MÁY", ln=True, align='C')
    
    pdf.set_draw_color(150, 150, 150)
    pdf.line(70, 32, 140, 32)
    pdf.ln(15)

    # Nội dung thông tin
    pdf.set_text_color(0, 0, 0)
    def add_info_row(label, value):
        pdf.set_font('Vietnamese', size=11)
        pdf.set_color = (100, 100, 100)
        pdf.cell(50, 10, txt=f"{label}:", border='B', ln=0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Vietnamese', size=12)
        pdf.cell(0, 10, txt=f" {value}", border='B', ln=True)
        pdf.ln(2)

    add_info_row("Tên đơn vị/Công ty", company)
    add_info_row("Địa chỉ giao nhận", add)
    add_info_row("Người gửi & Số ĐT", name_phone)
    add_info_row("Thiết bị & Số Seri", tool)
    
    pdf.ln(5)
    pdf.set_font('Vietnamese', size=12)
    pdf.cell(0, 10, txt="Tình trạng máy khi tiếp nhận:", ln=True)
    pdf.set_font('Vietnamese', size=11)
    pdf.multi_cell(0, 10, txt=note, border=1)

    # Phần chữ ký
    pdf.ln(20)
    pdf.set_font('Vietnamese', size=12)
    pdf.cell(95, 10, txt="KHÁCH HÀNG XÁC NHẬN", ln=0, align='C')
    pdf.cell(95, 10, txt="NGƯỜI NHẬN MÁY", ln=1, align='C')

    return pdf.output()

# --- 4. HÀM TỰ ĐỘNG TẢI VÀ MỞ FILE ---
def auto_download_and_open(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    js_code = f"""
    <script>
    var b64_data = 'data:application/pdf;base64,{b64}';
    
    // Tải về máy
    var dl = document.createElement('a');
    dl.href = b64_data;
    dl.download = '{filename}';
    document.body.appendChild(dl);
    dl.click();
    document.body.removeChild(dl);
    
    // Mở trong tab mới
    window.open(b64_data, '_blank');
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 5. GIAO DIỆN WEB STREAMLIT ---
st.set_page_config(page_title="Hilti Service - Tiếp Nhận Máy", page_icon="🔧")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; background-color: #dd0000; color: white;
        font-weight: bold; border-radius: 10px; padding: 15px; font-size: 18px; border: none;
    }
    .stButton>button:hover { background-color: #ff3333; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.title("🔴 HILTI TOOL SERVICE CENTER")

st.subheader("BIÊN BẢN NHẬN MÁY")

with st.container():
    company = st.text_input("🏢 Tên Công Ty:")
    add = st.text_input("📍 Địa chỉ nhận và trả máy:")
    name_phone = st.text_input("👤 Người gửi và Số điện thoại:")
    tool = st.text_input("🛠️ Tên máy và số Seri:")
    note = st.text_area("⚠️ Tình trạng hư hỏng của máy:")

st.markdown("---")

if st.button("XÁC NHẬN & TẠO PHIẾU"):
    if add and name_phone:
        try:
            pdf_bytes = create_pdf(company, add, name_phone, tool, note)
            
            # 1. Tự động tải và mở file PDF
            auto_download_and_open(pdf_bytes, f"BBNM_{company}.pdf")
            
            # 2. Gửi file về Telegram của bạn
            caption = f"🔔 CÓ MÁY MỚI!\n🏢 {company}\n👤 {name_phone}\n🛠️ {tool}"
            send_to_telegram(pdf_bytes, f"BBNM_{company}.pdf", caption)
            
            st.success("✅ Đã tải và mở file PDF thành công!")
            
            # 3. Hiện nút Zalo để khách gửi file
            zalo_link = f"https://zalo.me/{ZALO_PHONE}"
            st.markdown(f"""
                <a href="{zalo_link}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #0068ff; color: white; text-align: center; padding: 18px; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 20px;">
                        💬 BẤM VÀO ĐÂY ĐỂ GỬI FILE QUA ZALO
                    </div>
                </a>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")
    else:
        st.warning("⚠️ Vui lòng điền Địa chỉ và Số điện thoại.")