from abc import ABC, abstractmethod
import email
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from django.conf import settings
from django.utils.encoding import force_text

from .required import FileInfo, FileInfo, Providers


class MessageBuilderInterface(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def build(self) -> Any:
        pass

    @abstractmethod
    def attach_provider(self, provider):
        pass

    @abstractmethod
    def attach_subject(self, subject):
        pass

    @abstractmethod
    def attach_from(self, from_: str):
        pass

    @abstractmethod
    def attach_to(self, to: str):
        pass

    @abstractmethod
    def attach_reply(self, reply_to: str):
        pass

    @abstractmethod
    def attach_body(self, body):
        pass

    @abstractmethod
    def attach_pdf(self, file_info: FileInfo):
        pass


class MIMEMultipartMessageBuilder(MessageBuilderInterface):

    def __init__(self) -> None:
        super().__init__()
        self.potential_message = None
        self.reset()

    def reset(self):
        self.potential_message = MIMEMultipart()

    def build(self):
        return self.potential_message

    def attach_provider(self, provider):
        if not (provider == Providers.AWS and settings.SES_CONFIGURATION_SET):
            return

        self.potential_message["X-SES-CONFIGURATION-SET"] = (
            settings.SES_CONFIGURATION_SET
        )

    def attach_subject(self, subject):
        self.potential_message["Subject"] = email.header.Header(
            force_text(subject), "utf-8"
        )

    def attach_from(self, from_: str):
        self.potential_message["From"] = from_

    def attach_to(self, to: str):
        self.potential_message["To"] = to
    
    def attach_reply(self, reply_to: str):
        self.potential_message['Reply-To'] = reply_to
    
    def attach_body(self, body):
        self.potential_message.attach(MIMEText(body.encode("utf-8"), "html", "utf-8"))

    def attach_pdf(self, file_info: FileInfo):
        with open(file_info.path, "rb") as fp:
            att = MIMEApplication(fp.read(), _subtype="csv")
            att.add_header(
                "Content-Disposition", "attachment", filename=file_info.filename
            )
            self.potential_message.attach(att)
