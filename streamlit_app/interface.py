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

    # Khởi tạo session_state nếu chưa có
    if "fb_messages" not in st.session_state:
        st.session_state.fb_messages = []
        st.session_state.fb_reload = True

    # Nút làm mới hộp thư
    if st.button("🔄 Làm mới hộp thư"):
        st.session_state.fb_reload = True

    # Gọi API chỉ khi cần
    if st.session_state.fb_reload:
        try:
            res = requests.get("http://localhost:8000/fb/messages")
            st.session_state.fb_messages = res.json()
            st.session_state.fb_reload = False
        except Exception as e:
            st.error(f"Lỗi khi lấy tin nhắn: {e}")
            st.session_state.fb_messages = []

    grouped = defaultdict(list)
    for msg in st.session_state.fb_messages:
        grouped[msg["sender_id"]].append(msg)

    if not grouped:
        st.info("Không có tin nhắn nào.")
    else:
        for sender_id, chat_list in grouped.items():
            with st.expander(f"💬 Đoạn chat với: {sender_id}", expanded=True):
                for item in sorted(chat_list, key=lambda x: x["timestamp"]):
                    time_str = datetime.fromtimestamp(item["timestamp"] / 1000).strftime("%d-%m-%Y %H:%M")

                    if item["message"]:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin: 5px;">
                            <div style="background-color: #d0ebff; padding: 10px; border-radius: 10px; max-width: 65%;">
                                <div>{item['message']}</div>
                                <div style="font-size: 10px; text-align: right; color: gray;">{time_str}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    if item["reply"]:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-end; margin: 5px;">
                            <div style="background-color: #f1f0f0; padding: 10px; border-radius: 10px; max-width: 65%;">
                                <div>{item['reply']}</div>
                                <div style="font-size: 10px; text-align: right; color: gray;">{time_str}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                reply = st.text_input("Nhập phản hồi", key=f"reply_{sender_id}")
                if st.button("Gửi", key=f"btn_{sender_id}"):
                    try:
                        send = requests.post("http://localhost:8000/fb/reply", json={
                            "sender_id": sender_id,
                            "message": reply
                        })
                        if send.status_code == 200:
                            st.success("Đã gửi phản hồi!")
                            st.session_state.fb_reload = True  # để reload lại dữ liệu mới
                            st.rerun()
                        else:
                            st.error("Gửi phản hồi thất bại.")
                    except Exception as e:
                        st.error(f"Lỗi khi gửi: {e}")

# ========================== TAB 2 ==========================
with tab3:
    st.markdown("<h2 style='text-align: center;'>📂 Quản lý dữ liệu nội bộ</h2>", unsafe_allow_html=True)

    # ====== KHỞI TẠO session_state =======
    if "sample_updated" not in st.session_state:
        st.session_state.sample_updated = True  # cho phép lấy dữ liệu lần đầu

    if "file_list" not in st.session_state:
        st.session_state.file_list = []
        st.session_state.need_reload_files = True

    # ====== CHỈ LẤY sample.txt KHI CẦN =======
    sample_content = ""
    if st.session_state.sample_updated:
        try:
            res = requests.get("http://localhost:8000/api/files/sample")
            sample_content = res.json().get("content", "")
        except:
            sample_content = ""
        st.session_state.sample_updated = False

    edited_sample = st.text_area("Chỉnh sửa sample.txt", value=sample_content, height=200)
    if st.button("💾 Lưu sample.txt"):
        res = requests.post("http://localhost:8000/api/files/sample", params={"content": edited_sample})
        if res.status_code == 200:
            st.success("✅ Đã lưu sample.txt")
            st.session_state.sample_updated = True
            st.rerun()

    # ====== UPLOAD FILE =======
    uploaded_file = st.file_uploader("📤 Tải lên tệp hỗ trợ (.txt, .pdf, .csv, .docx)", type=["txt", "pdf", "csv", "docx"])
    if "uploaded_once" not in st.session_state:
        st.session_state.uploaded_once = False

    if uploaded_file and not st.session_state.uploaded_once:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = requests.post("http://localhost:8000/api/files/upload", files=files)
        if res.status_code == 200:
            st.success(f"✅ {uploaded_file.name} đã được tải lên.")
            st.session_state.need_reload_files = True
            st.session_state.uploaded_once = True
            st.rerun()

    # ====== LẤY DANH SÁCH FILE KHI CẦN =======
    if st.session_state.need_reload_files:
        try:
            res = requests.get("http://localhost:8000/api/files/list")
            st.session_state.file_list = res.json().get("files", [])
        except:
            st.session_state.file_list = []
        st.session_state.need_reload_files = False

    st.subheader("📂 Danh sách tệp đã tải")
    for file in st.session_state.file_list:
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"- {file}")
        if col2.button("❌ Xoá", key=f"del_{file}"):
            res = requests.delete(f"http://localhost:8000/api/files/delete/{file}")
            if res.status_code == 200:
                st.success(f"Đã xoá {file}")
                st.session_state.need_reload_files = True
                st.rerun()

    # ====== CẬP NHẬT RETRIEVER =======
    if st.button("🔄 Cập nhật retriever"):
        res = requests.post("http://localhost:8000/api/files/update_retriever")
        if res.status_code == 200:
            st.success("✅ Đã cập nhật FAISS retriever!")
        else:
            st.error("❌ Lỗi khi cập nhật.")



