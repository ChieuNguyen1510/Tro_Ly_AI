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

# Thêm MathJax để render LaTeX
st.markdown(
    """
    <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    """,
    unsafe_allow_html=True
)

# Hiển thị logo (nếu có)
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)
except:
    pass

# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
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

# CSS
st.markdown(
    """
    <style>
        .message {
            padding: 10px;
            border-radius: 10px;
            max-width: 75%;
            background: none;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        .user {
            text-align: right;
            margin-left: auto;
            flex-direction: row-reverse;
        }
        .icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
        }
        .text {
            flex: 1;
        }
        .typing {
            font-style: italic;
            color: gray;
            padding: 5px 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hiển thị lịch sử tin nhắn (trừ system)
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'''
        <div class="message">
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
if prompt := st.chat_input("Please enter your questions here"):
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
        '<div class="typing">Assistant is typing...</div>',
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

    # Xử lý response để thêm cú pháp LaTeX nếu cần
    if "[" in response and "]" in response:
        response = response.replace("[", "$$").replace("]", "$$")

    # Hiển thị phản hồi từ assistant và buộc MathJax render lại
    st.markdown(
        f'''
        <div class="message">
            <img src="data:image/png;base64,{assistant_icon}" class="icon" />
            <div class="text">{response}</div>
        </div>
        <script type="text/javascript">
            window.MathJax.Hub.Queue(["Typeset", window.MathJax.Hub]);
        </script>
        ''',
        unsafe_allow_html=True
    )

    st.session_state.messages.append({"role": "assistant", "content": response})