from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .required import FileInfo, Providers
from .builder import MessageBuilderInterface


class MessageDirector:
    builder: MessageBuilderInterface

    def __init__(
        self,
        sender: str,
        reply_to: str,
        provider: Optional[Providers],
        subject,
        body,
        file_info: FileInfo,
    ):
        self.sender = sender
        self.reply_to = reply_to
        self.provider = provider
        self.subject = subject
        self.body = body
        self.file_info = file_info

    def set_builder(self, builder: MessageBuilderInterface):
        self.builder = builder

    def construct(self, receiver: str):
        self.builder.reset()
        self.builder.attach_from(self.sender)
        self.builder.attach_to(receiver)
        if self.reply_to:
            self.builder.attach_reply(self.reply_to)
        self.builder.attach_subject(self.subject)
        self.builder.attach_provider(self.provider)
        self.builder.attach_body(self.body)
        if self.file_info:
            self.builder.attach_pdf(self.file_info)
        return self.builder.build()
