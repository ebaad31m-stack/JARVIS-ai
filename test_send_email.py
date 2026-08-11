from core.gmail_manager import send_email


to_email = input("Send test email to: ").strip()

subject = "JARVIS Email Test"

body = """
Hello!

This is a test email sent by JARVIS.

If you received this, the Gmail system is working.
"""

print("Sending email...")

success = send_email(
    to_email,
    subject,
    body
)

if success:
    print("SUCCESS! Email sent.")
else:
    print("FAILED! Check the error above.")