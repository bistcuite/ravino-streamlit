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
""",
)
# تنظیمات صفحه Streamlit
st.set_page_config(page_title="از زبانزد بپرس")
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
st.text_input("", placeholder="چیزی بپرسید", on_change=submit, key="user_input")

# شروع داستان (فقط یک بار اجرا می‌شود)
if 'started' not in st.session_state:
    response = st.session_state.chat_session.send_message("شروع مکالمه")
    st.session_state.started = True
    st.session_state.initial_response = response.text

# عنوان برنامه
st.title("زبان‌مند")
st.markdown(st.session_state.initial_response)

# st.write(st.session_state.initial_response)
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

# import time
# import os
# import joblib
# import streamlit as st
# import google.generativeai as genai
# from dotenv import load_dotenv
# load_dotenv()
# genai.configure(api_key="AIzaSyDuExne7oG9NnfNZeaqDOSXVtxUdau7IBU")

# new_chat_id = f'{time.time()}'
# MODEL_ROLE = 'ai'
# AI_AVATAR_ICON = '✨'

# # Create a data/ folder if it doesn't already exist
# try:
#     os.mkdir('data/')
# except:
#     # data/ folder already exists
#     pass

# # Load past chats (if available)
# try:
#     past_chats: dict = joblib.load('data/past_chats_list')
# except:
#     past_chats = {}

# # Sidebar allows a list of past chats
# with st.sidebar:
#     st.write('# Past Chats')
#     if st.session_state.get('chat_id') is None:
#         st.session_state.chat_id = st.selectbox(
#             label='Pick a past chat',
#             options=[new_chat_id] + list(past_chats.keys()),
#             format_func=lambda x: past_chats.get(x, 'New Chat'),
#             placeholder='_',
#         )
#     else:
#         # This will happen the first time AI response comes in
#         st.session_state.chat_id = st.selectbox(
#             label='Pick a past chat',
#             options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
#             index=1,
#             format_func=lambda x: past_chats.get(x, 'New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
#             placeholder='_',
#         )
#     # Save new chats after a message has been sent to AI
#     # TODO: Give user a chance to name chat
#     st.session_state.chat_title = f'ChatSession-{st.session_state.chat_id}'

# st.write('# Chat with Gemini')

# # Chat history (allows to ask multiple questions)
# try:
#     st.session_state.messages = joblib.load(
#         f'data/{st.session_state.chat_id}-st_messages'
#     )
#     st.session_state.gemini_history = joblib.load(
#         f'data/{st.session_state.chat_id}-gemini_messages'
#     )
#     print('old cache')
# except:
#     st.session_state.messages = []
#     st.session_state.gemini_history = []
#     print('new_cache made')
# st.session_state.model = genai.GenerativeModel('gemini-pro')
# st.session_state.chat = st.session_state.model.start_chat(
#     history=st.session_state.gemini_history,
# )

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(
#         name=message['role'],
#         avatar=message.get('avatar'),
#     ):
#         st.markdown(message['content'])

# # React to user input
# if prompt := st.chat_input('Your message here...'):
#     # Save this as a chat for later
#     if st.session_state.chat_id not in past_chats.keys():
#         past_chats[st.session_state.chat_id] = st.session_state.chat_title
#         joblib.dump(past_chats, 'data/past_chats_list')
#     # Display user message in chat message container
#     with st.chat_message('user'):
#         st.markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append(
#         dict(
#             role='user',
#             content=prompt,
#         )
#     )
#     ## Send message to AI
#     response = st.session_state.chat.send_message(
#         prompt,
#         stream=True,
#     )
#     # Display assistant response in chat message container
#     with st.chat_message(
#         name=MODEL_ROLE,
#         avatar=AI_AVATAR_ICON,
#     ):
#         message_placeholder = st.empty()
#         full_response = ''
#         assistant_response = response
#         # Streams in a chunk at a time
#         for chunk in response:
#             # Simulate stream of chunk
#             # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
#             for ch in chunk.text.split(' '):
#                 full_response += ch + ' '
#                 time.sleep(0.05)
#                 # Rewrites with a cursor at end
#                 message_placeholder.write(full_response + '▌')
#         # Write full message with placeholder
#         message_placeholder.write(full_response)

#     # Add assistant response to chat history
#     st.session_state.messages.append(
#         dict(
#             role=MODEL_ROLE,
#             content=st.session_state.chat.history[-1].parts[0].text,
#             avatar=AI_AVATAR_ICON,
#         )
#     )
#     st.session_state.gemini_history = st.session_state.chat.history
#     # Save to file
#     joblib.dump(
#         st.session_state.messages,
#         f'data/{st.session_state.chat_id}-st_messages',
#     )
#     joblib.dump(
#         st.session_state.gemini_history,
#         f'data/{st.session_state.chat_id}-gemini_messages',
#     )
