import streamlit as st
from fpdf import FPDF
import os

def create_pdf(name, phone, note):
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
    pdf.cell(200, 10, txt="THÔNG TIN ĐĂNG KÝ HILTI", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Họ tên: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Số điện thoại: {phone}", ln=True)
    pdf.ln(5)
    pdf.write(10, f"Yêu cầu:\n{note}")
    
    return pdf.output()

st.set_page_config(page_title="Form Thông Tin", page_icon="📝")

st.title("📝 Phiếu Cung Cấp Thông Tin")
st.write("Vui lòng điền thông tin, hệ thống sẽ tạo phiếu gửi cho chúng tôi.")

# Phần nhập liệu
with st.container():
    name = st.text_input("Họ và tên của bạn:")
    phone = st.text_input("Số điện thoại liên lạc:")
    note = st.text_area("Nội dung chi tiết (nếu có):")

if st.button("XÁC NHẬN & TẠO PHIẾU"):
    if name and phone:
        # 1. Hiển thị bảng tóm tắt để khách chụp màn hình (Dành cho khách thích nhanh)
        st.markdown("---")
        st.subheader("📌 BẢN TÓM TẮT THÔNG TIN")
        st.info(f"**Họ tên:** {name}  \n**Số điện thoại:** {phone}  \n**Yêu cầu:** {note}")
        st.write("👉 *Bạn có thể chụp ảnh màn hình bảng trên để gửi qua Zalo cho nhanh!*")

        # 2. Tạo nút tải PDF (Dành cho khách thích chuyên nghiệp)
        try:
            pdf_data = create_pdf(name, phone, note)
            st.download_button(
                label="📥 TẢI FILE PDF CHÍNH THỨC",
                data=bytes(pdf_data),
                file_name=f"YeuCau_{name}.pdf",
                mime="application/pdf",
                help="Bấm vào đây để lưu file PDF chất lượng cao"
            )
        except Exception as e:
            st.error(f"Lỗi tạo PDF: {e}")
    else:
        st.warning("⚠️ Vui lòng nhập Tên và Số điện thoại trước khi bấm nút.")