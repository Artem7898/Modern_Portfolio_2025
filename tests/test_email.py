from fastapi import HTTPException
from main import app, ContactMessage, send_notification_email, send_auto_reply_email


@app.get("/test-email")
async def test_email():
    """Тестирование отправки email"""
    test_msg = ContactMessage(
        name="Тестовый Пользователь",
        email="test@example.com",
        message="Это тестовое сообщение для проверки отправки email."
    )

    try:
        await send_notification_email(test_msg)
        await send_auto_reply_email(test_msg)
        return {"status": "success", "message": "Тестовые письма отправлены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))