import google.generativeai as genai
import streamlit as st
from PIL import Image
import io
import base64
import hashlib
import os

# تنظیم کلید API و مدل
genai.configure(api_key="AIzaSyDuExne7oG9NnfNZeaqDOSXVtxUdau7IBU")

# تنظیمات مدل
generation_config = {
    "temperature": 0.25,
    "top_p": 0.55,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="""
    شما یک متخصص پردازش تصویر هستید که به کاربران در ویرایش و بهبود تصاویر محصول کمک می‌کنید.
    لطفاً بر اساس تصویر ارائه شده و درخواست کاربر، پیشنهادات حرفه‌ای ارائه دهید.
    در پاسخ‌های خود موارد زیر را رعایت کنید:
    - ارائه توضیحات فنی واضح و مختصر
    - پیشنهاد راه‌حل‌های عملی برای بهبود تصویر
    - ذکر نکات مهم در پردازش تصویر محصول
    - پاسخ‌های مفید و کاربردی بدون حاشیه
    تو یک ربات هستی تا تصاویر عکاسی معمولی را همانطوری که کاربر میگوید تبدیل کنی به تصاویر حرفه ای عکاسی شده برای همین خیلی خیلی خیلی خیلی مهم است که جزئیات محصولی که کاربر تصویرش را فرستاده حفظ شود. ممکن است لباس را در تن یک انسان ببیند یا روی آویز یا هر چیز دیگری. صرفا هم به لباس محدود نیست تصاویر و تمام محصولات دنیا را ممکن است شامل شود.
    """
)

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
        background-color: #f8f9fa;
    }
    p, div, input, label, h1, h2, h3, h4, h5, h6 {
        direction: RTL;
        text-align: right;
        font-family: Vazirmatn, sans-serif!important;
    }
    .uploaded-image {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
        background-color: #e3f2fd;
        border-right: 4px solid #2196f3;
    }
    .chat-message.assistant {
        background-color: #f3e5f5;
        border-right: 4px solid #9c27b0;
    }
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# مدیریت احراز هویت
def check_password():
    """بررسی رمز عبور کاربر"""
    # رمز عبور هش شده (برای امنیت بیشتر)
    # رمز پیش فرض: admin123 (می‌توانید تغییر دهید)
    hashed_password = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # admin123
    
    # اگر کاربر قبلاً وارد شده بود
    if st.session_state.get("authenticated", False):
        return True
        
    # نمایش فرم ورود
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.title("🔐 ورود به سیستم")
    
    password = st.text_input("رمز عبور:", type="password")
    login_button = st.button("ورود")
    
    if login_button:
        # هش کردن رمز وارد شده و مقایسه با رمز ذخیره شده
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        if input_hash == hashed_password:
            st.session_state.authenticated = True
            st.success("ورود موفقیت‌آمیز بود!")
            st.rerun()
        else:
            st.error("رمز عبور نادرست است")
    
    st.markdown("</div>", unsafe_allow_html=True)
    return False

# بررسی احراز هویت قبل از نمایش محتوای اصلی
if not check_password():
    st.stop()

# مدیریت وضعیت (state) برنامه
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'processing_request' not in st.session_state:
    st.session_state.processing_request = ""

# تابع برای پردازش تصویر با جمنای
def process_image_with_gemini(image, prompt):
    try:
        # تبدیل تصویر به فرمتی که جمنای بتواند پردازش کند
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # ایجاد مدل برای پردازش تصویر
        vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        # ارسال تصویر و درخواست به جمنای
        response = vision_model.generate_content([
            prompt,
            Image.open(io.BytesIO(img_byte_arr))
        ])
        
        return response.text
    except Exception as e:
        return f"خطا در پردازش تصویر: {str(e)}"

# تابع برای پردازش متن با جمنای
def process_text_with_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطا در پردازش متن: {str(e)}"

# عنوان برنامه
st.title("🎨 پردازش تصویر با جمنای")
st.markdown("تصویر محصول خود را paste کنید یا آپلود کنید و با جمنای چت کنید")

# دکمه خروج
if st.sidebar.button("خروج از سیستم"):
    st.session_state.authenticated = False
    st.rerun()

# ایجاد دو ستون
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📤 آپلود تصویر")
    
    # روش اول: آپلود فایل
    uploaded_file = st.file_uploader("تصویر را انتخاب کنید", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.uploaded_image = image
        st.image(image, caption="تصویر آپلود شده", use_column_width=True)
    
    # روش دوم: Paste از کلیپ‌بورد
    st.markdown("---")
    st.subheader("📋 Paste از کلیپ‌بورد")
    
    # ایجاد یک زمینه برای paste کردن تصویر
    paste_area = st.empty()
    paste_content = paste_area.text_input("برای paste کردن تصویر، اینجا کلیک کنید و Ctrl+V را بزنید", 
                                         help="میتوانید تصویر را از هر جایی کپی کنید و اینجا paste کنید")
    
    if paste_content:
        try:
            # اگر کاربر تصویری paste کرده باشد
            if paste_content.startswith('data:image'):
                # استخراج داده‌های base64 از URL
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
    
    # نمایش تاریخچه چت
    for message in st.session_state.chat_history:
        with st.container():
            if message['role'] == 'user':
                st.markdown(f"<div class='chat-message user'><strong>شما:</strong> {message['content']}</div>", 
                           unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message assistant'><strong>جمنای:</strong> {message['content']}</div>", 
                           unsafe_allow_html=True)
    
    # ورودی کاربر
    user_input = st.text_input("سوال یا درخواست خود را وارد کنید", key="user_input")
    
    if st.button("ارسال") and user_input:
        # افزودن پیام کاربر به تاریخچه چت
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # پردازش درخواست
        if st.session_state.uploaded_image:
            # اگر تصویر وجود دارد، از مدل بینایی استفاده کنید
            with st.spinner("جمنای در حال پردازش تصویر..."):
                response = process_image_with_gemini(st.session_state.uploaded_image, user_input)
        else:
            # اگر تصویر وجود ندارد، از مدل متنی استفاده کنید
            with st.spinner("جمنای در حال پردازش..."):
                response = process_text_with_gemini(user_input)
        
        # افزودن پاسخ جمنای به تاریخچه چت
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        
        # رفرش صفحه برای نمایش پیام جدید
        st.rerun()

# بخش راهنما
st.markdown("---")
st.subheader("📋 راهنما")
st.markdown("""
1. **آپلود تصویر**: از طریق دکمه 'تصویر را انتخاب کنید' یک فایل تصویر آپلود کنید
2. **Paste تصویر**: از هر جایی تصویر را کپی کنید (Ctrl+C) و در کادر متن Paste کنید (Ctrl+V)
3. **چت با جمنای**: درخواست خود را تایپ کنید و ارسال کنید
4. **نمایش نتایج**: پاسخ جمنای در بخش چت نمایش داده می‌شود
""")

# پاک کردن تاریخچه چت
if st.button("پاک کردن تاریخچه چت"):
    st.session_state.chat_history = []
    st.rerun()
