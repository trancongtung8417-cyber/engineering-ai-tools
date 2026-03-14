import streamlit as st
from fpdf import FPDF
import os

def create_pdf(company, add, name_phone, tool, note):
    pdf = FPDF()
    pdf.add_page()
    
    # ĐƯỜNG DẪN ĐẾN FILE FONT BẠN VỪA TẢI LÊN
    font_path = "Roboto-Regular.ttf" 
    
    if os.path.exists(font_path):
        # Đăng ký font với tên 'Vietnamese'
        pdf.add_font('Vietnamese', '', font_path)
        pdf.set_font('Vietnamese', size=14)
    else:
        # Nếu không có font, phần mềm sẽ báo lỗi này để bạn biết
        st.error("Không tìm thấy file Roboto-Regular.ttf trên GitHub!")
        pdf.set_font("Helvetica", size=14)
    
    # Vẽ nội dung
    pdf.set_text_color(220, 0, 0) # Màu đỏ Hilti
    pdf.cell(200, 10, txt="BIÊN BẢN NHẬN MÁY", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Công ty: {company}", ln=True)
    pdf.cell(200, 10, txt=f"Địa chỉ: {add}", ln=True)
    pdf.cell(200, 10, txt=f"Tên và SDT: {name_phone}", ln=True)
    pdf.cell(200, 10, txt=f"Thông tin máy:** {tool}", ln=True)
    pdf.ln(5)
    pdf.write(10, f"Tình trạng máy:\n{note}")
    
    return pdf.output()

st.set_page_config(page_title="Form Thông Tin", page_icon="📝")

st.title("📝 Phiếu Cung Cấp Thông Tin")
st.write("Vui lòng điền thông tin, hệ thống sẽ tạo phiếu gửi cho chúng tôi.")

# Phần nhập liệu
with st.container():
    company = st.text_input("Tên Công Ty:")
    add = st.text_input("Địa chỉ nhận và trả máy:")
    name_phone = st.text_input("Tên và số điện thoại:")
    tool = st.text_input("Tên máy và số Seri:")
    note = st.text_area("Tình trạng máy (không hoạt động, không khoan, không đục...):")

if st.button("XÁC NHẬN & TẠO BIÊN BẢN"):
    if add and name_phone:
        # 1. Hiển thị bảng tóm tắt để khách chụp màn hình (Dành cho khách thích nhanh)
        st.markdown("---")
        st.subheader("📌 BẢN TÓM TẮT THÔNG TIN")
        st.info(f"**Công ty:** {company}  \n**Địa chỉ:** {add}  \n**Tên và SDT:** {name_phone}  \n**Thông tin máy:** {tool}  \n**Tình trạng máy:** {note}  ")
        st.write("👉 *Bạn có thể chụp ảnh màn hình bảng tóm tắt trên!*")

        # 2. Tạo nút tải PDF (Dành cho khách thích chuyên nghiệp)
        try:
            pdf_data = create_pdf(company, add, name_phone, tool, note)
            st.download_button(
                label="📥 TẢI FILE PDF CHÍNH THỨC",
                data=bytes(pdf_data),
                file_name=f"BIÊN BẢN NHẬN MÁY - {company}.pdf",
                mime="application/pdf",
                help="Bấm vào đây để lưu file PDF chất lượng cao"
            )
        except Exception as e:
            st.error(f"Lỗi tạo PDF: {e}")
    else:
        st.warning("⚠️ Vui lòng nhập Tên và Số điện thoại trước khi bấm nút.")