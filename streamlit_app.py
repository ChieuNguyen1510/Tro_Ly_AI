import streamlit as st
from openai import OpenAI
from base64 import b64encode

# Ẩn thanh công cụ và nút "Manage app"
st.markdown(
    """
    <style>
        /* Ẩn các nút Share, Star, Edit, GitHub */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stAppViewBlockContainer"] > div > div > div > div > div {
            display: none !important;
        }
        /* Ẩn nút Manage app */
        [data-testid="manage-app-button"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hàm đọc nội dung từ file văn bản
def rfile(name_file):
    with open(name_file, "r", encoding="utf-8") as file:
        return file.read()

# Hàm chuyển ảnh thành base64
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()

# Chuyển ảnh sang base64
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

# Hiển thị logo (nếu có)
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">{title_content}</h1>""",
    unsafe_allow_html=True
)

# OpenAI API
openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Tin nhắn hệ thống
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# Khởi tạo session_state.messages nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# Nút "New chat" tùy chỉnh với icon
st.markdown(
    """
    <style>
        .new-chat-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 14px;
            cursor: pointer;
            width: fit-content;
            margin: 10px 0;
        }
        .new-chat-btn:hover {
            background-color: #45a049;
        }
        .new-chat-icon {
            width: 16px;
            height: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sử dụng st.button để xử lý logic, nhưng ẩn nó và kích hoạt qua HTML
if st.button("New chat", key="new_chat_hidden"):
    # Reset messages về trạng thái ban đầu
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]
    # Làm mới giao diện
    st.rerun()

# Hiển thị nút tùy chỉnh với icon
st.markdown(
    """
    <button class="new-chat-btn" onclick="document.getElementById('new_chat_hidden').click()">
        <svg class="new-chat-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15v-2h2v2h-2zm1-4c-1.1 0-2-.9-2-2V7h4v4c0 1.1-.9 2-2 2z"/>
        </svg>
        New chat
    </button>
    """,
    unsafe_allow_html=True
)

# CSS cải tiến
st.markdown(
    """
    <style>
        .message {
            padding: 12px !important;
            border-radius: 12px !important;
            max-width: 75% !important;
            display: flex !important;
            align-items: flex-start !important;
            gap: 12px !important;
            margin: 8px 0 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        .assistant {
            background-color: #f0f7ff !important;
        }
        .user {
            background-color: #e6ffe6 !important;
            text-align: right !important;
            margin-left: auto !important;
            flex-direction: row-reverse !important;
        }
        .icon {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            border: 1px solid #ddd !important;
        }
        .text {
            flex: 1 !important;
            font-size: 16px !important;
            line-height: 1.4 !important;
        }
        .typing {
            font-style: italic !important;
            color: #888 !important;
            padding: 5px 10px !important;
            display: flex !important;
            align-items: center !important;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .typing::after {
            content: "..." !important;
            animation: blink 1s infinite !important;
        }
        [data-testid="stChatInput"] {
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            padding: 8px !important;
            background-color: #fafafa !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hiển thị lịch sử tin nhắn (trừ system)
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'''
        <div class="message assistant">
            <img src="data:image/png;base64,{assistant_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'''
        <div class="message user">
            <img src="data:image/png;base64,{user_icon}" class="icon" />
            <div class="text">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

# Ô nhập câu hỏi
if prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.markdown(f'''
    <div class="message user">
        <img src="data:image/png;base64,{user_icon}" class="icon" />
        <div class="text">{prompt}</div>
    </div>
    ''', unsafe_allow_html=True)

    # Assistant đang trả lời...
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        '<div class="typing">Assistant đang trả lời</div>',
        unsafe_allow_html=True
    )

    # Gọi API
    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""

    # Xóa dòng "Assistant is typing..."
    typing_placeholder.empty()

    # Hiển thị phản hồi từ assistant
    st.markdown(f'''
    <div class="message assistant">
        <img src="data:image/png;base64,{assistant_icon}" class="icon" />
        <div class="text">{response}</div>
    </div>
    ''', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})