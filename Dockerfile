# انتخاب تصویر پایه مناسب برای Python
FROM python:3.9-slim

# تنظیم متغیرهای محیطی برای بهینه‌سازی Streamlit
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_HEADLESS=true

# تنظیم مسیر کاری
WORKDIR /app

# کپی کردن فایل‌های مورد نیاز پروژه
COPY . /app

# نصب pip و کتابخانه‌های مورد نیاز
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# باز کردن پورت مورد نیاز برای Streamlit
EXPOSE 8501

# فرمان اجرای Streamlit
CMD ["streamlit", "run", "grontend.py"]
