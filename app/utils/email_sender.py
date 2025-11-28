import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

MOT_DE_PASSE_EMAIL = os.getenv("MOT_DE_PASSE_EMAIL_SUBJECT")

def send_reset_email(to_email: str, reset_link: str):
    sender_email = "nasmihael@gmail.com"
    sender_password =MOT_DE_PASSE_EMAIL  # pas ton mot de passe normal

    msg = MIMEText(f"""
    Bonjour,

    Cliquez ici pour réinitialiser votre mot de passe :
    {reset_link}

    Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
    """)

    msg["Subject"] = "Réinitialisation de mot de passe"
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
