import streamlit as st
from fpdf import FPDF
import os
import requests

# --- CẤU HÌNH THÔNG TIN QUẢN LÝ ---
ZALO_PHONE = "0908080163"  # Ví dụ: 0901234567
TELEGRAM_TOKEN = "TOKEN_BOT_CỦA_BẠN"
TELEGRAM_CHAT_ID = "ID_CHAT_CỦA_BẠN"

# --- HÀM GỬI FILE QUA TELEGRAM ---
def send_to_telegram(file_data, filename, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {'document': (filename, file_data)}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
    try:
        requests.post(url, data=data, files=files, timeout=10)
    except:
        pass

# --- HÀM TẠO PDF CHUYÊN NGHIỆP ---
def create_pdf(company, add, name_phone, tool, note):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. Vẽ khung viền trang trí (Border)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(150, 150, 150) 
    pdf.rect(7, 7, 196, 283) 
    pdf.set_line_width(0.2)
    pdf.rect(8, 8, 194, 281) 

    # 2. Cài đặt Font Unicode (Yêu cầu file Roboto-Regular.ttf cùng thư mục)
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Vietnamese', '', font_path)
        pdf.set_font('Vietnamese', size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    # 3. Tiêu đề màu đỏ Hilti
    pdf.ln(10)
    pdf.set_text_color(220, 0, 0)
    pdf.set_font('Vietnamese', size=22)
    pdf.cell(0, 15, txt="BIÊN BẢN NHẬN MÁY", ln=True, align='C')
    
    pdf.set_draw_color(150, 150, 150)
    pdf.line(70, 32, 140, 32)
    pdf.ln(15)

    # 4. Nội dung thông tin
    pdf.set_text_color(0, 0, 0)
    
    def add_info_row(label, value):
        pdf.set_font('Vietnamese', size=11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(50, 10, txt=f"{label}:", border='B', ln=0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Vietnamese', size=12)
        pdf.cell(0, 10, txt=f" {value}", border='B', ln=True)
        pdf.ln(2)

    add_info_row("Tên đơn vị/Công ty", company)
    add_info_row("Địa chỉ giao nhận", add)
    add_info_row("Người gửi & Số ĐT", name_phone)
    add_info_row("Thiết bị & Số Seri", tool)
    
    # Khung tình trạng máy
    pdf.ln(5)
    pdf.set_font('Vietnamese', size=12)
    pdf.cell(0, 10, txt="Tình trạng máy khi tiếp nhận:", ln=True)
    pdf.set_font('Vietnamese', size=11)
    pdf.multi_cell(0, 10, txt=note, border=1)

    # 5. Phần chữ ký
    pdf.ln(20)
    pdf.set_font('Vietnamese', size=12)
    pdf.cell(95, 10, txt="KHÁCH HÀNG XÁC NHẬN", ln=0, align='C')
    pdf.cell(95, 10, txt="NGƯỜI NHẬN MÁY", ln=1, align='C')
    pdf.set_font('Vietnamese', size=10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(95, 10, txt="(Ký và ghi rõ họ tên)", ln=0, align='C')
    pdf.cell(95, 10, txt="(Ký và ghi rõ họ tên)", ln=1, align='C')

    return pdf.output()

# --- GIAO DIỆN WEB STREAMLIT ---
st.set_page_config(page_title="Hilti Service - Tiếp Nhận Máy", page_icon="🔧")

# CSS làm đẹp giao diện
st.markdown(f"""
    <style>
    .stButton>button {{
        width: 100%;
        background-color: #dd0000;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 15px;
        font-size: 18px;
        border: none;
    }}
    .stButton>button:hover {{ background-color: #ff3333; color: white; }}
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
        st.success("✅ Thông tin đã được ghi nhận!")
        with st.expander("👉 NHẤN VÀO ĐÂY ĐỂ XEM TÓM TẮT", expanded=True):
            st.write(f"**Công ty:** {company}")
            st.write(f"**Khách hàng:** {name_phone}")
            st.write(f"**Thiết bị:** {tool}")
            st.write(f"**Tình trạng:** {note}")
        
        try:
            pdf_bytes = create_pdf(company, add, name_phone, tool, note)
            
            # 1. Gửi ngầm về Telegram cho bạn
            caption = f"🔔 CÓ MÁY MỚI!\n🏢 {company}\n👤 {name_phone}\n🛠️ {tool}"
            send_to_telegram(pdf_bytes, f"BBNM_{company}.pdf", caption)
            
            # 2. Nút tải file cho khách
            st.download_button(
                label="📥 1. TẢI BIÊN BẢN PDF VỀ MÁY",
                data=bytes(pdf_bytes),
                file_name=f"BBNM_{company}.pdf",
                mime="application/pdf"
            )
            
            # 3. Nút bấm mở Zalo nhanh
            zalo_link = f"https://zalo.me/{ZALO_PHONE}"
            st.markdown(f"""
                <a href="{zalo_link}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #0068ff; color: white; text-align: center; padding: 15px; border-radius: 10px; font-weight: bold; margin-top: 10px;">
                        💬 2. GỬI FILE VỪA TẢI QUA ZALO CHO HILTI
                    </div>
                </a>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Lỗi: {e}")
    else:
        st.warning("⚠️ Vui lòng điền Địa chỉ và Số điện thoại.")import streamlit as st
from fpdf import FPDF
import os

# --- HÀM TẠO PDF CHUYÊN NGHIỆP ---
def create_pdf(company, add, name_phone, tool, note):
    # Khởi tạo PDF khổ A4
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. Vẽ khung viền trang trí (Border)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(150, 150, 150) # Màu đỏ Hilti cho khung
    pdf.rect(7, 7, 196, 283) # Khung ngoài
    pdf.set_line_width(0.2)
    pdf.rect(8, 8, 194, 281) # Khung trong tạo hiệu ứng viền đôi

    # 2. Cài đặt Font
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Vietnamese', '', font_path)
        pdf.set_font('Vietnamese', size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    # 3. Tiêu đề
    pdf.ln(10)
    pdf.set_text_color(220, 0, 0)
    pdf.set_font('Vietnamese', size=22)
    pdf.cell(0, 15, txt="BIÊN BẢN NHẬN MÁY", ln=True, align='C')
    
    # Dòng kẻ trang trí dưới tiêu đề
    pdf.set_draw_color(150, 150, 150)
    pdf.line(70, 32, 140, 32)
    pdf.ln(15)

    # 4. Nội dung thông tin (Bố cục dạng bảng)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Vietnamese', size=12)
    
    def add_info_row(label, value):
        pdf.set_font('Vietnamese', size=11)
        pdf.set_text_color(100, 100, 100) # Màu xám cho nhãn
        pdf.cell(50, 10, txt=f"{label}:", border='B', ln=0)
        pdf.set_text_color(0, 0, 0) # Màu đen cho giá trị
        pdf.set_font('Vietnamese', size=12)
        pdf.cell(0, 10, txt=f" {value}", border='B', ln=True)
        pdf.ln(2)

    add_info_row("Tên đơn vị/Công ty", company)
    add_info_row("Địa chỉ giao nhận", add)
    add_info_row("Người gửi & Số ĐT", name_phone)
    add_info_row("Thiết bị & Số Seri", tool)
    add_info_row("Tình trạng máy", note)

    # 5. Phần tình trạng máy (Khung ghi chú lớn)
    #pdf.ln(5)
    #pdf.set_font('Vietnamese', size=12)
    #pdf.set_fill_color(240, 240, 240)
    #pdf.cell(0, 10, txt=" Tình trạng máy khi tiếp nhận:", ln=True, fill=True)
    #pdf.set_font('Vietnamese', size=11)
    #pdf.multi_cell(0, 10, txt=note, border=1)

    # 6. Phần chữ ký
#    pdf.ln(25)
#    pdf.set_font('Vietnamese', size=12)
#    pdf.cell(95, 10, txt="ĐẠI DIỆN KHÁCH HÀNG", ln=0, align='C')
#    pdf.cell(95, 10, txt="NGƯỜI NHẬN MÁY", ln=1, align='C')
#    pdf.set_font('Vietnamese', size=10)
#    pdf.set_text_color(150, 150, 150)
#    pdf.cell(95, 10, txt="(Ký và ghi rõ họ tên)", ln=0, align='C')
#    pdf.cell(95, 10, txt="(Ký và ghi rõ họ tên)", ln=1, align='C')

    return pdf.output()

# --- GIAO DIỆN WEB STREAMLIT (LÀM ĐẸP BẰNG CSS) ---
st.set_page_config(page_title="Hilti Service - Tiếp Nhận Máy", page_icon="🔧")

# CSS để thay đổi giao diện theo tông đỏ-đen
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        width: 100%;
        background-color: #dd0000;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 15px;
        font-size: 18px;
    }
    .stButton>button:hover { background-color: #ff3333; color: white; border: none; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    </style>
    """, unsafe_allow_html=True)

# Hiển thị Logo (Nếu bạn đã tải file logo.png lên GitHub)
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.title("🔴 HILTI TOOL SERVICE CENTER")

st.subheader("BIÊN BẢN NHẬN MÁY")
st.write("Vui lòng điền thông tin máy cần bảo hành/sửa chữa.")

# Form nhập liệu
with st.container():
    company = st.text_input("🏢 Tên Công Ty:")
    add = st.text_input("📍 Địa chỉ nhận và trả máy:")
    name_phone = st.text_input("👤 Người gửi và Số điện thoại:")
    tool = st.text_input("🛠️ Tên máy và số Seri:")
    note = st.text_area("⚠️ Tình trạng hư hỏng của máy:")

st.markdown("---")

if st.button("XÁC NHẬN & TẠO PHIẾU"):
    if add and name_phone:
        # Bảng tóm tắt hiển thị đẹp mắt
        st.success("✅ Thông tin đã được ghi nhận!")
        with st.expander("👉 NHẤN VÀO ĐÂY ĐỂ XEM TÓM TẮT", expanded=True):
            st.write(f"**Công ty:** {company}")
            st.write(f"**Khách hàng:** {name_phone}")
            st.write(f"**Địa chỉ:** {add}")
            st.write(f"**Thiết bị:** {tool}")
            st.write(f"**Tình trạng:** {note}")
        
        try:
            pdf_data = create_pdf(company, add, name_phone, tool, note)
            st.download_button(
                label="📥 TẢI BIÊN BẢN PDF",
                data=bytes(pdf_data),
                file_name=f"BBNM_{company}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Lỗi tạo PDF: {e}")
    else:
        st.warning("⚠️ Vui lòng điền ít nhất Địa chỉ và Số điện thoại liên lạc.")