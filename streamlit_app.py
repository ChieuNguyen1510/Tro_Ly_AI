import streamlit as st
from openai import OpenAI
from base64 import b64encode

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
    col1, col2, col3 = st.columns([1, 2, 1])  # Điều chỉnh tỷ lệ để logo căn giữa đẹp hơn
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# Hiển thị tiêu đề với viền dưới
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

if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# CSS cải tiến
st.markdown(
    """
    <style>
        .message {
            padding: 12px;
            border-radius: 12px;
            max-width: 75%;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin: 8px 0;  /* Thêm khoảng cách giữa các tin nhắn */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);  /* Thêm bóng đổ */
        }
        .assistant {
            background-color: #f0f7ff;  /* Màu nền nhạt cho assistant */
        }
        .user {
            background-color: #e6ffe6;  /* Màu nền nhạt cho user */
            text-align: right;
            margin-left: auto;
            flex-direction: row-reverse;
        }
        .icon {
            width: 32px;  /* Tăng kích thước icon một chút */
            height: 32px;
            border-radius: 50%;
            border: 1px solid #ddd;  /* Thêm viền nhẹ cho icon */
        }
        .text {
            flex: 1;
            font-size: 16px;  /* Tăng cỡ chữ cho dễ đọc */
            line-height: 1.4;  /* Tăng khoảng cách dòng */
        }
        .typing {
            font-style: italic;
            color: #888;
            padding: 5px 10px;
            display: flex;
            align-items: center;
        }
        /* Hiệu ứng nhấp nháy cho "Assistant is typing..." */
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .typing::after {
            content: "...";
            animation: blink 1s infinite;
        }
        /* Tùy chỉnh ô nhập liệu */
        [data-testid="stChatInput"] {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 8px;
            background-color: #fafafa;
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
if prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):  # Thêm placeholder tùy chỉnh
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