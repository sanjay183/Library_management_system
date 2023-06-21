import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from secret_token import host,password

def send_email(sender_email, receiver_email, subject, message):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message to the email body
    msg.attach(MIMEText(message, 'plain'))
    print(host)
    print(password)
    # SMTP configuration
    smtp_host = host
    smtp_port = 587
    smtp_username = sender_email
    smtp_password = password

    # Create a secure SSL/TLS connection
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

# Usage example



