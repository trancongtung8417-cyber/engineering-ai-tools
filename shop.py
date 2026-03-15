import streamlit as st
from streamlit_gsheets import GSheetsConnection
from groq import Groq
import pandas as pd

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Tiệm Trà AI", page_icon="🍹", layout="centered")

# --- KẾT NỐI DỮ LIỆU (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Hàm đọc dữ liệu (tự động cập nhật sau 5 giây nếu có thay đổi)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1ggWWPxqe8zjM7Ydp0BE7KaUB1qG87qahq0EVJbCjGZM/edit?gid=0#gid=0"
    return conn.read(spreadsheet=url, worksheet="Sheet1", ttl=5)
    return df
#def load_data():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1ggWWPxqe8zjM7Ydp0BE7KaUB1qG87qahq0EVJbCjGZM/edit?gid=0#gid=0"
    df = conn.read(
        spreadsheet=spreadsheet_url,
        worksheet="Sheet1"
    )
    return df
df = load_data()
st.write(df)

#def load_data():
    #return conn.read(worksheet="Sheet1", ttl=5)

# --- GIAO DIỆN CHÍNH ---
st.title("🍹 Quản Lý Tiệm Trà Thông Minh")

# Phân chia Tab để anh dùng thử cả 2 hướng
tab_ops, tab_marketing, tab_admin = st.tabs(["⚡ Vận Hành (Tích Điểm)", "🪄 Marketing AI", "📈 Quản Lý & Báo Cáo"])

# --- TAB 1: VẬN HÀNH (Dùng tại quầy) ---
with tab_ops:
    st.subheader("💳 Tích Điểm Nhanh")
    df = load_data()
    sdt = st.text_input("Nhập Số điện thoại khách:", key="sdt_ops")
    
    if sdt:
        khach = df[df['Số điện thoại'].astype(str) == sdt]
        if not khach.empty:
            idx = khach.index[0]
            st.info(f"Khách: **{khach.iloc[0]['Tên']}** | Điểm: **{khach.iloc[0]['Số điểm']} 🌟**")
            
            if st.button("➕ Cộng 1 điểm"):
                df.at[idx, 'Số điểm'] += 1
                conn.update(worksheet="Sheet1", data=df)
                st.success("Đã cộng điểm lên Google Sheets!")
                st.rerun()
        else:
            st.warning("Khách mới! Hãy thêm thông tin bên Tab 'Quản lý'.")

# --- TAB 2: MARKETING (Dùng khi rảnh) ---
with tab_marketing:
    st.subheader("🤖 Trợ lý nội dung AI")
    topic = st.text_input("Món mới hoặc Ưu đãi:")
    if st.button("Tạo nội dung"):
        if "GROQ_API_KEY" in st.secrets:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Viết bài quảng cáo hấp dẫn cho: {topic}"}],
                model="llama-3.3-70b-versatile"
            )
            st.write(res.choices[0].message.content)
        else:
            st.error("Thiếu API Key trong Secrets!")

# --- TAB 3: QUẢN LÝ (Dành cho chủ shop) ---
with tab_admin:
    st.subheader("📊 Báo cáo & Thêm khách")
    df_admin = load_data()
    
    with st.expander("➕ Thêm khách hàng mới"):
        with st.form("new_user"):
            new_name = st.text_input("Tên:")
            new_phone = st.text_input("SĐT:")
            if st.form_submit_button("Lưu khách hàng"):
                new_data = pd.DataFrame([[new_name, new_phone, 1, ""]], columns=df_admin.columns)
                df_updated = pd.concat([df_admin, new_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_updated)
                st.success("Đã lưu khách mới lên Đám mây!")
                st.rerun()

    st.write("---")
    st.dataframe(df_admin, use_container_width=True)
    if not df_admin.empty:
        st.bar_chart(df_admin.set_index('Tên')['Số điểm'])