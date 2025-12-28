from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime
import logging


# Загружаем переменные окружения
load_dotenv()
# Явно указываем кодировку для .env файла
load_dotenv(encoding='utf-8')

SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# Lifespan async context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up...")
    yield
    print("App shutting down...")


app = FastAPI(
    title="Modern Portfolio 2025",
    description="A sleek portfolio landing page built with FastAPI new features.",
    version="1.0.0",
    openapi_version="3.1.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Pydantic v2 model
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str

    @property
    def summary(self) -> str:
        return f"Message from {self.name}: {self.message[:50]}..."


# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "alimpievne@gmail.com")


async def send_email(msg: ContactMessage):
    """Send email notification about new contact form submission"""
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"New Contact Form Submission from {msg.name}"
        message["From"] = SMTP_USERNAME
        message["To"] = RECIPIENT_EMAIL

        # Create HTML version
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #0ea5e9;">New Contact Form Submission</h2>
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; border-left: 4px solid #0ea5e9;">
                <p><strong>Name:</strong> {msg.name}</p>
                <p><strong>Email:</strong> {msg.email}</p>
                <p><strong>Message:</strong></p>
                <div style="background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-top: 10px;">
                    {msg.message}
                </div>
            </div>
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
                This email was sent from your portfolio website contact form.
            </p>
        </body>
        </html>
        """

        # Create plain text version
        text = f"""
        New Contact Form Submission

        Name: {msg.name}
        Email: {msg.email}
        Message:
        {msg.message}

        This email was sent from your portfolio website contact form.
        """

        # Add both plain text and HTML parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, message.as_string())

        print(f"[EMAIL] Successfully sent to {RECIPIENT_EMAIL}")

        # Also send auto-reply to the sender
        await send_auto_reply(msg)

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
        # Don't raise exception to avoid breaking the background task


async def send_auto_reply(msg: ContactMessage):
    """Send auto-reply to the person who submitted the form"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Thank you for contacting me!"
        message["From"] = SMTP_USERNAME
        message["To"] = msg.email

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #0ea5e9; margin-bottom: 10px;">Thank You!</h1>
                    <p style="color: #666;">I've received your message and will get back to you soon.</p>
                </div>

                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <p><strong>Your message:</strong></p>
                    <div style="background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin: 10px 0;">
                        {msg.message}
                    </div>
                </div>

                <div style="border-top: 2px solid #0ea5e9; padding-top: 20px; margin-top: 30px;">
                    <p><strong>Best regards,</strong><br>
                    Artem Alimpiev<br>
                    Python Developer</p>
                    <p style="color: #666; font-size: 14px;">
                        This is an automated response. Please don't reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text = f"""
        Thank You!

        Hi {msg.name},

        Thank you for reaching out! I've received your message and will get back to you as soon as possible.

        Your message:
        {msg.message}

        Best regards,
        Artem Alimpiev
        Python Developer

        This is an automated response. Please don't reply to this email.
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, msg.email, message.as_string())

        print(f"[AUTO-REPLY] Sent to {msg.email}")

    except Exception as e:
        print(f"[AUTO-REPLY ERROR] Failed to send auto-reply: {e}")


# Root route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    projects = [
        {"title": "Python Mentor Bot", "desc": "AI-powered app",
         "link": "https://github.com/Artem7898/Python-Mentor-Bot"},
        {"title": "Data Visualization", "desc": "Data analysis and visualization",
         "link": "https://github.com/Artem7898/Data_visualization"},
        {"title": "Aggregator Web App", "desc": "Web application aggregator",
         "link": "https://github.com/Artem7898/Aggregator-Web-App"},
    ]
    skills = ["Python", "FastAPI", "Django", "Web Dev", "Cloud", "GIT", "PostgreSQL"]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": "Artem Alimpiev",
        "about": "I'm a Python developer specializing in modern web APIs and AI integrations.",
        "projects": projects,
        "skills": skills
    })
    # Замените строки 214-230 на это:


@app.post("/contact")
async def contact(
        name: str = Form(...),
        email: str = Form(...),
        message: str = Form(...),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Обработка контактной формы с раздельной отправкой писем"""
    # Валидация с помощью Pydantic v2
    try:
        msg = ContactMessage(name=name, email=email, message=message)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # Разделяем отправку на две независимые фоновые задачи
    background_tasks.add_task(send_notification_email, msg)  # Уведомление вам
    background_tasks.add_task(send_auto_reply, msg)   # Автоответ пользователю

    print(f"📩 Получено сообщение от {msg.name} ({msg.email}): {msg.summary}")
    return {
        "status": "success",
        "message": "Сообщение отправлено! Вы получите подтверждение на email.",
        "summary": msg.summary
    }


async def send_notification_email(msg: ContactMessage):
    """Отправка уведомления администратору"""
    try:
        logger.info(f"📨 Начинаем отправку уведомления для {msg.name}")
        logger.debug(f"SMTP конфиг: {SMTP_SERVER}:{SMTP_PORT}, user: {SMTP_USERNAME}")

        message = MIMEMultipart("alternative")
        message["Subject"] = f"📨 Новое сообщение от {msg.name}"
        message["From"] = SMTP_USERNAME
        message["To"] = RECIPIENT_EMAIL

        # Проверяем конфигурацию
        if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, RECIPIENT_EMAIL]):
            logger.error("❌ Не все SMTP переменные настроены!")
            return

        # Текст письма (упрощенный для теста)
        text = f"""Новое сообщение с портфолио
        Имя: {msg.name}
        Email: {msg.email}
        Сообщение: {msg.message}
        """

        message.attach(MIMEText(text, "plain"))

        logger.info(f"🔗 Подключаемся к {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            logger.info("🔐 Включаем STARTTLS...")
            server.starttls()

            logger.info(f"🔑 Авторизуемся как {SMTP_USERNAME}")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            logger.info(f"📤 Отправляем письмо на {RECIPIENT_EMAIL}")
            server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, message.as_string())
            logger.info("✅ Письмо успешно отправлено!")

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Ошибка авторизации SMTP: {e}")
        logger.error("Проверьте логин/пароль. Для Gmail используйте пароль приложения.")
    except smtplib.SMTPException as e:
        logger.error(f"❌ Ошибка SMTP: {e}")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}", exc_info=True)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)