import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


def send_verification_email(to_email, otp):
    """Send OTP verification email using Brevo SMTP."""

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("MAIL_FROM")

    # -----------------------------
    # Check configuration
    # -----------------------------

    if not smtp_host:
        raise ValueError("SMTP_HOST is missing")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME is missing")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is missing")

    if not smtp_from:
        raise ValueError("MAIL_FROM is missing")

    # -----------------------------
    # Create email
    # -----------------------------

    message = EmailMessage()

    message["Subject"] = "FINORA - Email Verification"
    message["From"] = smtp_from
    message["To"] = to_email

    message.set_content(
        f"""\
Welcome to FINORA!

Your email verification code is:

{otp}

This OTP will expire in 10 minutes.

If you did not create a FINORA account, you can safely ignore this email.

Regards,
FINORA Team
"""
    )

    # -----------------------------
    # Connect to Brevo SMTP
    # -----------------------------

    try:

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=30
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(
                message
            )

        print(
            f"OTP email sent successfully to {to_email}"
        )

        return True

    except Exception as e:

        print(
            "EMAIL ERROR:",
            e
        )

        raise