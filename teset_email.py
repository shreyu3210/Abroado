import os
import resend
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your API key
resend.api_key = os.getenv("RESEND_API_KEY")

def send_test_email():
    try:
        params = {
            "from": "onboarding@resend.dev",
            "to": "shreyu3210@gmail.com",
            "subject": "Test Email from Resend",
            "html": "<strong>It works!</strong><p>This is a test email sent from Python using the Resend API.</p>"
        }

        email = resend.Emails.send(params)
        print("Email sent successfully!")
        print("Response:", email)

    except Exception as e:
        print("Failed to send email.")
        print("Error:", str(e))

if __name__ == "__main__":
    send_test_email()
