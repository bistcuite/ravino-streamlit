import google.generativeai as genai
import streamlit as st
import json

# تنظیم کلید API
genai.configure(api_key="AIzaSyDuExne7oG9NnfNZeaqDOSXVtxUdau7IBU")

# تنظیمات اولیه مدل
def initialize_model(system_instruction):
    generation_config = {
        "temperature": 0.25,
        "top_p": 0.55,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

# داده‌های اولیه system instruction
default_system_instruction = """شما دستیار هوشمند آموزشگاه زبان «زبانزد» هستید. آدرس سایت آموزشگاه: https://zabanzadacademy.ir/

دو وظیفه اصلی دارید:

🟦 ۱. مشاوره درباره کلاس‌های آموزشگاه:

اطلاعات کلاس‌ها به صورت ساختارمند در قالب JSON زیر به شما داده شده است:

📦 داده‌های کلاس‌ها:
```json
{
  "کلاس‌ها": [
    {
      "نام": "مکالمه زبان انگلیسی - سطح متوسط",
      "سطح": "متوسط",
      "توضیح": "تقویت مهارت مکالمه و شنیداری در موقعیت‌های روزمره",
      "مدرس": "سرکار خانم سارا جانسون",
      "قیمت": 1200000,
      "تعداد جلسات": 12,
      "زمان‌بندی": "دوشنبه و چهارشنبه‌ها - ساعت ۱۸ تا ۱۹:۳۰",
      "ظرفیت باقی‌مانده": 5
    },
    {
      "نام": "دوره آمادگی آیلتس",
      "سطح": "پیشرفته",
      "توضیح": "آمادگی کامل برای آزمون آیلتس آکادمیک و جنرال",
      "مدرس": "آقای علی حسینی",
      "قیمت": 1800000,
      "تعداد جلسات": 15,
      "زمان‌بندی": "سه‌شنبه و پنج‌شنبه‌ها - ساعت ۱۷ تا ۱۹",
      "ظرفیت باقی‌مانده": 2
    },
    {
      "نام": "گرامر و واژگان سطح مقدماتی",
      "سطح": "مبتدی",
      "توضیح": "آموزش پایه‌ای گرامر و لغات برای ارتباط اولیه",
      "مدرس": "سرکار خانم لادن مهر",
      "قیمت": 900000,
      "تعداد جلسات": 10,
      "زمان‌بندی": "شنبه‌ها - ساعت ۱۰ تا ۱۲",
      "ظرفیت باقی‌مانده": 8
    },
    {
      "نام": "انگلیسی تجاری",
      "سطح": "بالا-متوسط",
      "توضیح": "مهارت‌های زبان برای جلسات، پرزنتیشن و مکاتبات تجاری",
      "مدرس": "آقای جیمز کارتر",
      "قیمت": 1500000,
      "تعداد جلسات": 10,
      "زمان‌بندی": "جمعه‌ها - ساعت ۱۴ تا ۱۷",
      "ظرفیت باقی‌مانده": 0
    }
  ]
}
```
"""

# تنظیمات صفحه Streamlit
st.set_page_config(page_title="زبان‌مند", layout="wide")
st.markdown("""
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
<style>
body, html {
    direction: RTL;
    unicode-bidi: bidi-override;
    text-align: right;
    font-family: Vazirmatn, sans-serif !important;
    background-color: #f5f5f5;
}
.stApp {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
.chat-message {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 10px;
    max-width: 70%;
}
.chat-message.user {
    background-color: #007bff;
    color: white;
    margin-left: auto;
}
.chat-message.assistant {
    background-color: #e9ecef;
    color: black;
    margin-right: auto;
}
.stTextInput > div > div > input {
    border: 1px solid #ced4da;
    border-radius: 25px;
    padding: 10px 20px;
    font-size: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    background-color: white;
}
.stTextInput {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 700px;
    z-index: 100;
}
.admin-link {
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 14px;
}
.admin-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}
.stForm {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.stTextArea > div > div > textarea {
    border: 1px solid #ced4da;
    border-radius: 10px;
    padding: 10px;
    font-family: Vazirmatn, sans-serif;
}
@media (prefers-color-scheme: dark) {
    body, html {
        background-color: #1a1a1a;
    }
    .stApp {
        background-color: #1a1a1a;
    }
    .chat-message.user {
        background-color: #0a6bff;
    }
    .chat-message.assistant {
        background-color: #2c2c2c;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #2c2c2c;
        color: white;
        border-color: #444;
    }
    .stForm {
        background-color: #2c2c2c;
    }
    .stTextArea > div > div > textarea {
        background-color: #2c2c2c;
        color: white;
        border-color: #444;
    }
}
</style>
""", unsafe_allow_html=True)

# مدیریت وضعیت لاگین
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'system_instruction' not in st.session_state:
    st.session_state.system_instruction = default_system_instruction
if 'model' not in st.session_state:
    st.session_state.model = initialize_model(st.session_state.system_instruction)

# تابع برای بررسی لاگین
def check_login(username, password):
    return username == "admin" and password == "admin123"

# صفحه لاگین
def login_page():
    st.title("ورود به پنل ادمین")
    with st.form(key="login_form", clear_on_submit=True):
        username = st.text_input("نام کاربری")
        password = st.text_input("رمز عبور", type="password")
        submit_button = st.form_submit_button("ورود")
        if submit_button:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.success("ورود با موفقیت انجام شد!")
                st.experimental_rerun()
            else:
                st.error("نام کاربری یا رمز عبور اشتباه است.")

# صفحه پنل ادمین
def admin_panel():
    st.title("پنل ادمین")
    st.subheader("ویرایش دستورالعمل سیستم")
    
    with st.form(key="system_instruction_form"):
        new_instruction = st.text_area(
            "دستورالعمل سیستم",
            value=st.session_state.system_instruction,
            height=400
        )
        submit_button = st.form_submit_button("ذخیره تغییرات")
        
        if submit_button:
            try:
                json_start = new_instruction.find('```json')
                if json_start != -1:
                    json_end = new_instruction.find('```', json_start + 7)
                    if json_end != -1:
                        json_str = new_instruction[json_start + 7:json_end].strip()
                        json.loads(json_str)
                
                st.session_state.system_instruction = new_instruction
                st.session_state.model = initialize_model(new_instruction)
                st.session_state.chat_session = st.session_state.model.start_chat(history=[])
                st.success("دستورالعمل سیستم با موفقیت به‌روزرسانی شد!")
            except json.JSONDecodeError:
                st.error("JSON در دستورالعمل سیستم معتبر نیست. لطفاً بررسی کنید.")
            except Exception as e:
                st.error(f"خطا در به‌روزرسانی دستورالعمل: {str(e)}")
    
    if st.button("خروج"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# صفحه اصلی چت
def main_page():
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""
    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = st.session_state.model.start_chat(history=[])
    if 'i' not in st.session_state:
        st.session_state.i = 0

    def submit():
        st.session_state.prompt = st.session_state.user_input
        st.session_state.user_input = ""

    st.text_input("", placeholder="چیزی بپرسید...", on_change=submit, key="user_input")

    if 'started' not in st.session_state:
        response = st.session_state.chat_session.send_message("شروع مکالمه")
        st.session_state.started = True
        st.session_state.initial_response = response.text

    st.title("زبان‌مند")
    st.markdown(st.session_state.initial_response)

    while st.session_state.i < len(st.session_state.chat_session.history):
        message = st.session_state.chat_session.history[st.session_state.i]
        if message.role == "user":
            if message.parts[0].text == "شروع مکالمه":
                st.session_state.i += 1
                continue
            with st.container():
                st.markdown(f'<div class="chat-message user">{message.parts[0].text}</div>', unsafe_allow_html=True)
        else:
            if message.parts[0].text != st.session_state.initial_response:
                st.markdown(f'<div class="chat-message assistant">{message.parts[0].text}</div>', unsafe_allow_html=True)
            else:
                st.session_state.i += 1
                continue
        st.session_state.i += 1

    if st.session_state.prompt and 'started' in st.session_state:
        with st.container():
            st.markdown(f'<div class="chat-message user">{st.session_state.prompt}</div>', unsafe_allow_html=True)
        response = st.session_state.chat_session.send_message(st.session_state.prompt)
        st.markdown(f'<div class="chat-message assistant">{response.text}</div>', unsafe_allow_html=True)
        st.session_state.prompt = ""

# مدیریت صفحات
if st.session_state.logged_in:
    admin_panel()
else:
    if st.query_params.get("page") == ["admin"]:
        login_page()
    else:
        main_page()

# لینک به پنل ادمین
if not st.session_state.logged_in and st.query_params.get("page") != ["admin"]:
    st.markdown('<a href="?page=admin" class="admin-link">ورود به پنل ادمین</a>', unsafe_allow_html=True)
