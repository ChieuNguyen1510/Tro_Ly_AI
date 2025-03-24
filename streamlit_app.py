import streamlit as st
from openai import OpenAI
from base64 import b64encode

# Hàm đọc file văn bản
def rfile(name_file):
    with open(name_file, "r", encoding="utf-8") as file:
        return file.read()

# Chuyển ảnh sang base64
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return b64encode(f.read()).decode()

# Tự động sửa công thức từ [ \ ... ] → $ ... $
def fix_latex(text):
    return text.replace("[", "$").replace("]", "$")

# Chuyển icon
assistant_icon = img_to_base64("assistant_icon.png")
user_icon = img_to_base64("user_icon.png")

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

# OpenAI
openai_api_key = st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Tin nhắn hệ thống
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# CSS typing
st.markdown(
    """
    <style>
        .typing {
            font-style: italic;
            color: gray;
            padding: 5px 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Hiển thị lịch sử trò chuyện
for message in st.session_state.messages:
    content_fixed = fix_latex(message["content"])
    if message["role"] == "assistant":
        col1, col2 = st.columns([1, 8])
        with col1:
            st.image(f"data:image/png;base64,{assistant_icon}", width=28)
        with col2:
            st.markdown(content_fixed, unsafe_allow_html=False)
    elif message["role"] == "user":
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"<div style='text-align: right'>{fix_latex(message['content'])}</div>", unsafe_allow_html=True)
        with col2:
            st.image(f"data:image/png;base64,{user_icon}", width=28)

# Người dùng nhập câu hỏi
if prompt := st.chat_input("Please enter your questions here"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Hiển thị user input
    col1, col2 = st.columns([8, 1])
    with col1:
        st.markdown(f"<div style='text-align: right'>{fix_latex(prompt)}</div>", unsafe_allow_html=True)
    with col2:
        st.image(f"data:image/png;base64,{user_icon}", width=28)

    # Assistant is typing...
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        '<div class="typing">Assistant is typing...</div>',
        unsafe_allow_html=True
    )

    # Gọi API OpenAI
    response = ""
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices:
            response += chunk.choices[0].delta.content or ""

    typing_placeholder.empty()

    # Hiển thị kết quả assistant
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(f"data:image/png;base64,{assistant_icon}", width=28)
    with col2:
        st.markdown(fix_latex(response), unsafe_allow_html=False)

    st.session_state.messages.append({"role": "assistant", "content": response})
