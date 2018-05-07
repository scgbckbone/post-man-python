"""
Email Utilities

Classes:
    EmailMsg
    SMTPPostMan
"""

import re
import os
import smtplib
import logging
import config

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, IO


log_path = config.log_path

logger = logging.getLogger(config.logger_name)
logger.setLevel(logging.INFO)

f_handler = logging.FileHandler(log_path)
f_handler.setLevel(logging.INFO)

logger.addHandler(f_handler)


class EmailMsg(object):
    """
    Email message definition.
    """

    def __init__(self, send_from: str, send_to: List[str], subject: str,
                 text: str, attachments: List[str]=None):
        self.send_from = send_from
        self.send_to = send_to
        self.subject = subject
        self.text = text
        self.attachments = attachments

    def __repr__(self):
        return (
            f"subject: {self.subject};"
            f"attachments: {True if self.attachments else False};"
            f"no_attached: {len(self.attachments)}"
        )

    @staticmethod
    def attach_data(data: IO[bytes], file_name: str) -> MIMEBase:
        """
        Encode and attach bytes as message attachment.
        """
        part = MIMEBase("application", "octet-stream")
        part.set_payload(data.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(file_name)}"
        )
        return part

    def attach_file(self, file_name: str) -> MIMEBase:
        """
        Attach file from 'file_name' to message.
        """
        with open(file_name, "rb") as f:
            return self.attach_data(data=f, file_name=file_name)

    def attach_all_attachments(self, message: MIMEMultipart) -> MIMEMultipart:
        """
        Attach all files from 'self.attachments' to message.
        """
        for file_ in self.attachments:
            part = self.attach_file(file_name=file_)
            message.attach(part)

        return message

    def build_msg(self) -> str:
        """
        Builds a message from arguments provided in '__init__'.
        """
        msg = MIMEMultipart()
        msg["From"] = self.send_from
        msg["To"] = ", ".join(self.send_to)
        msg["Subject"] = self.subject
        msg.attach(MIMEText(self.text, "plain"))

        if self.attachments:
            msg = self.attach_all_attachments(message=msg)

        return msg.as_string()


class SMTPPostMan(object):
    """Defines a SMTPPostMan object."""

    def __init__(self, smtp_host: str, smtp_port: int, addr: str, pwd: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.addr = addr
        self.pwd = pwd

    @staticmethod
    def valid_email(email: str) -> bool:
        """
        Regex email address validation.
        """
        p = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
        if re.match(p, email):
            return True
        return False

    def _send(self, send_to: List[str], message: EmailMsg) -> None:
        """
        Sends a message over SMTP
        """
        server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

        try:
            server.login(self.addr, self.pwd)
            server.sendmail(self.addr, send_to, message.build_msg())

            logger.info(f"{message}")
            logger.info(f'Email sent.\t{self.addr} --> {send_to}')

        except Exception:
            logger.error("Failed to send email!", exc_info=True)

        finally:
            res = server.quit()
            logger.info(res)

    def send_email(self, send_to: List[str], subject: str=None, text: str=None,
                   attachments: List[str]=None):
        """
        Send a message with all its attachments to a recipient.
        """
        if not send_to:
            return

        for recipient in send_to:
            if not self.valid_email(email=recipient):
                logger.warning(
                    f"Recipient email address [{send_to}] seems invalid.",
                    "Sending may fail."
                )

        msg = EmailMsg(
            send_from=self.addr,
            send_to=send_to,
            subject=subject if subject else "[no-subject]",
            text=text if text else "[no-text]",
            attachments=attachments
        )
        self._send(send_to=send_to, message=msg)
        logger.info(80 * "=")

