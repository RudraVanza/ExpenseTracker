import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")


def send_test_email():

    recipient = input("Enter email address to receive test email: ").strip()

    message = MIMEMultipart()

    message["From"] = MAIL_FROM
    message["To"] = recipient
    message["Subject"] = "Expense Tracker - Test Email"

    body = """
Hello!

This is a test email from Expense Tracker.

Your Brevo SMTP configuration is working correctly.

Regards,
Expense Tracker
"""

    message.attach(
        MIMEText(body, "plain")
    )

    try:

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )

            server.sendmail(
                MAIL_FROM,
                recipient,
                message.as_string()
            )

        print("\n✅ Email sent successfully!")

    except Exception as e:

        print("\n❌ Email failed!")
        print("Error:", e)


if __name__ == "__main__":
    send_test_email()