from main import app, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, RECIPIENT_EMAIL, SMTP_PASSWORD


@app.get("/email-config")
async def email_config():
    """Показать текущую конфигурацию email (без пароля)"""
    return {
        "smtp_server": SMTP_SERVER,
        "smtp_port": SMTP_PORT,
        "smtp_username": SMTP_USERNAME,
        "recipient": RECIPIENT_EMAIL,
        "password_set": bool(SMTP_PASSWORD),
        "password_contains_hash": '#' in SMTP_PASSWORD if SMTP_PASSWORD else False
    }