from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .sender import EmailMessageSender


class EmailResult:

    def __init__(self, message: Any) -> None:
        self.message = message
        self.err: Optional[Exception] = None

    @property
    def successful(self) -> bool:
        return self.err is None


class EmailJobQueueInterface(ABC):

    @abstractmethod
    def __iter__(self) -> "EmailQueueProcessorInterface":
        pass


class EmailQueueProcessorInterface(ABC):
    @abstractmethod
    def __next__(self):
        pass


class EmailJobQueue(EmailJobQueueInterface):
    def __init__(self, sender: EmailMessageSender) -> None:
        self.q: List[EmailResult] = []
        self.processed_q: List[EmailResult] = []

        self.head_i = 0
        self.sender = sender

    def enqueue(self, item: EmailResult) -> None:
        self.q.append(item)

    def head(self) -> EmailResult:
        return self.q[self.head_i]

    def dequeue(self) -> EmailResult:
        return self.q.pop(self.head_i)

    def __iter__(self):
        return EmailQueueProcessor(self)


class EmailQueueProcessor:
    def __init__(self, queue: EmailJobQueue) -> None:
        self._queue = queue

    def process_email(self, email_result: EmailResult):
        try:
            self._queue.sender(email_result.message)
        except Exception as e:
            email_result.err = e
            self._queue.head_i += 1
        else:
            self._queue.processed_q.append(email_result)
            self._queue.dequeue()

    def __next__(self):
        try:
            email_result = self._queue.head()
            self.process_email(email_result)
            return email_result
        except IndexError:
            self._queue.head_i = 0
            raise StopIteration
