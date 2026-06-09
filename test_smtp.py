import os
import smtplib

from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")

SMTP_SERVER = "mail.abroado.in"
SMTP_PORT = 465

import email.utils

msg = MIMEText("Hello, this is a test email sent from the Abroado backend using Python smtplib to verify the SMTP configuration.", "plain")

msg["Subject"] = "Backend SMTP Configuration Test latest"
msg["From"] = EMAIL
msg["To"] = "shreyu3210@gmail.com"  # Change this to your Gmail to test Gmail delivery
msg["Date"] = email.utils.formatdate(localtime=True)
msg["Message-ID"] = email.utils.make_msgid()
try:
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

    server.set_debuglevel(1)

    server.login(EMAIL, PASSWORD)

    result = server.sendmail(
        EMAIL,
        "shreyu3210@gmail.com",
        msg.as_string()
    )

    print("SEND RESULT:")
    print(result)

    server.quit()

except Exception as e:
    print(e)