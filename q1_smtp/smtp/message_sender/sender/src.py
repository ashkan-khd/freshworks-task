from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
import smtplib
from time import sleep
from typing import Any

from .interface import EmailMessageSender, EmailMessageSenderFactory


class MIMEMultipartMessageSenderFactory(EmailMessageSenderFactory):

    def __init__(
        self, host: str, port: int, username: str, password: str, use_tls: bool = True
    ) -> None:
        super().__init__()
        self.smtp_client = None
        self.host, self.port = host, port
        self.username, self.password = username, password
        self.use_tls = use_tls
        self.should_quit: bool
        self.sender: EmailMIMEMultipartMessageSender

    def start(self, should_quit: bool) -> "EmailMessageSenderFactory":
        self.should_quit = should_quit
        return self

    def __enter__(self) -> "EmailMessageSender":
        assert hasattr(self, "should_quit"), "Factory is not started yet!"
        smtp_client = smtplib.SMTP(self.host, self.port)
        if self.use_tls:
            smtp_client.starttls()
        smtp_client.login(self.username, self.password)
        self.sender = EmailMIMEMultipartMessageSender(smtp_client)
        return self.sender

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_quit:
            self.sender.smtp_client.quit()


class EmailMIMEMultipartMessageSender(EmailMessageSender):
    MAX_RETRY = 2
    should_quit = True

    def __init__(self, smtp_client) -> None:
        super().__init__()
        self.smtp_client = smtp_client

    def __call__(self, message: MIMEMultipart):
        assert (
            self.smtp_client
        ), "You should enter the object in order to use the send method!"

        for _ in range(self.MAX_RETRY):
            try:
                self.smtp_client.sendmail(
                    message["From"], [message["To"]], message.as_string()
                )
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 454:
                    sleep(1)
                    continue
                raise e
