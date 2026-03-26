import streamlit as st
import time
from supabase import create_client, Client
from fpdf import FPDF
import os

# ╔══════════════════════════════╗
# ║        ⚙️  CONFIG           ║
# ╚══════════════════════════════╝
APP_NAME        = "Hilti"
APP_SHORT_NAME  = "Hilti"
TAGLINE         = "Performance. Passion. Integrity. Teamwork."
THEME_COLOR     = "#D2001A"          # Đỏ Hilti chính xác
THEME_DARK      = "#A50014"          # Đỏ tối hơn cho gradient
BG_COLOR        = "#ffffff"

GITHUB_USER     = "trancongtung8417-cyber"        # ← ĐỔI THÀNH USERNAME GITHUB CỦA BẠN
GITHUB_REPO     = "engineering-ai-tools"        # ← ĐỔI THÀNH TÊN REPO CỦA BẠN
GITHUB_BRANCH   = "main"
LOGO_FILE       = "hilti_logo.png"   # tên file logo trong assets/

_BASE     = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/assets"
LOGO_URL  = f"{_BASE}/{LOGO_FILE}"

SPLASH_DURATION = 2.2   # giây


# ╔══════════════════════════════════════╗
# ║  1. PAGE CONFIG  (trước mọi st.*)   ║
# ╚══════════════════════════════════════╝
st.set_page_config(
    page_title=APP_NAME,
    page_icon=LOGO_URL,          # favicon tab trình duyệt
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ╔══════════════════════════════════════╗
# ║  2. PWA MANIFEST  → đổi icon điện   ║
# ║     thoại khi Add to Home Screen    ║
# ╚══════════════════════════════════════╝
import urllib.parse
manifest = {
    "name": APP_NAME,
    "short_name": APP_SHORT_NAME,
    "description": TAGLINE,
    "start_url": "/",
    "display": "standalone",
    "background_color": BG_COLOR,
    "theme_color": THEME_COLOR,
    "orientation": "portrait",
    "icons": [
        {"src": LOGO_URL, "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": LOGO_URL, "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}
import json as _json
_manifest_str = urllib.parse.quote(_json.dumps(manifest), safe="")

st.markdown(
    f"""
    <link rel="manifest"
          href="data:application/manifest+json,{_manifest_str}">
    <meta name="mobile-web-app-capable"       content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title"   content="{APP_SHORT_NAME}">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color"                  content="{THEME_COLOR}">
    <link rel="apple-touch-icon"              href="{LOGO_URL}">
    
    
    <style>
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

    """,
    unsafe_allow_html=True,
)


# ╔══════════════════════════════════════╗
# ║  3. GLOBAL CSS                       ║
# ╚══════════════════════════════════════╝
st.markdown(
    f"""
    <style>
    /* Ẩn watermark Streamlit */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0.5rem !important; max-width: 1100px; }}

    /* Font */
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    }}

    /* Nút chính */
    .stButton > button {{
        background: {THEME_COLOR} !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
        transition: background 0.2s, transform 0.15s, box-shadow 0.15s;
    }}
    .stButton > button:hover {{
        background: {THEME_DARK} !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px {THEME_COLOR}44 !important;
    }}

    /* Metric */
    [data-testid="metric-container"] {{
        background: #fff;
        border: 1px solid #f0f0f0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px #0000000a;
    }}
    [data-testid="stMetricValue"] {{
        color: {THEME_COLOR} !important;
        font-weight: 800 !important;
        font-size: 1.7rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ╔══════════════════════════════════════╗
# ║  4. SPLASH SCREEN                    ║
# ╚══════════════════════════════════════╝
if "splashed" not in st.session_state:
    st.session_state.splashed = False

if not st.session_state.splashed:
    _splash = st.empty()
    _splash.markdown(
        f"""
        <style>
        #sp {{
            position:fixed; inset:0; z-index:99999;
            background: linear-gradient(160deg, {THEME_COLOR} 0%, {THEME_DARK} 100%);
            display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            animation: spOut 0.55s ease {SPLASH_DURATION}s forwards;
        }}
        #sp-logo {{
            width:130px; height:130px; object-fit:contain;
            filter: drop-shadow(0 8px 32px #00000055);
            animation: spPop 0.6s cubic-bezier(.175,.885,.32,1.275) 0.1s both;
        }}
        #sp-fallback {{
            width:130px; height:130px; display:none;
            align-items:center; justify-content:center;
            background: white; border-radius: 20px;
            font-size:3rem;
            filter: drop-shadow(0 8px 32px #00000055);
            animation: spPop 0.6s cubic-bezier(.175,.885,.32,1.275) 0.1s both;
        }}
        #sp h1 {{
            color:#fff; font-size:2.8rem; font-weight:900;
            letter-spacing:3px; margin:22px 0 6px;
            animation: spUp 0.5s ease 0.35s both;
            text-transform: uppercase;
        }}
        #sp p {{
            color:#ffffff99; font-size:0.85rem; margin:0;
            animation: spUp 0.5s ease 0.5s both;
            text-align:center; max-width:300px; line-height:1.5;
        }}
        #sp .divider {{
            width:60px; height:3px; background:#fff;
            margin:18px 0; border-radius:99px;
            animation: spUp 0.4s ease 0.55s both;
        }}
        #sp .bar-wrap {{
            margin-top:36px; width:200px; height:3px;
            background:#ffffff33; border-radius:99px; overflow:hidden;
            animation: spUp 0.4s ease 0.6s both;
        }}
        #sp .bar {{
            height:100%; width:0%;
            background:#fff; border-radius:99px;
            animation: spFill {SPLASH_DURATION}s ease 0.25s forwards;
        }}
        @keyframes spPop {{
            from {{ transform:scale(0.4); opacity:0 }}
            to   {{ transform:scale(1);   opacity:1 }}
        }}
        @keyframes spUp {{
            from {{ transform:translateY(18px); opacity:0 }}
            to   {{ transform:translateY(0);    opacity:1 }}
        }}
        @keyframes spFill {{
            from {{ width:0% }} to {{ width:100% }}
        }}
        @keyframes spOut {{
            to {{ opacity:0; pointer-events:none }}
        }}
        </style>

        <div id="sp">
            <img id="sp-logo" src="{LOGO_URL}" alt="Hilti Logo"
                 onerror="this.style.display='none';
                          var f=document.getElementById('sp-fallback');
                          f.style.display='flex';">
            <div id="sp-fallback">🔧</div>
            <h1>HILTI</h1>
            <div class="divider"></div>
            <p>{TAGLINE}</p>
            <div class="bar-wrap"><div class="bar"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(SPLASH_DURATION + 0.55)
    _splash.empty()
    st.session_state.splashed = True


# ╔══════════════════════════════════════╗
# ║  5. HEADER                           ║
# ╚══════════════════════════════════════╝
st.markdown(
    f"""
    <div style="
        display:flex; align-items:center; gap:14px;
        background: linear-gradient(90deg, {THEME_COLOR} 0%, {THEME_DARK} 100%);
        padding:14px 24px; border-radius:12px;
        margin-bottom:1.4rem;
        box-shadow: 0 4px 20px {THEME_COLOR}44;
    ">
        <img src="{LOGO_URL}" width="46" height="46"
             style="object-fit:contain; filter:brightness(0) invert(1);"
             onerror="this.outerHTML='<span style=font-size:2rem;color:white>🔧</span>'">
        <div>
            <div style="font-size:1.4rem;font-weight:900;color:#fff;
                        letter-spacing:2px;text-transform:uppercase">HILTI</div>
            <div style="font-size:0.78rem;color:#ffffff99">{TAGLINE}</div>
        </div>
        <div style="margin-left:auto;color:#ffffff99;font-size:0.82rem">
            🔴 Online
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



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

# --- 2. KẾT NỐI SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Lỗi cấu hình Secrets: {e}")
    st.stop()

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