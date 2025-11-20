#!/usr/bin/env python3
"""Test SMTP credentials directly"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "supachatglobal@gmail.com"
SMTP_PASSWORD = "nwyhpclsknnwsbhr"

print("Testing SMTP credentials...")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"Username: {SMTP_USERNAME}")
print(f"Password: {'*' * len(SMTP_PASSWORD)}")
print()

try:
    # Create test message
    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_USERNAME
    msg['Subject'] = "Test Email - SMTP Credentials Verification"

    html = """
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h1 style="color: #50C878;">✓ SMTP Test Successful!</h1>
        <p>If you're reading this, the SMTP credentials are working correctly.</p>
      </body>
    </html>
    """

    html_part = MIMEText(html, 'html')
    msg.attach(html_part)

    # Send email
    print("Connecting to SMTP server...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        print("Starting TLS...")
        server.starttls()

        print("Logging in...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        print("Sending email...")
        server.send_message(msg)

    print("\n✓ SUCCESS! Email sent successfully.")
    print(f"Check inbox: {SMTP_USERNAME}")

except smtplib.SMTPAuthenticationError as e:
    print(f"\n✗ AUTHENTICATION FAILED: {e}")
    print("\nPossible issues:")
    print("1. App-specific password is incorrect")
    print("2. 2-Factor Authentication not enabled on Gmail account")
    print("3. App password was revoked or expired")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
