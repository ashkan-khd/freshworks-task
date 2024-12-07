from abc import ABC, abstractmethod
from typing import Any


class EmailMessageSender(ABC):

    @abstractmethod
    def __call__(self, message: Any):
        pass


class EmailMessageSenderFactory(ABC):

    @abstractmethod
    def start(self, *args, **kwargs) -> "EmailMessageSenderFactory":
        pass

    @abstractmethod
    def __enter__(self) -> EmailMessageSender:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


