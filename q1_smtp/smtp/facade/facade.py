import logging
from django.conf import settings

from q1_smtp.smtp.message_builder import MessageDirector, FileInfo
from q1_smtp.smtp.message_sender import (
    EmailMessageSender,
    EmailJobQueueInterface,
    EmailResult,
)
from q1_smtp.smtp.message_sender.sender import EmailMessageSenderFactory

from .config_context import ConfigContextInterface


logger = logging.getLogger()


class SMTPFacade:

    def __create_config_context(self, config) -> ConfigContextInterface:
        from .config_context import ConfigContext

        return ConfigContext(config)

    def __create_message_director(self, subject, html_msg, filename, filepath):
        from q1_smtp.smtp.message_builder.builder import MIMEMultipartMessageBuilder

        director = MessageDirector(
            sender=self.from_email,
            reply_to=self.reply_email,
            subject=subject,
            body=html_msg,
            file_info=FileInfo(filename, filepath),
            **self.config_context.get_message_fields(),
        )

        builder = MIMEMultipartMessageBuilder()
        director.set_builder(builder)
        return director

    def __create_job_queue(
        self, sender: EmailMessageSender, message_director: MessageDirector, receiver
    ) -> EmailJobQueueInterface:
        from q1_smtp.smtp.message_sender.email_queue import EmailJobQueue

        queue = EmailJobQueue(sender)
        for rec in receiver:
            queue.enqueue(EmailResult(message_director.construct(rec)))
        return queue

    def __create_sender_factory(self) -> "EmailMessageSenderFactory":
        from q1_smtp.smtp.message_sender.sender.src import (
            MIMEMultipartMessageSenderFactory,
        )

        return MIMEMultipartMessageSenderFactory(
            **self.config_context.get_sender_fields()
        )

    def __init__(
        self,
        from_email=settings.DEFAULT_FROM_EMAIL,
        reply_email=None,
        config=settings.DEFAULT_EMAIL_CONFIG,
    ) -> None:
        self.from_email = from_email
        self.reply_email = reply_email
        self.config_context = self.__create_config_context(config)

    def send_email(
        self,
        subject,
        receiver,
        html_msg,
        filepath=None,
        filename=None,
        q=True,
        log_each_email: bool = False,
    ):
        message_director = self.__create_message_director(
            subject, html_msg, filename, filepath
        )

        sender_factory = self.__create_sender_factory()

        with sender_factory.start(q) as email_sender:
            job_queue = self.__create_job_queue(
                email_sender, message_director, receiver
            )
            for email in job_queue:
                if log_each_email:
                    logs = [
                        f"Email to {email.message['To']} Success: {email.successful}",
                    ]
                    if not email.successful:
                        logs.append(f"Err: {str(email.err)}")
                    logger.debug("\n".join(logs))


SmtpService = SMTPFacade
