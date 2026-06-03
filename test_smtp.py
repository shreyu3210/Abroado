import os
import smtplib

from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")

SMTP_SERVER = "mail.abroado.in"
SMTP_PORT = 465

msg = MIMEText("SMTP debug test")

msg["Subject"] = "Debug Test"
msg["From"] = EMAIL
msg["To"] = "test@abroado.in"

try:
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

    server.set_debuglevel(1)

    server.login(EMAIL, PASSWORD)

    result = server.sendmail(
        EMAIL,
        "test@abroado.in",
        msg.as_string()
    )

    print("SEND RESULT:")
    print(result)

    server.quit()

except Exception as e:
    print(e)