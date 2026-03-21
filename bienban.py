import streamlit as st
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