import streamlit as st
from PIL import Image
import io
import base64
import mimetypes
import os
from google import genai
from google.genai import types

# تنظیمات کلید API
GENAI_API_KEY = "AIzaSyDuExne7oG9NnfNZeaqDOSXVtxUdau7IBU"  # کلید API خود را وارد کنید
os.environ["GEMINI_API_KEY"] = GENAI_API_KEY

# تعریف تابع ذخیره فایل
def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

# تعریف تابع تولید محتوا
def generate_with_gemini(prompt, image=None):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.5-flash-image-preview"
    
    # محتوای ورودی
    parts = [types.Part.from_text(text=prompt)]
    if image:
        # تبدیل تصویر به داده باینری
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        parts.append(types.Part.from_inline_data(data=img_byte_arr.getvalue(), mime_type="image/png"))
    
    contents = [types.Content(role="user", parts=parts)]
    
    generate_content_config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    
    results = {"text": "", "images": []}
    file_index = 0
    
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        
        # متن خروجی
        if chunk.candidates[0].content.parts[0].text:
            results["text"] += chunk.candidates[0].content.parts[0].text
        
        # تصویر خروجی
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            file_name = f"gemini_output_{file_index}{file_extension}"
            file_index += 1
            save_binary_file(file_name, data_buffer)
            results["images"].append(file_name)
    
    return results

# تنظیمات صفحه Streamlit
st.set_page_config(page_title="پردازش تصویر با جمنای", layout="wide")
st.markdown("""
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
<style>
    body, html, .stApp {
        direction: RTL;
        unicode-bidi: bidi-override;
        text-align: right;
        font-family: Vazirmatn, sans-serif!important;
        background-color: #121212;
        color: #e0e0e0;
    }
    .stMarkdown, h1, h2, h3, h4, h5, h6, label, p {
        color: #e0e0e0 !important;
    }
    .uploaded-image {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #212121;
        border-right: 4px solid #2196f3;
        color: #e0e0e0;
    }
    .chat-message.assistant {
        background-color: #424242;
        border-right: 4px solid #9c27b0;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# مدیریت وضعیت برنامه
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# عنوان برنامه
st.title("🎨 پردازش تصویر با جمنای")
st.markdown("تصویر محصول خود را paste کنید یا آپلود کنید و با جمنای چت کنید")

# ایجاد دو ستون
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📤 آپلود تصویر")
    uploaded_file = st.file_uploader("تصویر را انتخاب کنید", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.uploaded_image = image
        st.image(image, caption="تصویر آپلود شده", use_column_width=True)
    
    st.markdown("---")
    st.subheader("📋 Paste از کلیپ‌بورد")
    paste_area = st.empty()
    paste_content = paste_area.text_input("برای paste کردن تصویر، اینجا کلیک کنید و Ctrl+V را بزنید")
    if paste_content:
        try:
            if paste_content.startswith('data:image'):
                image_data = paste_content.split(',')[1]
                decoded_image = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(decoded_image))
                st.session_state.uploaded_image = image
                st.image(image, caption="تصویر Paste شده", use_column_width=True)
                paste_area.text_input("برای paste کردن تصویر، اینجا کلیک کنید و Ctrl+V را بزنید", value="")
            else:
                st.info("لطفاً یک تصویر معتبر paste کنید")
        except Exception as e:
            st.error(f"خطا در پردازش تصویر paste شده: {str(e)}")

with col2:
    st.header("💬 چت با جمنای")
    for message in st.session_state.chat_history:
        with st.container():
            if message['role'] == 'user':
                st.markdown(f"<div class='chat-message user'><strong>شما:</strong> {message['content']}</div>", 
                           unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message assistant'><strong>جمنای:</strong> {message['content']}</div>", 
                           unsafe_allow_html=True)
    
    user_input = st.text_input("سوال یا درخواست خود را وارد کنید", key="user_input")
    if st.button("ارسال") and user_input:
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        if st.session_state.uploaded_image:
            with st.spinner("جمنای در حال پردازش تصویر..."):
                results = generate_with_gemini(user_input, st.session_state.uploaded_image)
        else:
            with st.spinner("جمنای در حال پردازش..."):
                results = generate_with_gemini(user_input)
        
        st.session_state.chat_history.append({'role': 'assistant', 'content': results["text"]})
        for image_file in results["images"]:
            st.image(image_file, caption="تصویر خروجی", use_column_width=True)
        st.rerun()

# پاک کردن تاریخچه چت
if st.button("پاک کردن تاریخچه چت"):
    st.session_state.chat_history = []
    st.rerun()
