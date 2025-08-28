
GENAI_API_KEY = "AIzaSyAGHfM_nN3N9no9Ox1cIMsEn1KvyeFE_F4"  # کلید API خود را وارد کنید
# -*- coding: utf-8 -*-
import os
import io
import base64
import mimetypes
from typing import List, Dict, Any

import streamlit as st
from google import genai
from google.genai import types

APP_TITLE = "چت‌بات Gemini (متنی + تصویری)"
MODEL_IMAGE = "gemini-2.5-flash-image-preview"  # پشتیبانی ورودی/خروجی تصویر
MODEL_TEXT = "gemini-2.5-flash"                 # پشتیبان برای متن‌محور

# ---------- استایل: فونت وزیرمتن + راست‌چین ----------
st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="centered")
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/npm/vazirmatn@33.003/Vazirmatn-font-face.css');
html, body, [class*="css"] {
  font-family: Vazirmatn, system-ui, -apple-system, Segoe UI, Roboto, Arial !important;
  direction: rtl;
}
[data-testid="stSidebar"] * { direction: rtl; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title(APP_TITLE)
st.caption("ورودی متن و تصویر بگیر، خروجی متن و تصویر تحویل بگیر 😎")

# ---------- کلاینت ----------
def get_client() -> genai.Client:
    return genai.Client(api_key="AIzaSyAGHfM_nN3N9no9Ox1cIMsEn1KvyeFE_F4")

client = get_client()

# ---------- وضعیت چت ----------
if "history" not in st.session_state:
    st.session_state.history: List[Dict[str, Any]] = []   # هر آیتم: {"role": "user"/"assistant", "text": str, "images": [bytes...]}

# ---------- سایدبار ----------
with st.sidebar:
    st.subheader("ورودی تصویر")
    uploaded_images = st.file_uploader(
        "می‌تونی یک یا چند عکس اضافه کنی:",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="عکس‌ها به‌عنوان بخشی از پیام ارسال می‌شن."
    )
    st.markdown("---")
    use_image_model = st.toggle("اجبار به مدل تصویری (برای تولید/ویرایش تصویر)", value=True,
                                help="اگر خاموش باشه و تصویری نفرستی، از مدل متنی سریع استفاده می‌کنه.")

# ---------- نمایش تاریخچه ----------
for msg in st.session_state.history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        if msg.get("text"):
            st.markdown(msg["text"])
        for img_bytes in msg.get("images", []):
            st.image(img_bytes, use_container_width=True)

# ---------- ورودی چت ----------
user_text = st.chat_input("هر چی می‌خوای بپرس یا توضیح بده...")

def to_parts_from_images(uploaded_files) -> List[types.Part]:
    parts = []
    for f in uploaded_files or []:
        data = f.read()
        # حدس MIME از خود فایل‌خوان یا از اسم
        mime = getattr(f, "type", None) or mimetypes.guess_type(f.name)[0] or "image/jpeg"
        parts.append(types.Part.from_bytes(mime_type=mime, data=data))
    return parts

def build_contents_from_history(history: List[Dict[str, Any]]) -> List[types.Content]:
    contents: List[types.Content] = []
    for m in history:
        parts = []
        if m.get("text"):
            parts.append(types.Part.from_text(text=m["text"]))
        for img in m.get("images", []):
            # این‌ها bytes هستن؛ MIME رو به صورت پیشفرض jpeg می‌ذاریم چون برای کانتکست اهمیتی نداره
            parts.append(types.Part.from_bytes(mime_type="image/jpeg", data=img))
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=parts))
    return contents

def parse_response_for_text_and_images(resp) -> (str, List[bytes]):
    """
    از پاسخ مدل، متن نهایی و لیستی از بایت‌های تصویر رو استخراج می‌کنه.
    """
    acc_text = []
    images: List[bytes] = []
    if not resp or not getattr(resp, "candidates", None):
        return "", images

    cand = resp.candidates[0]
    if not cand or not getattr(cand, "content", None) or not cand.content.parts:
        return "", images

    for p in cand.content.parts:
        # متن
        if getattr(p, "text", None):
            acc_text.append(p.text)
        # تصویر (inline_data)
        inline = getattr(p, "inline_data", None)
        if inline and getattr(inline, "data", None):
            # google-genai بایت خام می‌ده، لازم نیست دوباره base64 دیکد کنیم
            images.append(inline.data)

    # بعضی پاسخ‌ها .text ترکیبی هم دارند
    if hasattr(resp, "text") and resp.text:
        acc_text.append(resp.text)

    return "\n".join(t for t in acc_text if t), images

def generate_reply(user_text: str, image_files):
    """
    یک بار درخواست می‌زند (non-stream) تا با مدل تصویری، خروجی متن/عکس را بگیریم.
    برای پایداری بیشتر از call غیر استریم استفاده شده.
    """
    # محتوای گفتگو تا الان + پیام جدید کاربر
    history_contents = build_contents_from_history(st.session_state.history)

    current_user_parts = []
    if user_text:
        current_user_parts.append(types.Part.from_text(text=user_text))
    current_user_parts.extend(to_parts_from_images(image_files))

    # اگر کاربر چیزی نفرستاده، هیچی نفرست
    if not current_user_parts:
        return None

    # لیست نهایی محتوا
    contents = history_contents + [types.Content(role="user", parts=current_user_parts)]

    # اگر تصویر داریم یا کاربر خواسته از مدل تصویری استفاده بشه
    use_image = bool(image_files) or use_image_model
    model = MODEL_IMAGE if use_image else MODEL_TEXT

    # برای مدل تصویری بهتره مودالیتی‌ها رو مشخص کنیم
    cfg = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"] if use_image else ["TEXT"]
    )

    # فراخوانی
    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=cfg,
    )
    return resp

if user_text is not None:
    # 1) پیام کاربر را به تاریخچه اضافه کن
    user_images_bytes = [f.read() for f in (uploaded_images or [])]  # برای ذخیره در تاریخچه باید bytes خام داشته باشیم
    st.session_state.history.append({
        "role": "user",
        "text": user_text,
        "images": user_images_bytes
    })

    # 2) نمایش فوری پیام کاربر
    with st.chat_message("user"):
        if user_text:
            st.markdown(user_text)
        for b in user_images_bytes:
            st.image(b, use_container_width=True)

    # 3) تماس با مدل
    with st.chat_message("assistant"):
        try:
            resp = generate_reply(user_text, uploaded_images)
            text_out, images_out = parse_response_for_text_and_images(resp)

            # نمایش خروجی
            if text_out:
                st.markdown(text_out)
            for i, img_bytes in enumerate(images_out):
                st.image(io.BytesIO(img_bytes), use_container_width=True, caption=f"خروجی تصویر {i+1}")

            # 4) ذخیره پاسخ در تاریخچه
            st.session_state.history.append({
                "role": "assistant",
                "text": text_out or "",
                "images": images_out or []
            })

        except Exception as e:
            # خطای مفید نشون بده
            st.error(f"خطا در فراخوانی سرویس: {e}")
            st.info(
                "اگر پیام «client error» دیدی، معمولاً به یکی از این دلایل است:\n"
                "• متغیر محیطی `GOOGLE_API_KEY` تنظیم نشده یا مقدارش درست نیست.\n"
                "• به مدل‌های preview مثل `gemini-2.5-flash-image-preview` دسترسی نداری.\n"
                "• نوع ورودی/خروجی با قابلیت‌های مدل نمی‌خونه."
            )
