from fastapi import logger
from main import app, ContactMessage, send_notification_email


@app.get("/test-email-sync")
async def test_email_sync():
    """Синхронный тест отправки email (без фоновых задач)"""
    test_msg = ContactMessage(
        name="Тестовый Пользователь",
        email="test@example.com",
        message="Тестовое сообщение для проверки отправки."
    )

    try:
        logger.info("🚀 Запускаем синхронный тест отправки...")
        await send_notification_email(test_msg)
        return {"status": "success", "message": "Тест запущен, проверьте логи"}
    except Exception as e:
        logger.error(f"❌ Тест не удался: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}