import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "mustafakuasha2003@gmail.com"
SMTP_PASS = "sklxvnoeaymlhler"   # Gmail App Password, not real gmail password

def send_otp_email(to_email: str, otp: str):
    msg = MIMEText(f"""
    Hello,

    Your signup verification code is:

        {otp}

    This code expires in 10 minutes. Do not share it with anyone.
    """)
    msg["Subject"] = "Your Signup OTP"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())