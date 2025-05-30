import google.generativeai as genai
import streamlit as st

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
    system_instruction="""شما دستیار هوشمند آموزشگاه زبان «زبانزد» هستید. آدرس سایت آموزشگاه: https://zabanzadacademy.ir/

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
)

# تنظیمات صفحه Streamlit
st.set_page_config(page_title="از زبانزد بپرس", layout="wide")
st.markdown("""
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
<style>
body, html {
    direction: RTL;
    unicode-bidi: bidi-override;
    text-align: right;
    font-family: Vazirmatn, sans-serif !important;
}
p, div, input, label, h1, h2, h3, h4, h5, h6 {
    direction: RTL;
    text-align: right;
    font-family: Vazirmatn, sans-serif !important;
}
.stTextInput > div > div > input {
    direction: RTL;
    font-family: Vazirmatn, sans-serif !important;
}
.chat-container {
    max-height: 70vh;
    overflow-y: auto;
    padding: 10px;
    margin-bottom: 100px;
}
</style>
""", unsafe_allow_html=True)

# مدیریت وضعیت (state) برنامه
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.chat_history = []  # لیست برای ذخیره تاریخچه پیام‌ها
    st.session_state.initialized = False

# پیام خوش‌آمدگویی اولیه
if not st.session_state.initialized:
    response = st.session_state.chat_session.send_message("شروع مکالمه")
    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
    st.session_state.initialized = True

# عنوان برنامه
st.title("زبان‌مند")
st.markdown("دستیار هوشمند آموزشگاه زبانزد - از ما درباره کلاس‌ها یا هر چیز دیگری بپرسید!")

# نمایش تاریخچه چت در یک ظرف با قابلیت اسکرول
with st.container():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

# بخش ورودی کاربر
user_input = st.text_input("", placeholder="چیزی بپرسید", key="user_input")

# پردازش ورودی کاربر
if user_input:
    # افزودن پیام کاربر به تاریخچه
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # ارسال پیام به مدل و دریافت پاسخ
    response = st.session_state.chat_session.send_message(user_input)
    
    # افزودن پاسخ مدل به تاریخچه
    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
    
    # رفرش صفحه برای نمایش پیام جدید
    st.rerun()
