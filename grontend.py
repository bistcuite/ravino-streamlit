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
st.set_page_config(page_title="از زبانزد بپرس", layout="wide")
st.markdown("""
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
<style>
body, html {
    direction: RTL;
    unicode-bidi: bidi-override;
    text-align: right;
    font-family: Vazirmatn, sans-serif!important;
}
p, div, input, label, h1, h2, h3, h4, h5, h6 {
    direction: RTL;
    text-align: right;
    font-family: Vazirmatn, sans-serif!important;
}
.stTextInput {
    position: fixed;
    bottom: 0;
    padding-bottom: 45px;
    padding-right: 20px;
    padding-left: 20px;
    right: 0;
    left: 0;
    width: 100%;
    margin-left: 1rem;
    z-index: 100;
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
    # در عمل باید از روش‌های امن‌تر (مثل هش کردن) استفاده شود
    return username == "admin" and password == "admin123"

# صفحه لاگین
def login_page():
    st.title("ورود به پنل ادمین")
    with st.form(key="login_form"):
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
    st.subheader("ویرایش System Instruction")
    
    with st.form(key="system_instruction_form"):
        new_instruction = st.text_area(
            "دستورالعمل سیستم",
            value=st.session_state.system_instruction,
            height=400
        )
        submit_button = st.form_submit_button("ذخیره تغییرات")
        
        if submit_button:
            try:
                # بررسی معتبر بودن JSON در صورت وجود
                json_start = new_instruction.find('```json')
                if json_start != -1:
                    json_end = new_instruction.find('```', json_start + 7)
                    if json_end != -1:
                        json_str = new_instruction[json_start + 7:json_end].strip()
                        json.loads(json_str)  # بررسی صحت JSON
                
                # به‌روزرسانی system instruction و مدل
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
    # مدیریت وضعیت (state) برنامه
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""
    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = st.session_state.model.start_chat(history=[])
    if 'i' not in st.session_state:
        st.session_state.i = 0

    # تابع برای ارسال پیام
    def submit():
        st.session_state.prompt = st.session_state.user_input
        st.session_state.user_input = ""

    # بخش ورودی کاربر
    st.text_input("", placeholder="چیزی بپرسید", on_change=submit, key="user_input")

    # شروع داستان (فقط یک بار اجرا می‌شود)
    if 'started' not in st.session_state:
        response = st.session_state.chat_session.send_message("شروع مکالمه")
        st.session_state.started = True
        st.session_state.initial_response = response.text

    # عنوان برنامه
    st.title("زبان‌مند")
    st.markdown(st.session_state.initial_response)

    # نمایش تاریخچه چت (به جز پیام اولیه)
    while st.session_state.i < len(st.session_state.chat_session.history):
        message = st.session_state.chat_session.history[st.session_state.i]
        if message.role == "user":
            if message.parts[0].text == "شروع مکالمه":
                st.session_state.i += 1
                continue
            with st.chat_message("user"):
                st.write(message.parts[0].text)
        else:
            if message.parts[0].text != st.session_state.initial_response:
                st.write(message.parts[0].text)
            else:
                st.session_state.i += 1
                continue
        st.session_state.i += 1

    # بررسی ورودی کاربر و تولید پاسخ
    if st.session_state.prompt and 'started' in st.session_state:
        response = st.session_state.chat_session.send_message(st.session_state.prompt)
        with st.chat_message("user"):
            st.write(st.session_state.prompt)
        st.write(response.text)
        st.session_state.prompt = ""

# مدیریت صفحات
if st.session_state.logged_in:
    admin_panel()
else:
    if st.query_params.get("page") == ["admin"]:
        login_page()
    else:
        main_page()

# لینک به پنل ادمین در صفحه اصلی
if not st.session_state.logged_in and st.query_params.get("page") != ["admin"]:
    st.markdown("[ورود به پنل ادمین](?page=admin)")
