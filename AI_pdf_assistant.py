import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

st.set_page_config(page_title="Technical PDF Assistant", page_icon="📄")

# Nhập API Key (Để an toàn, khách tự nhập hoặc bạn cấu hình trong secrets)
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.info("This tool helps you analyze complex technical specifications.")

st.title("📄 AI Technical PDF Assistant")
st.write("Upload a technical spec or manual to start chatting.")

uploaded_file = st.file_uploader("Upload your PDF document", type="pdf")

if uploaded_file and api_key:
    # 1. Trích xuất text từ PDF
    reader = PdfReader(uploaded_file)
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text()
    
    # 2. Giao diện Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about the technical specs..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 3. Gọi AI với System Prompt chuyên gia
        client = Groq(api_key=api_key)
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a Senior Technical Engineer. Analyze the provided text and answer questions accurately. Use Metric units and formal English. If info is missing, say 'Not found'."},
                    {"role": "system", "content": f"Document Content: {raw_text[:15000]}"}, # Giới hạn 15k ký tự đầu để tránh lỗi token
                    *st.session_state.messages
                ]
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
elif not api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to begin.")