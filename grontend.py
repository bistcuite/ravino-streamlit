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

---

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
""",
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
.card {
    background-color: #f5f5f5;
    border-radius: 10px;
    padding: 15px;
    margin: 10px;
    text-align: center;
    cursor: pointer;
    transition: background-color 0.3s;
}
.card:hover {
    background-color: #e0e0e0;
}
.course-box {
    background-color: #e8f4f8;
    border: 1px solid #007bzff;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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

# تابع برای نمایش دوره‌ها در قالب باکس
def display_course(course):
    st.markdown(f"""
    <div class='course-box'>
        <h3>{course['نام']}</h3>
        <p><strong>سطح:</strong> {course['سطح']}</p>
        <p><strong>توضیح:</strong> {course['توضیح']}</p>
        <p><strong>مدرس:</strong> {course['مدرس']}</p>
        <p><strong>قیمت:</strong> {course['قیمت']:,} تومان</p>
        <p><strong>تعداد جلسات:</strong> {course['تعداد جلسات']}</p>
        <p><strong>زمان‌بندی:</strong> {course['زمان‌بندی']}</p>
        <p><strong>ظرفیت باقی‌مانده:</strong> {course['ظرفیت باقی‌مانده']}</p>
    </div>
    """, unsafe_allow_html=True)

# کارت‌های پیشنهادی
st.title("زبان‌مند")
st.markdown("### پیشنهادهای ویژه برای شما")
cols = st.columns(3)
suggestions = [
    {"text": "معرفی دوره‌های آموزشی", "prompt": "دوره‌های آموزشی زبانزد را معرفی کن"},
    {"text": "آزمون تعیین سطح", "prompt": "چطور می‌توانم در آزمون تعیین سطح شرکت کنم؟"},
    {"text": "پرسش درباره تلفظ", "prompt": "چگونه می‌توانم تلفظ کلمات انگلیسی را بهبود دهم؟"}
]

for i, suggestion in enumerate(suggestions):
    with cols[i % 3]:
        if st.button(suggestion["text"], key=f"suggestion_{i}"):
            st.session_state.prompt = suggestion["prompt"]

# شروع داستان (فقط یک بار اجرا می‌شود)
if 'started' not in st.session_state:
    response = st.session_state.chat_session.send_message("شروع مکالمه")
    st.session_state.started = True
    st.session_state.initial_response = response.text

# نمایش پیام خوش‌آمدگویی
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
            # بررسی اگر پاسخ شامل معرفی دوره‌ها باشد
            if "دوره‌ها" in message.parts[0].text or "کلاس‌ها" in message.parts[0].text:
                for course in eval(model.system_instruction.split("```json")[1].split("```")[0])["کلاس‌ها"]:
                    display_course(course)
            else:
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
    if "دوره‌ها" in st.session_state.prompt or "کلاس‌ها" in st.session_state.prompt:
        for course in eval(model.system_instruction.split("```json")[1].split("```")[0])["کلاس‌ها"]:
            display_course(course)
    else:
        st.write(response.text)
    
    # پاک کردن ورودی پس از ارسال
    st.session_state.prompt = ""

# بخش ورودی کاربر
st.text_input("", placeholder="چیزی بپرسید", on_change=submit, key="user_input")
