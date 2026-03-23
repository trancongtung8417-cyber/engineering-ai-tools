# ... (đoạn code phía trên giữ nguyên) ...
                
                st.divider()
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_amt = st.number_input("Số tiền (VND)", min_value=0, step=10000, format="%d")
                    # Hiển thị khung xác nhận số tiền màu xanh
                    st.info(f"💰 Đang nhập: **{format_vn_currency(m_amt)}**")
                with col_m2:
                    m_act = st.radio("Loại giao dịch", ["Nạp tiền", "Trừ tiền"])
                    m_reason = st.text_input("Nội dung dịch vụ")
                
                if st.button("Xác nhận Giao dịch", use_container_width=True, type="primary"):
                    if not m_reason: st.warning("Vui lòng nhập nội dung!")
                    elif m_amt <= 0: st.warning("Số tiền không hợp lệ!")
                    else:
                        new_bal = current_bal + m_amt if m_act == "Nạp tiền" else current_bal - m_amt
                        update_user_field(m_target, "balance", new_bal)
                        add_history(m_target, m_amt, m_act, m_reason)
                        st.success("Giao dịch thành công!")
                        st.rerun()