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
  system_instruction="شما یک راوی داستان تعاملی هستید و داستان را برای کاربر روایت می‌کنید. همیشه از دوم شخص (تو) برای مخاطب استفاده کن.  \nکاربر شخصیت اصلی داستان است و شما باید هر صحنه را از دید او توصیف کنید. هنگام روایت، هیچگاه از سوم شخص (او) برای کاربر استفاده نکن. تمام توصیفات باید با جزئیات و حس ماجراجویی همراه باشد تا کاربر احساس کند که واقعاً در دل داستان حضور دارد.  \n\nبرای شروع:  \nتو، آریال، تنها بازمانده از محفل اشباح سیاه، با قدم‌های محکم در دل شبی مه‌آلود و پرخطر، به سوی خرابه‌های قدیمی حرکت می‌کنی. هر قدمت صدای خش‌خش برگ‌های خشک زیر پا را به گوش می‌رساند. شنلت در باد سرد شبانه به اهتزاز درمی‌آید و تاریکی اطراف، همچون سایه‌هایی زنده تو را احاطه کرده است. هیچ انتخابی در این لحظه ساده نیست، اما می‌دانی که باید استاد داسنیرو را پیدا کنی تا سرزمینت را از دست جادوگر شوم، آلتایر، نجات دهی.  \n\nیادآوری مهم:  \n- همیشه روایت را به زبان فارسی و از دوم شخص (تو) ادامه بده.  \n- تنها در اولین پیام، نام شخصیت (آریال) به او یادآوری شود.  \n- هرگز مستقیماً از کاربر نپرس که چه می‌خواهد بکند یا به او راه پیشنهاد نکن.  \n- فقط صحنه را توصیف کن و ماجراجویی را پیش ببر، به گونه‌ای که کاربر خود تصمیم بگیرد.  \n- کاربر را به نامش نخوان. فکر کن داری یک رمان فانتزی با روایت دوم شخص می‌نویسی.  \n",
)
# تنظیمات صفحه Streamlit
st.set_page_config(page_title="راوینو | داستان را خودت روایت کن!")
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
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
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
            z-index:100;
      }
    </style>
""", unsafe_allow_html=True)

# مدیریت وضعیت (state) برنامه
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

if 'i' not in st.session_state:
    st.session_state.i = 0

# تابع برای ارسال پیام
def submit():
    st.session_state.prompt = st.session_state.user_input
    st.session_state.user_input = ""

# بخش ورودی کاربر
st.text_input("", placeholder="چه می‌کنید؟", on_change=submit, key="user_input")

# شروع داستان (فقط یک بار اجرا می‌شود)
if 'started' not in st.session_state:
    response = st.session_state.chat_session.send_message("شروع داستان")
    st.session_state.started = True
    st.session_state.initial_response = response.text

# عنوان برنامه
st.title("جنگ بی‌نهایت")
st.markdown(st.session_state.initial_response)

# st.write(st.session_state.initial_response)
# نمایش تاریخچه چت (به جز پیام اولیه)

while st.session_state.i < len(st.session_state.chat_session.history):
    message = st.session_state.chat_session.history[st.session_state.i]

    if message.role == "user":
        if message.parts[0].text == "شروع داستان":
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
    # ارسال پیام جدید به مدل
    response = st.session_state.chat_session.send_message(st.session_state.prompt)
    
    # نمایش پیام کاربر
    with st.chat_message("user"):
        st.write(st.session_state.prompt)
    
    # نمایش پاسخ مدل
    st.write(response.text)
    print(st.session_state.chat_session.history)
    # پاک کردن ورودی پس از ارسال
    st.session_state.prompt = ""
