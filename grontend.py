
GENAI_API_KEY = "AIzaSyDuExne7oG9NnfNZeaqDOSXVtxUdau7IBU"  # کلید API خود را وارد کنید
import streamlit as st
import base64
import mimetypes
import os
from google import genai
from google.genai import types

# -----------------------
# تنظیم فونت وزیرمتن
# -----------------------
st.set_page_config(page_title="چت‌بات تعاملی", page_icon="🤖")
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    html, body, [class*="css"] {
        font-family: Vazirmatn, sans-serif;
    }
    .stChatMessage {
        font-family: Vazirmatn, sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# کلاینت Gemini
# -----------------------
client = genai.Client(api_key="AIzaSyDuExne7oG9NnfNZeaqDOSXVtxUdau7IBU")
model = "gemini-2.5-flash-image-preview"

# -----------------------
# حافظه گفتگو
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 چت‌بات تعاملی با تصویر")

# -----------------------
# نمایش گفتگوها
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "text":
            st.markdown(msg["content"])
        elif msg["type"] == "image":
            st.image(msg["content"], use_container_width=True)

# -----------------------
# ورودی کاربر
# -----------------------
with st.chat_message("user"):
    cols = st.columns([3, 1])
    with cols[0]:
        user_input = st.text_input("متن خود را وارد کنید:", key="input_text", label_visibility="collapsed")
    with cols[1]:
        uploaded_file = st.file_uploader("📷", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

send_btn = st.button("ارسال")

# -----------------------
# پردازش
# -----------------------
if send_btn and (user_input or uploaded_file):
    parts = []
    if user_input:
        parts.append(types.Part.from_text(text=user_input))
        st.session_state.messages.append({"role": "user", "type": "text", "content": user_input})

    if uploaded_file:
        file_bytes = uploaded_file.read()
        mime_type = mimetypes.guess_type(uploaded_file.name)[0] or "image/jpeg"
        parts.append(types.Part.from_bytes(mime_type=mime_type, data=file_bytes))
        st.session_state.messages.append({"role": "user", "type": "image", "content": uploaded_file})

    contents = [
        types.Content(role="user", parts=parts)
    ]

    generate_content_config = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])

    with st.chat_message("assistant"):
        placeholder = st.empty()
        output_images = []

        file_index = 0
        text_buffer = ""

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates
                and chunk.candidates[0].content
                and chunk.candidates[0].content.parts
            ):
                part = chunk.candidates[0].content.parts[0]

                if getattr(part, "inline_data", None) and part.inline_data.data:
                    data_buffer = part.inline_data.data
                    file_extension = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
                    file_name = f"output_{file_index}{file_extension}"
                    file_index += 1
                    with open(file_name, "wb") as f:
                        f.write(data_buffer)
                    output_images.append(file_name)
                elif getattr(chunk, "text", None):
                    text_buffer += chunk.text
                    placeholder.markdown(text_buffer)

        # ذخیره خروجی در session_state
        if text_buffer.strip():
            st.session_state.messages.append({"role": "assistant", "type": "text", "content": text_buffer})

        for img in output_images:
            st.image(img, use_container_width=True)
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": img})
