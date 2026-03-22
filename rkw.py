import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, timedelta
from supabase import create_client, Client
import io

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RKW - Quản Lý Kho Hàng",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e9ecef;
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
        color: #495057;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d6efd !important;
        color: white !important;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-card h2 { color: #0d6efd; margin: 0; font-size: 2rem; }
    .metric-card p  { color: #6c757d; margin: 0; font-size: 0.85rem; }
    .section-header {
        background: linear-gradient(135deg, #0d6efd, #0a58ca);
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        margin: 16px 0 8px;
        font-weight: 700;
    }
    .dataframe { font-size: 13px; }
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ─── SUPABASE CONNECTION ────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url  = st.secrets["SUPABASE_URL"]
    key  = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def supabase_available():
    try:
        get_supabase()
        return True
    except Exception:
        return False

# ─── DEFAULT SEED DATA ─────────────────────────────────────────────────────────
DEFAULT_CONTAINERS = [
    {"ma_cont": "43.*/0326", "ma_hang": "FIP2Z0FR01.0016", "ten_hang": "Aldi Sued 1L+3L+6L",
     "ke_hoach": 1193, "nw": 8894, "ngay_bat_dau": "2026-02-11", "ngay_ket_thuc": "2026-02-26",
     "con_tru_kho_rkw": 0, "con_tru_kho_qmi": 0},
    {"ma_cont": "90.1/0625", "ma_hang": "FIP21RSS00.0077", "ten_hang": "Aldi IE 25L",
     "ke_hoach": 3092, "nw": 3996, "ngay_bat_dau": "2026-02-11", "ngay_ket_thuc": "2026-02-26",
     "con_tru_kho_rkw": 0, "con_tru_kho_qmi": 0},
]
DEFAULT_NHAP_XUAT_RKW = [
    {"ma_cont": "43.*/0326", "ngay": "2026-02-15", "ca1": 500, "ca2": 393, "nhap_qmi": 300, "xuat_cont": 700, "xuat_qmi": 208},
    {"ma_cont": "90.1/0625", "ngay": "2026-02-18", "ca1": 1500, "ca2": 1092, "nhap_qmi": 500, "xuat_cont": 2100, "xuat_qmi": 992},
]
DEFAULT_NHAP_XUAT_QMI = [
    {"ma_cont": "43.*/0326", "ngay": "2026-02-15", "ca1": 150, "ca2": 158, "nhap_l2": 600, "xuat_cont": 0, "xuat_l2": 100},
    {"ma_cont": "90.1/0625", "ngay": "2026-02-18", "ngay_etd_l1": "2026-03-01", "ngay_etd_l2": "2026-03-10",
     "ca1": 900, "ca2": 616, "nhap_l2": 500, "xuat_cont": 1500, "xuat_l2": 516},
]

# ─── SESSION STATE INIT ─────────────────────────────────────────────────────────
def init_state():
    if "containers" not in st.session_state:
        st.session_state.containers = DEFAULT_CONTAINERS.copy()
    if "nhap_xuat_rkw" not in st.session_state:
        st.session_state.nhap_xuat_rkw = DEFAULT_NHAP_XUAT_RKW.copy()
    if "nhap_xuat_qmi" not in st.session_state:
        st.session_state.nhap_xuat_qmi = DEFAULT_NHAP_XUAT_QMI.copy()

init_state()

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def get_df_containers():
    return pd.DataFrame(st.session_state.containers)

def calc_rkw(ma_cont):
    rows = [r for r in st.session_state.nhap_xuat_rkw if r["ma_cont"] == ma_cont]
    tong_nhap = sum(r.get("ca1",0)+r.get("ca2",0)+r.get("nhap_qmi",0) for r in rows)
    tong_xuat = sum(r.get("xuat_cont",0)+r.get("xuat_qmi",0) for r in rows)
    con = next((c for c in st.session_state.containers if c["ma_cont"]==ma_cont), {})
    con_tru = con.get("con_tru_kho_rkw", 0)
    return tong_nhap, tong_xuat, con_tru + tong_nhap - tong_xuat

def calc_qmi(ma_cont):
    rows = [r for r in st.session_state.nhap_xuat_qmi if r["ma_cont"] == ma_cont]
    tong_nhap = sum(r.get("ca1",0)+r.get("ca2",0)+r.get("nhap_l2",0) for r in rows)
    tong_xuat = sum(r.get("xuat_cont",0)+r.get("xuat_l2",0) for r in rows)
    con = next((c for c in st.session_state.containers if c["ma_cont"]==ma_cont), {})
    con_tru = con.get("con_tru_kho_qmi", 0)
    return tong_nhap, tong_xuat, con_tru + tong_nhap - tong_xuat

def ma_cont_list():
    return [c["ma_cont"] for c in st.session_state.containers]

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/RKW-Việt%20Nam-blue?style=for-the-badge", width=200)
    st.markdown("## ⚙️ Cài đặt")
    if supabase_available():
        st.success("✅ Supabase: Đã kết nối")
    else:
        st.warning("⚠️ Supabase: Chưa cấu hình\n(Dữ liệu lưu tạm trong session)")
    st.markdown("---")
    st.markdown("### 📦 Thêm Container Mới")
    with st.form("add_cont"):
        new_cont    = st.text_input("Mã Cont")
        new_ma_hang = st.text_input("Mã Hàng")
        new_ten_hang= st.text_input("Tên Hàng")
        new_ke_hoach= st.number_input("Kế Hoạch", min_value=0, value=0)
        new_nw      = st.number_input("NW (kg)", min_value=0.0, value=0.0)
        new_bd      = st.date_input("Ngày Bắt Đầu", value=date.today())
        new_kt      = st.date_input("Ngày Kết Thúc", value=date.today())
        submitted   = st.form_submit_button("➕ Thêm")
        if submitted and new_cont:
            if new_cont not in [c["ma_cont"] for c in st.session_state.containers]:
                st.session_state.containers.append({
                    "ma_cont": new_cont, "ma_hang": new_ma_hang,
                    "ten_hang": new_ten_hang, "ke_hoach": new_ke_hoach,
                    "nw": new_nw, "ngay_bat_dau": str(new_bd),
                    "ngay_ket_thuc": str(new_kt),
                    "con_tru_kho_rkw": 0, "con_tru_kho_qmi": 0,
                })
                st.success(f"Đã thêm: {new_cont}")
                st.rerun()
            else:
                st.error("Mã cont đã tồn tại!")

# ─── MAIN TABS ─────────────────────────────────────────────────────────────────
st.title("🏭 Hệ Thống Quản Lý Kho Hàng - RKW Việt Nam")
tab1, tab2, tab3, tab4 = st.tabs(["📦 Kho RKW", "🏪 Kho QMI", "📊 Kho Tổng", "📋 Báo Cáo"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: KHO RKW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📦 KHO RKW - Theo Dõi Nhập/Xuất</div>', unsafe_allow_html=True)

    df_c = get_df_containers()
    if df_c.empty:
        st.info("Chưa có container. Thêm từ sidebar.")
    else:
        # Summary metrics per container
        summary_rows = []
        for c in st.session_state.containers:
            mc = c["ma_cont"]
            t_nhap, t_xuat, t_ton = calc_rkw(mc)
            summary_rows.append({
                "Mã Cont": mc, "Mã Hàng": c["ma_hang"], "Tên Hàng": c["ten_hang"],
                "Kế Hoạch": c["ke_hoach"], "NW": c["nw"],
                "Ngày BD": c["ngay_bat_dau"], "Ngày KT": c["ngay_ket_thuc"],
                "Còn Trữ Kho": c["con_tru_kho_rkw"],
                "Tổng Nhập": t_nhap, "Tổng Xuất": t_xuat, "Tồn Cuối": t_ton,
            })
        df_sum = pd.DataFrame(summary_rows)
        st.dataframe(df_sum, use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng Nhập Toàn Bộ", f"{df_sum['Tổng Nhập'].sum():,}")
        col2.metric("Tổng Xuất Toàn Bộ", f"{df_sum['Tổng Xuất'].sum():,}")
        col3.metric("Tồn Cuối Toàn Bộ",  f"{df_sum['Tồn Cuối'].sum():,}")

    st.markdown('<div class="section-header">📥 Nhập Xuất Theo Ngày - Kho RKW</div>', unsafe_allow_html=True)

    # Form add daily entry RKW
    with st.expander("➕ Thêm Dữ Liệu Nhập/Xuất Ngày (Kho RKW)"):
        with st.form("add_nx_rkw"):
            c1, c2, c3 = st.columns(3)
            sel_cont = c1.selectbox("Mã Cont", ma_cont_list())
            sel_date = c2.date_input("Ngày", value=date.today())
            c3.write("")
            r1, r2, r3, r4, r5 = st.columns(5)
            v_ca1      = r1.number_input("Ca 1",       min_value=0, value=0)
            v_ca2      = r2.number_input("Ca 2",       min_value=0, value=0)
            v_nhap_qmi = r3.number_input("Nhập QMI",   min_value=0, value=0)
            v_xuat_cont= r4.number_input("Xuất Cont",  min_value=0, value=0)
            v_xuat_qmi = r5.number_input("Xuất QMI",   min_value=0, value=0)
            if st.form_submit_button("💾 Lưu"):
                st.session_state.nhap_xuat_rkw.append({
                    "ma_cont": sel_cont, "ngay": str(sel_date),
                    "ca1": v_ca1, "ca2": v_ca2, "nhap_qmi": v_nhap_qmi,
                    "xuat_cont": v_xuat_cont, "xuat_qmi": v_xuat_qmi,
                })
                st.success("Đã lưu!")
                st.rerun()

    df_nx_rkw = pd.DataFrame(st.session_state.nhap_xuat_rkw)
    if not df_nx_rkw.empty:
        df_nx_rkw["Tổng Nhập Ngày"] = df_nx_rkw.get("ca1",0) + df_nx_rkw.get("ca2",0) + df_nx_rkw.get("nhap_qmi",0)
        df_nx_rkw["Tổng Xuất Ngày"] = df_nx_rkw.get("xuat_cont",0) + df_nx_rkw.get("xuat_qmi",0)
        df_nx_rkw.columns = [c.replace("_"," ").title() for c in df_nx_rkw.columns]
        st.dataframe(df_nx_rkw, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu nhập xuất theo ngày.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: KHO QMI
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">🏪 KHO QMI - Theo Dõi Nhập/Xuất</div>', unsafe_allow_html=True)

    df_c2 = get_df_containers()
    if df_c2.empty:
        st.info("Chưa có container.")
    else:
        summary_qmi = []
        for c in st.session_state.containers:
            mc = c["ma_cont"]
            t_nhap, t_xuat, t_ton = calc_qmi(mc)
            summary_qmi.append({
                "Mã Cont": mc, "Mã Hàng": c["ma_hang"], "Tên Hàng": c["ten_hang"],
                "Kế Hoạch": c["ke_hoach"], "NW": c["nw"],
                "Ngày BD": c["ngay_bat_dau"], "Ngày KT": c["ngay_ket_thuc"],
                "Còn Trữ Kho": c["con_tru_kho_qmi"],
                "Tổng Nhập QMI": t_nhap, "Tổng Xuất QMI": t_xuat, "Tồn Cuối QMI": t_ton,
            })
        df_sq = pd.DataFrame(summary_qmi)
        st.dataframe(df_sq, use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng Nhập QMI", f"{df_sq['Tổng Nhập QMI'].sum():,}")
        col2.metric("Tổng Xuất QMI", f"{df_sq['Tổng Xuất QMI'].sum():,}")
        col3.metric("Tồn Cuối QMI",  f"{df_sq['Tồn Cuối QMI'].sum():,}")

    st.markdown('<div class="section-header">📥 Nhập Xuất Theo Ngày - Kho QMI</div>', unsafe_allow_html=True)

    with st.expander("➕ Thêm Dữ Liệu Nhập/Xuất Ngày (Kho QMI)"):
        with st.form("add_nx_qmi"):
            c1, c2, c3 = st.columns(3)
            sel_cont2 = c1.selectbox("Mã Cont", ma_cont_list(), key="qmi_cont")
            sel_date2 = c2.date_input("Ngày", value=date.today(), key="qmi_date")
            c3.write("")
            r1, r2, r3, r4, r5 = st.columns(5)
            v_ca1_q    = r1.number_input("Ca 1",      min_value=0, value=0, key="q_ca1")
            v_ca2_q    = r2.number_input("Ca 2",      min_value=0, value=0, key="q_ca2")
            v_nhap_l2  = r3.number_input("Nhập L2",   min_value=0, value=0, key="q_nhap_l2")
            v_xuat_cont_q = r4.number_input("Xuất Cont", min_value=0, value=0, key="q_xuat_cont")
            v_xuat_l2  = r5.number_input("Xuất L2",   min_value=0, value=0, key="q_xuat_l2")
            if st.form_submit_button("💾 Lưu"):
                st.session_state.nhap_xuat_qmi.append({
                    "ma_cont": sel_cont2, "ngay": str(sel_date2),
                    "ca1": v_ca1_q, "ca2": v_ca2_q, "nhap_l2": v_nhap_l2,
                    "xuat_cont": v_xuat_cont_q, "xuat_l2": v_xuat_l2,
                })
                st.success("Đã lưu!")
                st.rerun()

    df_nx_qmi = pd.DataFrame(st.session_state.nhap_xuat_qmi)
    if not df_nx_qmi.empty:
        show_cols = [c for c in df_nx_qmi.columns]
        st.dataframe(df_nx_qmi[show_cols], use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu nhập xuất theo ngày.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: KHO TỔNG
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">📊 KHO TỔNG - Tổng Hợp RKW + QMI</div>', unsafe_allow_html=True)

    tong_rows = []
    for c in st.session_state.containers:
        mc = c["ma_cont"]
        _, _, ton_rkw = calc_rkw(mc)
        _, _, ton_qmi = calc_qmi(mc)
        total        = ton_rkw + ton_qmi
        total_nw     = total * c["nw"]

        # ETD fields from QMI records
        qmi_rows = [r for r in st.session_state.nhap_xuat_qmi if r["ma_cont"] == mc]
        etd_l1 = qmi_rows[-1].get("ngay_etd_l1", "") if qmi_rows else ""
        etd_l2 = qmi_rows[-1].get("ngay_etd_l2", "") if qmi_rows else ""

        tong_rows.append({
            "Mã Cont":    mc,
            "Mã Hàng":    c["ma_hang"],
            "Tên Hàng":   c["ten_hang"],
            "Kế Hoạch":   c["ke_hoach"],
            "NW/thùng":   c["nw"],
            "Ngày BD":    c["ngay_bat_dau"],
            "Ngày KT":    c["ngay_ket_thuc"],
            "Kho RKW":    ton_rkw,
            "Kho QMI":    ton_qmi,
            "Total":      total,
            "Total NW":   round(total_nw, 2),
            "Date ETD L1": etd_l1,
            "Date ETD L2": etd_l2,
        })

    df_tong = pd.DataFrame(tong_rows)
    st.dataframe(df_tong, use_container_width=True, hide_index=True)

    # Summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng Tồn RKW", f"{df_tong['Kho RKW'].sum():,}")
    col2.metric("Tổng Tồn QMI", f"{df_tong['Kho QMI'].sum():,}")
    col3.metric("Grand Total",   f"{df_tong['Total'].sum():,}")
    col4.metric("Total NW (kg)", f"{df_tong['Total NW'].sum():,.1f}")

    # ETD update
    st.markdown('<div class="section-header">📅 Cập Nhật ETD</div>', unsafe_allow_html=True)
    with st.expander("Cập Nhật Date ETD cho Container"):
        with st.form("etd_form"):
            etd_cont = st.selectbox("Chọn Mã Cont", ma_cont_list(), key="etd_cont")
            c1, c2 = st.columns(2)
            etd_l1_val = c1.date_input("Date ETD L1", key="etd_l1")
            etd_l2_val = c2.date_input("Date ETD L2", key="etd_l2")
            if st.form_submit_button("💾 Lưu ETD"):
                # Find or create a QMI record for this cont
                existing = [i for i,r in enumerate(st.session_state.nhap_xuat_qmi) if r["ma_cont"]==etd_cont]
                if existing:
                    st.session_state.nhap_xuat_qmi[existing[-1]]["ngay_etd_l1"] = str(etd_l1_val)
                    st.session_state.nhap_xuat_qmi[existing[-1]]["ngay_etd_l2"] = str(etd_l2_val)
                else:
                    st.session_state.nhap_xuat_qmi.append({
                        "ma_cont": etd_cont, "ngay": str(date.today()),
                        "ngay_etd_l1": str(etd_l1_val), "ngay_etd_l2": str(etd_l2_val),
                        "ca1": 0, "ca2": 0, "nhap_l2": 0, "xuat_cont": 0, "xuat_l2": 0,
                    })
                st.success("Đã cập nhật ETD!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: BÁO CÁO
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📋 BÁO CÁO TỔNG HỢP</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    filter_kho  = col_f1.multiselect("Kho", ["RKW", "QMI"], default=["RKW","QMI"])
    filter_cont = col_f2.multiselect("Mã Cont", ma_cont_list(), default=ma_cont_list())
    date_from   = col_f3.date_input("Từ ngày", value=date(2026,1,1))
    date_to     = col_f3.date_input("Đến ngày", value=date.today())

    # Build unified report
    report_rows = []

    if "RKW" in filter_kho:
        for r in st.session_state.nhap_xuat_rkw:
            if r["ma_cont"] in filter_cont:
                d = datetime.strptime(r["ngay"], "%Y-%m-%d").date()
                if date_from <= d <= date_to:
                    report_rows.append({
                        "Kho": "RKW", "Mã Cont": r["ma_cont"], "Ngày": r["ngay"],
                        "Ca 1": r.get("ca1",0), "Ca 2": r.get("ca2",0),
                        "Nhập Kho": r.get("nhap_qmi",0),
                        "Tổng Nhập": r.get("ca1",0)+r.get("ca2",0)+r.get("nhap_qmi",0),
                        "Xuất Cont": r.get("xuat_cont",0), "Xuất KM": r.get("xuat_qmi",0),
                        "Tổng Xuất": r.get("xuat_cont",0)+r.get("xuat_qmi",0),
                    })

    if "QMI" in filter_kho:
        for r in st.session_state.nhap_xuat_qmi:
            if r["ma_cont"] in filter_cont:
                try:
                    d = datetime.strptime(r["ngay"], "%Y-%m-%d").date()
                except:
                    continue
                if date_from <= d <= date_to:
                    report_rows.append({
                        "Kho": "QMI", "Mã Cont": r["ma_cont"], "Ngày": r["ngay"],
                        "Ca 1": r.get("ca1",0), "Ca 2": r.get("ca2",0),
                        "Nhập Kho": r.get("nhap_l2",0),
                        "Tổng Nhập": r.get("ca1",0)+r.get("ca2",0)+r.get("nhap_l2",0),
                        "Xuất Cont": r.get("xuat_cont",0), "Xuất KM": r.get("xuat_l2",0),
                        "Tổng Xuất": r.get("xuat_cont",0)+r.get("xuat_l2",0),
                    })

    df_report = pd.DataFrame(report_rows)

    if df_report.empty:
        st.info("Không có dữ liệu theo bộ lọc.")
    else:
        st.dataframe(df_report, use_container_width=True, hide_index=True)

        # Aggregated
        st.markdown("#### 📊 Tổng Hợp Theo Kho")
        agg = df_report.groupby("Kho")[["Tổng Nhập","Tổng Xuất"]].sum().reset_index()
        st.dataframe(agg, use_container_width=True, hide_index=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Tổng Nhập (lọc)", f"{df_report['Tổng Nhập'].sum():,}")
        col_m2.metric("Tổng Xuất (lọc)", f"{df_report['Tổng Xuất'].sum():,}")
        col_m3.metric("Số dòng",          f"{len(df_report):,}")

        # Export Excel
        st.markdown("---")
        st.markdown("#### 📥 Xuất File Excel Tổng Hợp")

        def to_excel():
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_report.to_excel(writer, sheet_name="Báo Cáo Chi Tiết", index=False)
                agg.to_excel(writer, sheet_name="Tổng Hợp Theo Kho", index=False)

                # Kho Tổng sheet
                tong_rows2 = []
                for c in st.session_state.containers:
                    mc = c["ma_cont"]
                    _, _, ton_rkw = calc_rkw(mc)
                    _, _, ton_qmi = calc_qmi(mc)
                    total = ton_rkw + ton_qmi
                    tong_rows2.append({
                        "Mã Cont": mc, "Mã Hàng": c["ma_hang"], "Tên Hàng": c["ten_hang"],
                        "Kế Hoạch": c["ke_hoach"], "NW": c["nw"],
                        "Kho RKW": ton_rkw, "Kho QMI": ton_qmi,
                        "Total": total, "Total NW": round(total * c["nw"], 2),
                    })
                pd.DataFrame(tong_rows2).to_excel(writer, sheet_name="Kho Tổng", index=False)

            return output.getvalue()

        excel_data = to_excel()
        st.download_button(
            label="📊 Tải Xuống File Excel",
            data=excel_data,
            file_name=f"BaoCao_RKW_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
