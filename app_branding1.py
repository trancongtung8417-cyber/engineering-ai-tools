"""
=============================================================
  app_branding.py  –  Thêm vào đầu file app chính của bạn
=============================================================
Cách dùng:
  1. Copy file này vào thư mục dự án của bạn.
  2. Trong file app chính, thêm:
       from app_branding import setup_page
       setup_page()          # ← gọi ngay dòng đầu tiên sau import
  3. Đổi APP_NAME, LOGO_URL, ACCENT_COLOR bên dưới cho phù hợp.
=============================================================
"""

import streamlit as st
import time

# ── Tuỳ chỉnh tại đây ────────────────────────────────────────
APP_NAME    = "HILTI"                         # Tên hiện trên tab trình duyệt
APP_TAGLINE = "Making Construction Better"  # Dòng phụ trên splash screen
LOGO_URL    = "https://i.postimg.cc/MKLRmf8Q/hilti-logo.png"
# Hoặc dùng emoji làm favicon nếu chưa có file ảnh:
PAGE_ICON   = "🚀"                            # Hiện trên tab trình duyệt
ACCENT_COLOR = "#4F46E5"                      # Màu chủ đạo (indigo)
SPLASH_SECONDS = 2.2                          # Thời gian hiện splash screen
# ─────────────────────────────────────────────────────────────


def setup_page():
    """
    Gọi hàm này một lần duy nhất ở đầu script Streamlit.
    Nó sẽ:
      • Đặt tên tab + favicon
      • Hiện splash screen với logo + progress bar
      • Ẩn menu mặc định của Streamlit (trông pro hơn)
    """

    # 1. Cấu hình trang ─────────────────────────────────────
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=PAGE_ICON,         # Dùng PAGE_ICON (emoji) hoặc đường dẫn ảnh .png/.ico
        layout="centered",
        initial_sidebar_state="auto",
    )

    # 2. Ẩn watermark Streamlit + hamburger menu ────────────
    st.markdown(
        """
        <style>
        #MainMenu, footer, header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 3. Splash screen (chỉ hiện lần đầu mỗi session) ───────
    if "splashed" not in st.session_state:
        st.session_state.splashed = False

    if not st.session_state.splashed:
        _show_splash()
        st.session_state.splashed = True


# ── Nội bộ ───────────────────────────────────────────────────

def _show_splash():
    """Hiển thị màn hình chờ toàn trang với logo + thanh tiến trình."""

    splash_css = f"""
    <style>
    /* --- Overlay toàn màn hình --- */
    #splash-overlay {{
        position: fixed;
        inset: 0;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        animation: fadeOut 0.6s ease {SPLASH_SECONDS}s forwards;
    }}

    /* --- Logo / ảnh --- */
    #splash-logo {{
        width: 120px;
        height: 120px;
        border-radius: 24px;
        object-fit: contain;
        box-shadow: 0 0 60px {ACCENT_COLOR}55;
        animation: popIn 0.5s cubic-bezier(.175,.885,.32,1.275) 0.2s both;
    }}

    /* --- Tên app --- */
    #splash-title {{
        margin-top: 28px;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff;
        font-family: 'Segoe UI', system-ui, sans-serif;
        animation: slideUp 0.5s ease 0.4s both;
    }}

    /* --- Tagline --- */
    #splash-tag {{
        margin-top: 8px;
        font-size: 0.95rem;
        color: #888;
        font-family: 'Segoe UI', system-ui, sans-serif;
        animation: slideUp 0.5s ease 0.55s both;
    }}

    /* --- Thanh tiến trình --- */
    #splash-bar-wrap {{
        margin-top: 48px;
        width: 220px;
        height: 4px;
        background: #ffffff18;
        border-radius: 99px;
        overflow: hidden;
        animation: slideUp 0.4s ease 0.6s both;
    }}
    #splash-bar {{
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, {ACCENT_COLOR}, #818cf8);
        border-radius: 99px;
        animation: fillBar {SPLASH_SECONDS}s cubic-bezier(.4,0,.2,1) 0.3s forwards;
    }}

    /* --- Keyframes --- */
    @keyframes popIn {{
        from {{ transform: scale(0.6); opacity: 0; }}
        to   {{ transform: scale(1);   opacity: 1; }}
    }}
    @keyframes slideUp {{
        from {{ transform: translateY(16px); opacity: 0; }}
        to   {{ transform: translateY(0);    opacity: 1; }}
    }}
    @keyframes fillBar {{
        from {{ width: 0%; }}
        to   {{ width: 100%; }}
    }}
    @keyframes fadeOut {{
        to {{ opacity: 0; pointer-events: none; }}
    }}
    </style>

    <div id="splash-overlay">
        <img id="splash-logo" src="{LOGO_URL}" alt="Logo"
             onerror="this.outerHTML='<div style=\'width:120px;height:120px;border-radius:24px;background:linear-gradient(135deg,{ACCENT_COLOR},{ACCENT_COLOR}88);display:flex;align-items:center;justify-content:center;font-size:3rem;\'>🚀</div>'" />
        <div id="splash-title">{APP_NAME}</div>
        <div id="splash-tag">{APP_TAGLINE}</div>
        <div id="splash-bar-wrap">
            <div id="splash-bar"></div>
        </div>
    </div>
    """

    placeholder = st.empty()
    placeholder.markdown(splash_css, unsafe_allow_html=True)

    # Giữ splash đúng thời gian rồi xoá
    time.sleep(SPLASH_SECONDS + 0.6)
    placeholder.empty()


# ── Chạy thử độc lập ─────────────────────────────────────────
if __name__ == "__main__":
    setup_page()
    st.title(f"Chào mừng đến {APP_NAME} 👋")
    st.write("Splash screen và icon đã được cấu hình thành công!")
