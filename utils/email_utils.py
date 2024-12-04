from flask_mail import Message
from app import mail
from flask import current_app


def send_email(subject, recipients, body, attachments=None):
    """
    Envoie un email via Flask-Mail.
    """
    try:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        msg = Message(subject, sender=sender, recipients=recipients, body=body)
        if attachments:
            for attachment in attachments:
                with open(attachment, 'rb') as file:
                    msg.attach(
                        filename=attachment.split(
                            "/")[-1],  # Extract the filename
                        content_type="application/pdf",  # Adjust as needed
                        data=file.read()
                    )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
