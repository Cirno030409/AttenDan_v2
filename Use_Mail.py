import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:
    def __init__(self):
        self.from_address = ""
        self.smtp_server = "smtp.gmail.com"
        self.port = 587

    def connect_to_smtp(self):
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.port)
        except Exception as e:
            print("[Mail] failed to initialize. :", e)

    def send(self, to_address : str, subject : str, body : str):
        """
        与えられたアドレスにメールを送信する.成功すれば0を返す.

        Args:
            to_address (str): 
            subject (str): 
            body (str): 

        Returns:
            int: 0 if success, otherwise error code
        """
        msg = MIMEMultipart()
        msg["From"] = self.from_address
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        text = msg.as_string()
        try:
            self.server.sendmail(self.from_address, to_address, text)
        except Exception as e:
            print("[Mail] sent failed. :", e)
            return e
        print("[Mail] sent. :", to_address, subject, body)
        return 0

    def login_smtp(self, from_address, password):  # SMTPサーバーにログイン
        self.from_address = from_address
        print("[Mail] logging in... :", from_address)
        self.server.starttls()
        try:
            self.server.login(from_address, password)
        except Exception as e:
            print("[Mail] login failed. :", e)
            return -1
        print("[Mail] logged in. : ", from_address)

    def logout_smtp(self):  # SMTPサーバーからログアウト
        self.server.quit()
        print("[Mail] logged out.")
