import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_stock_report(receiver_email, subject, content_html):
    smtp_server = "smtp.mail.yahoo.com"
    smtp_port = 465
    sender_email = "tsekachun1992@yahoo.com.hk"
    app_password = "ujqymbbtagfzsksh" # 您的 Yahoo 應用程式密碼

    message = MIMEMultipart()
    message["From"] = f"AI 交易助手 <{sender_email}>"
    message["To"] = tsekachun1992@gmail.com
    message["Subject"] = subject
    message.attach(MIMEText(content_html, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"❌ 郵件發送錯誤: {e}")
        return False
