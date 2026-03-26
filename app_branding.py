"""
=============================================================
  app_branding.py – Đã tối ưu cho phong cách HILTI Gray
=============================================================
"""

import streamlit as st
import time

# ── Tuỳ chỉnh tại đây ────────────────────────────────────────
APP_NAME      = "HILTI"                          
APP_TAGLINE   = "Making Construction Better"  
LOGO_URL      = "https://i.postimg.cc/MKLRmf8Q/hilti-logo.png"
PAGE_ICON     = "🏗️"                            # Thay tên lửa bằng icon xây dựng
ACCENT_COLOR  = "#D1D5DB"                      # Màu xám nhạt chủ đạo bạn chọn
SPLASH_SECONDS = 2.2                          
# ─────────────────────────────────────────────────────────────

def setup_page():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=PAGE_ICON,
        layout="centered",
        initial_sidebar_state="auto",
    )

    # Ẩn menu mặc định
    st.markdown(
        """
        <style>
        #MainMenu, footer, header { visibility: hidden; }
        /* Tùy chỉnh màu các nút bấm mặc định của Streamlit sang màu xám/đỏ */
        .stButton>button {
            border-radius: 4px;
            border: 1px solid #D1D5DB;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "splashed" not in st.session_state:
        st.session_state.splashed = False

    if not st.session_state.splashed:
        _show_splash()
        st.session_state.splashed = True

def _show_splash():
    # Phối màu Splash Screen mới: Nền xám rất nhạt, chữ đen để chuyên nghiệp hơn
    splash_css = f"""
    <style>
    #splash-overlay {{
        position: fixed;
        inset: 0;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #F3F4F6; /* Nền xám sáng công nghiệp */
        animation: fadeOut 0.6s ease {SPLASH_SECONDS}s forwards;
    }}

    #splash-logo {{
        width: 150px; /* Tăng kích thước logo Hilti */
        height: auto;
        object-fit: contain;
        filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
        animation: popIn 0.5s cubic-bezier(.175,.885,.32,1.275) 0.2s both;
    }}

    #splash-title {{
        margin-top: 20px;
        font-size: 2.5rem;
        font-weight: 800;
        color: #111827; /* Chữ đen đậm */
        font-family: 'Segoe UI', Roboto, sans-serif;
        animation: slideUp 0.5s ease 0.4s both;
    }}

    #splash-tag {{
        margin-top: 5px;
        font-size: 1rem;
        color: #6B7280; /* Chữ xám phụ */
        letter-spacing: 1px;
        text-transform: uppercase;
        animation: slideUp 0.5s ease 0.55s both;
    }}

    #splash-bar-wrap {{
        margin-top: 40px;
        width: 250px;
        height: 3px;
        background: #E5E7EB;
        border-radius: 99px;
        overflow: hidden;
    }}
    #splash-bar {{
        height: 100%;
        width: 0%;
        background: #D21F3C; /* Điểm nhấn màu Đỏ Hilti ở thanh loading */
        animation: fillBar {SPLASH_SECONDS}s linear 0.3s forwards;
    }}

    @keyframes popIn {{ from {{ transform: scale(0.8); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
    @keyframes slideUp {{ from {{ transform: translateY(10px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
    @keyframes fillBar {{ from {{ width: 0%; }} to {{ width: 100%; }} }}
    @keyframes fadeOut {{ to {{ opacity: 0; pointer-events: none; }} }}
    </style>

    <div id="splash-overlay">
        <img id="splash-logo" src="{LOGO_URL}" alt="HILTI Logo"
             onerror="this.outerHTML='<div style=\'font-size:3rem;\'>{PAGE_ICON}</div>'" />
        <div id="splash-title">{APP_NAME}</div>
        <div id="splash-tag">{APP_TAGLINE}</div>
        <div id="splash-bar-wrap">
            <div id="splash-bar"></div>
        </div>
    </div>
    """

    placeholder = st.empty()
    placeholder.markdown(splash_css, unsafe_allow_html=True)
    time.sleep(SPLASH_SECONDS + 0.6)
    placeholder.empty()

if __name__ == "__main__":
    setup_page()
    st.title("Giao diện HILTI Modern Gray")
    st.info("Splash screen đã được làm mới với tông màu xám sáng và thanh load đỏ Hilti.")