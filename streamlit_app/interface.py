from datetime import datetime
from collections import defaultdict
import streamlit as st
import requests

st.set_page_config(page_title="Chatbot Shop", layout="wide")

tab1, tab2, tab3 = st.tabs(["💬 Chat thử với Chatbot", "📨 Hộp thư Facebook", "📄 Quản lý dữ liệu huấn luyện"])

# ========================== TAB 1 ==========================
with tab1:
    st.markdown("<h2 style='text-align: center;'>💬 Chat với chatbot cửa hàng</h2>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, msg in st.session_state.chat_history:
        align = "flex-start" if role == "user" else "flex-end"
        bgcolor = "#dcf8c6" if role == "user" else "#e4e6eb"
        bubble = f"""
        <div style="display: flex; justify-content: {align}; margin: 5px;">
            <div style="background-color: {bgcolor}; padding: 10px; border-radius: 10px; max-width: 60%;">
                {msg}
            </div>
        </div>
        """
        st.markdown(bubble, unsafe_allow_html=True)

    user_input = st.chat_input("Nhập tin nhắn để hỏi...")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("Đang trả lời..."):
            try:
                res = requests.post("http://localhost:8000/chat", json={"message": user_input})
                reply = res.json().get("reply", "Không có phản hồi.")
            except Exception as e:
                reply = f"Lỗi: {e}"
        st.session_state.chat_history.append(("bot", reply))
        st.rerun()

# ========================== TAB 2 ==========================
with tab2:
    st.markdown("<h2 style='text-align: center;'>📨 Tin nhắn Facebook</h2>", unsafe_allow_html=True)

    try:
        res = requests.get("http://localhost:8000/fb/messages")
        messages = res.json()
    except Exception as e:
        st.error(f"Lỗi khi lấy tin nhắn: {e}")
        messages = []

    grouped = defaultdict(list)
    for msg in messages:
        grouped[msg["sender_id"]].append(msg)

    if not grouped:
        st.info("Không có tin nhắn nào.")
    else:
        for sender_id, chat_list in grouped.items():
            with st.expander(f"💬 Đoạn chat với: {sender_id}", expanded=True):
                for item in sorted(chat_list, key=lambda x: x["timestamp"]):
                    is_user = item.get("from_user", True)
                    align = "flex-start"
                    bgcolor = "#d0ebff"
                    align_rep ="flex-end"
                    bgcolor_rep ="#f1f0f0"
                    
                    time_str = datetime.fromtimestamp(item["timestamp"] / 1000).strftime("%d-%m-%Y %H:%M")

                    bubble = f"""
                    <div style="display: flex; justify-content: {align}; margin: 5px;">
                        <div style="background-color: {bgcolor}; padding: 10px; border-radius: 10px; max-width: 65%;">
                            <div>{item['message']}</div>
                            <div style="font-size: 10px; text-align: right; color: gray;">{time_str}</div>
                        </div>
                    </div>
                    """
                    bubble_rep = f"""
                    <div style="display: flex; justify-content: {align_rep}; margin: 5px;">
                        <div style="background-color: {bgcolor_rep}; padding: 10px; border-radius: 10px; max-width: 65%;">
                            <div>{item['reply']}</div>
                            <div style="font-size: 10px; text-align: right; color: gray;">{time_str}</div>
                        </div>
                    </div>
                    """
                    if item['message'] != '': 
                        st.markdown(bubble, unsafe_allow_html=True)
                    if item['reply'] != '': 
                        st.markdown(bubble_rep, unsafe_allow_html=True)

                reply = st.text_input("Nhập phản hồi", key=f"reply_{sender_id}")
                if st.button("Gửi", key=f"btn_{sender_id}"):
                    try:
                        send = requests.post("http://localhost:8000/fb/reply", json={
                            "sender_id": sender_id,
                            "message": reply
                        })
                        if send.status_code == 200:
                            st.success("Đã gửi phản hồi!")
                        else:
                            st.error("Gửi phản hồi thất bại.")
                    except Exception as e:
                        st.error(f"Lỗi khi gửi: {e}")

from PyPDF2 import PdfReader

with tab3:
    st.markdown("<h2 style='text-align: center;'>📂 Quản lý dữ liệu văn bản</h2>", unsafe_allow_html=True)

    st.subheader("📝 Nội dung tệp mẫu (sample.txt)")
    try:
        with open("data/knowledge_base/sample.txt", "r", encoding="utf-8") as f:
            sample_content = f.read()
    except:
        sample_content = ""

    edited_sample = st.text_area("Chỉnh sửa nội dung sample.txt", value=sample_content, height=200)
    if st.button("💾 Lưu nội dung"):
        with open("data/knowledge_base/sample.txt", "w", encoding="utf-8") as f:
            f.write(edited_sample)
        st.success("Đã lưu nội dung thành công!")

    st.subheader("📤 Tải lên tệp mới (TXT hoặc PDF)")
    uploaded_file = st.file_uploader("Chọn tệp TXT hoặc PDF", type=["txt", "pdf"])

    if uploaded_file is not None:
        save_path = "data/knowledge_base/uploaded_content.txt"

        if uploaded_file.type == "application/pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

        elif uploaded_file.type == "text/plain":
            # đọc thẳng file txt
            text = uploaded_file.read().decode("utf-8")

        else:
            text = ""
            st.error("❌ Định dạng file không hợp lệ. Vui lòng tải lên file TXT hoặc PDF.")

        if text:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            st.success("✅ Đã tải và lưu nội dung tệp!")
        try:
            with open(save_path, "r", encoding="utf-8") as f:
                uploaded_content = f.read()
        except:
            uploaded_content = ""
        edited_sample = st.text_area("Chỉnh sửa nội dung uploaded_content.txt", value=uploaded_content, height=200)
        if st.button("Lưu nội dung"):
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(edited_sample)
            st.success("Đã lưu nội dung thành công!")

    if st.button("🔄 Cập nhật retriever"):
        try:
            res = requests.post("http://localhost:8000/update_retriever")
            if res.status_code == 200:
                st.success("✅ Đã cập nhật chunk và retriever thành công!")
            else:
                st.error("❌ Lỗi khi cập nhật retriever.")
        except Exception as e:
            st.error(f"❌ Lỗi kết nối: {e}")
