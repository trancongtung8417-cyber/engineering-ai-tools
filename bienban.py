import streamlit as st
from fpdf import FPDF
import os
import base64
import json

# ============================================================
# PWA + ẨN UI STREAMLIT (Header, Deploy, Toolbar, Footer)
# ============================================================

def get_pwa_html():
    """
    Trả về HTML để:
    1. Đăng ký Service Worker (PWA offline-ready)
    2. Inject <link rel="manifest"> cho Web App Manifest
    3. Ẩn toàn bộ UI mặc định của Streamlit
    """
    # Web App Manifest dạng JSON (inline base64)
    manifest = {
        "name": "Hilti Tool Service",
        "short_name": "Hilti Service",
        "description": "Biên bản nhận máy - Hilti Tool Service Center",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#dd0000",
        "theme_color": "#dd0000",
        "orientation": "portrait",
        "icons": [
            {
                "src": "https://i.postimg.cc/PJWDDV3g/hilti-logo.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/1585/1585444.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }

    # Encode manifest sang base64 để nhúng inline (không cần file server)
    manifest_json = json.dumps(manifest)
    manifest_b64 = base64.b64encode(manifest_json.encode()).decode()

    # Service Worker đơn giản: cache-first strategy
    sw_script = """
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => clients.claim());
self.addEventListener('fetch', e => {
    e.respondWith(
        caches.open('hilti-v1').then(cache =>
            cache.match(e.request).then(r => r || fetch(e.request))
        )
    );
});
"""
    sw_b64 = base64.b64encode(sw_script.encode()).decode()

    html = f"""
<head>
    <!-- PWA Manifest (inline base64) -->
    <link rel="manifest" href="data:application/json;base64,{manifest_b64}">

    <!-- iOS PWA Meta Tags -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Hilti Service">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/1585/1585444.png">

    <!-- Android / Theme -->
    <meta name="theme-color" content="#dd0000">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="application-name" content="Hilti Service">
</head>

<script>
// --- Đăng ký Service Worker từ blob ---
(function() {{
    if ('serviceWorker' in navigator) {{
        const swCode = atob("{sw_b64}");
        const blob = new Blob([swCode], {{ type: 'application/javascript' }});
        const swUrl = URL.createObjectURL(blob);
        navigator.serviceWorker.register(swUrl)
            .then(() => console.log('✅ PWA Service Worker đã đăng ký'))
            .catch(err => console.warn('SW error:', err));
    }}

    // --- Ẩn các phần tử UI của Streamlit ---
    function hideStreamlitUI() {{
        const css = `
            /* Ẩn header (Fork, GitHub, Menu 3 chấm) */
            header[data-testid="stHeader"] {{
                display: none !important;
            }}

            /* Ẩn nút Deploy / Crown đỏ */
            .stDeployButton,
            [data-testid="stDeployButton"],
            button[kind="deployButton"],
            [title="Deploy this app"],
            [data-testid="baseButton-deployButton"] {{
                display: none !important;
            }}

            /* Ẩn Toolbar góc dưới phải (logo Streamlit + running status) */
            [data-testid="stToolbar"],
            .viewerBadge_container__r5tak,
            .styles_viewerBadge__CvC9N,
            #MainMenu,
            footer,
            footer a,
            [data-testid="stStatusWidget"],
            .stStatusWidget {{
                display: none !important;
                visibility: hidden !important;
            }}

            /* Ẩn "Made with Streamlit" footer */
            .reportview-container .main footer {{
                display: none !important;
            }}

            /* Padding top vì không còn header */
            .block-container {{
                padding-top: 1.5rem !important;
            }}
        `;
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
    }}

    // Chạy ngay + chờ DOM render xong
    hideStreamlitUI();
    document.addEventListener('DOMContentLoaded', hideStreamlitUI);

    // Observer để bắt các phần tử lazy-render của Streamlit
    const observer = new MutationObserver(hideStreamlitUI);
    observer.observe(document.body || document.documentElement, {{
        childList: true,
        subtree: true
    }});

    // Dừng observer sau 10 giây để tiết kiệm tài nguyên
    setTimeout(() => observer.disconnect(), 10000);
}})();
</script>
"""
    return html

# Inject PWA + CSS ẩn UI vào Streamlit
st.set_page_config(
    page_title="Hilti Tool Service",
    page_icon="🔴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Nhúng PWA HTML vào trang
st.components.v1.html(get_pwa_html(), height=0)


# ============================================================
# HÀM TẠO PDF
# ============================================================
def create_pdf(company, add, name_phone, tool, note):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    pdf.set_line_width(0.5)
    pdf.set_draw_color(150, 150, 150)
    pdf.rect(7, 7, 196, 283)

    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=10, w=30)

    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Vietnamese', '', font_path)
        pdf.set_font('Vietnamese', size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    pdf.ln(20)
    pdf.set_text_color(220, 0, 0)
    pdf.set_font('Vietnamese', size=22)
    pdf.cell(0, 15, txt="BIÊN BẢN NHẬN MÁY", ln=True, align='C')
    pdf.ln(10)

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

    pdf.ln(5)
    pdf.set_font('Vietnamese', size=12)
    pdf.cell(0, 10, txt="Tình trạng máy (không hoạt động, không khoan, không đục...):", ln=True)
    pdf.set_font('Vietnamese', size=11)
    pdf.multi_cell(0, 10, txt=note, border=1)

    return pdf.output()


# ============================================================
# GIAO DIỆN STREAMLIT
# ============================================================
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

if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.title("🔴 HILTI TOOL SERVICE CENTER")

st.subheader("BIÊN BẢN NHẬN MÁY")
st.write("Vui lòng điền thông tin máy cần bảo hành/sửa chữa.")

with st.container():
    company = st.text_input("🏢 Tên Công Ty:")
    add = st.text_input("📍 Địa chỉ nhận và trả máy:")
    name_phone = st.text_input("👤 Người gửi và Số điện thoại:")
    tool = st.text_input("🛠️ Tên máy và số Seri:")
    note = st.text_area("⚠️ Tình trạng hư hỏng của máy (không hoạt động, không khoan, không đục...):")

st.markdown("---")

if st.button("XÁC NHẬN & TẠO PHIẾU"):
    if add and name_phone:
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
