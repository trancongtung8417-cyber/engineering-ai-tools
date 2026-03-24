import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json
import os
import tempfile
from io import BytesIO

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
# Hilti red square favicon as SVG data URI
FAVICON_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='14' fill='%23CC0000'/%3E%3Ctext x='50' y='68' font-family='Arial Black,sans-serif' font-size='52' font-weight='900' fill='white' text-anchor='middle' letter-spacing='-2'%3EHILTI%3C/text%3E%3C/svg%3E"

st.set_page_config(
    page_title="Hilti – Biên Bản Nhận Máy",
    page_icon=FAVICON_SVG,
    layout="centered",
    menu_items={}          # removes the ⋮ menu entirely
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

/* ── Hide ALL Streamlit chrome ── */
#MainMenu { visibility: hidden !important; display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { visibility: hidden !important; display: none !important; }
/* Fork / GitHub ribbon */
a[href*="github"] { display: none !important; }
/* Streamlit crown watermark */
.viewerBadge_container__1QSob,
.viewerBadge_link__1S137,
[data-testid="stDecoration"],
#stDecoration,
.decoration { display: none !important; }
/* Top toolbar (Deploy, Share, Star) */
[data-testid="stToolbar"],
.stToolbar,
[class*="toolbar"] { display: none !important; }
/* Remove top padding left by hidden header */
.block-container { padding-top: 2rem !important; }

/* Header banner */
.hilti-header {
    background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 6px 24px rgba(204,0,0,0.25);
}
.hilti-header h1 {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    color: white;
    margin: 0;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.hilti-header p {
    color: rgba(255,255,255,0.85);
    margin: 4px 0 0 0;
    font-size: 0.95rem;
}
.hilti-logo {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 2.8rem;
    color: white;
    background: rgba(255,255,255,0.15);
    padding: 6px 18px;
    border-radius: 8px;
    letter-spacing: 3px;
}

/* Section cards */
.section-card {
    background: #FAFAFA;
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 18px;
}
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #CC0000;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #CC0000;
}

/* Result card */
.result-card {
    background: white;
    border: 2px solid #CC0000;
    border-radius: 12px;
    padding: 32px 36px;
    margin-top: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.result-header {
    text-align: center;
    border-bottom: 2px solid #CC0000;
    padding-bottom: 16px;
    margin-bottom: 20px;
}
.result-header .brand {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #CC0000;
    letter-spacing: 2px;
}
.result-header .doc-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #222;
    margin: 4px 0;
}
.result-header .doc-date {
    color: #888;
    font-size: 0.9rem;
}
.info-row {
    display: flex;
    margin-bottom: 10px;
    font-size: 0.95rem;
}
.info-label {
    font-weight: 600;
    color: #555;
    min-width: 180px;
}
.info-value {
    color: #222;
    flex: 1;
}
.device-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
    font-size: 0.9rem;
}
.device-table th {
    background: #CC0000;
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-family: 'Barlow Condensed', sans-serif;
    letter-spacing: 0.5px;
}
.device-table td {
    padding: 9px 12px;
    border-bottom: 1px solid #EBEBEB;
    color: #333;
}
.device-table tr:nth-child(even) td {
    background: #FFF5F5;
}
.sign-area {
    display: flex;
    justify-content: space-between;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px dashed #DDD;
}
.sign-box {
    text-align: center;
    width: 45%;
}
.sign-box .sign-title {
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
}
.sign-box .sign-space {
    height: 60px;
    border-bottom: 1px solid #333;
    margin: 8px 0;
}
.badge-success {
    background: #D4EDDA;
    color: #155724;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

/* Streamlit overrides */
div.stButton > button {
    background: #CC0000 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 1px !important;
    padding: 10px 28px !important;
    width: 100%;
    transition: all 0.2s;
}
div.stButton > button:hover {
    background: #AA0000 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(204,0,0,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE INIT ────────────────────────────────────────────────────────────
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # Load from Streamlit secrets
        firebase_config = dict(st.secrets["firebase"])
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(firebase_config, f)
            tmp_path = f.name
        cred = credentials.Certificate(tmp_path)
        firebase_admin.initialize_app(cred)
        os.unlink(tmp_path)
    return firestore.client(prefer_rest=True)

try:
    db = init_firebase()
    firebase_ok = True
except Exception as e:
    firebase_ok = False
    firebase_error = str(e)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hilti-header">
    <div class="hilti-logo">HILTI</div>
    <div>
        <h1>Biên Bản Nhận Máy</h1>
        <p>Vui lòng điền đầy đủ thông tin bên dưới</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not firebase_ok:
    st.error(f"⚠️ Firebase chưa kết nối. Kiểm tra cấu hình Secrets.\n\n`{firebase_error}`")

# ─── FORM ─────────────────────────────────────────────────────────────────────
with st.form("bien_ban_form", clear_on_submit=False):

    st.markdown('<div class="section-card"><div class="section-title">📋 Thông Tin Khách Hàng</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        cong_ty = st.text_input("🏢 Công ty *", placeholder="Tên công ty / cá nhân")
        nguoi_gui = st.text_input("👤 Người gửi *", placeholder="Họ và tên")
    with col2:
        dia_chi = st.text_input("📍 Địa chỉ giao nhận *", placeholder="Địa chỉ cụ thể")
        so_dt = st.text_input("📞 Số điện thoại *", placeholder="0xxx xxx xxx")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">🔧 Thông Tin Thiết Bị</div>', unsafe_allow_html=True)

    # Dynamic device rows
    so_luong = st.number_input("Số lượng thiết bị", min_value=1, max_value=10, value=1, step=1)

    tinh_trang_options = [
        "Không hoạt động",
        "Không khoan",
        "Không đục",
        "Không có lực",
        "Chổi than bị mòn",
        "Mất nguồn",
        "Rung bất thường",
        "Cháy motor",
        "Khác",
    ]

    devices = []
    for i in range(int(so_luong)):
        st.markdown(f"**Thiết bị {i+1}**")
        c1, c2, c3 = st.columns([2, 2, 3])
        with c1:
            ten_may = st.text_input(f"Tên máy", key=f"ten_{i}", placeholder="VD: TE 6-A36")
        with c2:
            so_seri = st.text_input(f"Số Seri", key=f"seri_{i}", placeholder="VD: 123456789")
        with c3:
            tinh_trang = st.selectbox(f"Tình trạng", tinh_trang_options, key=f"tt_{i}")
        ghi_chu = st.text_input(f"Ghi chú thêm", key=f"gc_{i}", placeholder="(tuỳ chọn)")
        devices.append({
            "ten_may": ten_may,
            "so_seri": so_seri,
            "tinh_trang": tinh_trang,
            "ghi_chu": ghi_chu,
        })
        if i < int(so_luong) - 1:
            st.divider()

    st.markdown('</div>', unsafe_allow_html=True)

    ghi_chu_chung = st.text_area("📝 Ghi chú chung", placeholder="Ghi chú thêm về lần tiếp nhận này (nếu có)...")

    submitted = st.form_submit_button("✅ GỬI BIÊN BẢN")

# ─── RESULT ───────────────────────────────────────────────────────────────────
if submitted:
    errors = []
    if not cong_ty.strip(): errors.append("Công ty")
    if not dia_chi.strip(): errors.append("Địa chỉ giao nhận")
    if not nguoi_gui.strip(): errors.append("Người gửi")
    if not so_dt.strip(): errors.append("Số điện thoại")

    if errors:
        st.error(f"⚠️ Vui lòng điền: **{', '.join(errors)}**")
    else:
        now = datetime.now()
        ma_bb = f"BB{now.strftime('%Y%m%d%H%M%S')}"

        record = {
            "ma_bien_ban": ma_bb,
            "ngay_tao": now.isoformat(),
            "ngay_hien_thi": now.strftime("%d/%m/%Y %H:%M"),
            "cong_ty": cong_ty.strip(),
            "dia_chi": dia_chi.strip(),
            "nguoi_gui": nguoi_gui.strip(),
            "so_dt": so_dt.strip(),
            "ghi_chu_chung": ghi_chu_chung.strip(),
            "thiet_bi": devices,
        }

        # Save to Firebase
        if firebase_ok:
            try:
                db.collection("bien_ban_nhan_may").document(ma_bb).set(record)
                firebase_saved = True
            except Exception as e:
                firebase_saved = False
                firebase_save_err = str(e)
        else:
            firebase_saved = False

        # Build device rows HTML
        device_rows = ""
        for idx, d in enumerate(devices, 1):
            ten = d["ten_may"] or f"Máy {idx}"
            seri = d["so_seri"] or "—"
            tt = d["tinh_trang"]
            gc = d["ghi_chu"] or "—"
            device_rows += f"""
            <tr>
                <td style="font-weight:600">{idx}</td>
                <td>{ten}</td>
                <td>{seri}</td>
                <td><span style="color:#CC0000;font-weight:600">{tt}</span></td>
                <td>{gc}</td>
            </tr>
            """

        save_status = (
            '<span class="badge-success">✓ Đã lưu Firebase</span>'
            if firebase_saved else
            '<span style="background:#fff3cd;color:#856404;padding:4px 12px;border-radius:20px;font-size:0.82rem;font-weight:600">⚠ Lưu cục bộ</span>'
        )

        # Render result card
        st.markdown(f"""
        <div class="result-card" id="bien-ban-result">
            <div class="result-header">
                <div class="brand">HILTI</div>
                <div class="doc-title">BIÊN BẢN NHẬN MÁY</div>
                <div class="doc-date">Ngày: {now.strftime('%d tháng %m năm %Y')} &nbsp;|&nbsp; Mã BB: <strong>{ma_bb}</strong></div>
            </div>

            <div class="info-row"><span class="info-label">🏢 Công ty</span><span class="info-value">{record['cong_ty']}</span></div>
            <div class="info-row"><span class="info-label">📍 Địa chỉ giao nhận</span><span class="info-value">{record['dia_chi']}</span></div>
            <div class="info-row"><span class="info-label">👤 Người gửi</span><span class="info-value">{record['nguoi_gui']}</span></div>
            <div class="info-row"><span class="info-label">📞 Số điện thoại</span><span class="info-value">{record['so_dt']}</span></div>

            <br>
            <div class="section-title" style="font-size:1rem">🔧 Danh Sách Thiết Bị</div>
            <table class="device-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Tên Máy</th>
                        <th>Số Seri</th>
                        <th>Tình Trạng</th>
                        <th>Ghi Chú</th>
                    </tr>
                </thead>
                <tbody>
                    {device_rows}
                </tbody>
            </table>

            {"<br><div class='info-row'><span class='info-label'>📝 Ghi chú chung</span><span class='info-value'>" + record['ghi_chu_chung'] + "</span></div>" if record['ghi_chu_chung'] else ""}

            <div class="sign-area">
                <div class="sign-box">
                    <div class="sign-title">Người Gửi</div>
                    <div class="sign-space"></div>
                    <div style="font-size:0.85rem;color:#888">(Ký và ghi rõ họ tên)</div>
                    <div style="font-weight:600;margin-top:4px">{record['nguoi_gui']}</div>
                </div>
                <div class="sign-box">
                    <div class="sign-title">Nhân Viên Hilti Tiếp Nhận</div>
                    <div class="sign-space"></div>
                    <div style="font-size:0.85rem;color:#888">(Ký và ghi rõ họ tên)</div>
                </div>
            </div>

            <div style="text-align:right;margin-top:16px;font-size:0.82rem;color:#AAA">
                {save_status}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.success("🎉 Biên bản đã được tạo! Vui lòng **chụp màn hình** hoặc tải file JSON bên dưới để gửi qua Zalo.")

        # Download JSON
        json_bytes = json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            label="⬇️ Tải Biên Bản (JSON)",
            data=json_bytes,
            file_name=f"{ma_bb}.json",
            mime="application/json",
        )

        if not firebase_saved and firebase_ok:
            st.warning(f"Firebase lỗi: {firebase_save_err}")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#AAA;font-size:0.8rem'>Hilti Vietnam · Hệ thống Biên Bản Nhận Máy</div>",
    unsafe_allow_html=True,
)
