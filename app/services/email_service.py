import os
import smtplib
import json
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, body_html: str, from_email: str = None):
    try:
        sender_email = from_email or os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASS")
        smtp_server = "mail.abroado.in"
        smtp_port = 465

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid()

        part = MIMEText(body_html, "html")
        msg.attach(part)

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def get_template(template_name: str) -> dict:
    template_path = os.path.join(os.path.dirname(__file__), "..", "email_templates", f"{template_name}.json")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not load template {template_name}: {e}")
        return {}
