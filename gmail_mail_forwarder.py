#!/usr/bin/env python3
"""Gmail inbox forwarder for AI_agents.

This script connects to Gmail via IMAP, finds emails from a configured sender,
and forwards matching messages to another recipient.

Required environment variables:
- GMAIL_USERNAME: your Gmail address
- GMAIL_APP_PASSWORD: Gmail app password
- FILTER_SENDER: sender to match, e.g. example1@test.com
- FORWARD_TO: recipient to forward to, e.g. sender2@test.com

Example:
  export GMAIL_USERNAME="you@gmail.com"
  export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
  export FILTER_SENDER="example1@test.com"
  export FORWARD_TO="sender2@test.com"
  python gmail_mail_forwarder.py
"""

import os
import smtplib
from email import policy
from email.parser import BytesParser
from imaplib import IMAP4_SSL
from typing import List


class GmailInboxForwarder:
    def __init__(
        self,
        username: str,
        app_password: str,
        filter_sender: str,
        forward_to: str,
        imap_host: str = "imap.gmail.com",
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        self.username = username
        self.app_password = app_password
        self.filter_sender = filter_sender
        self.forward_to = forward_to
        self.imap_host = imap_host
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def _search_matching_message_ids(self, imap):
        status, data = imap.search(None, f'(FROM "{self.filter_sender}")')
        if status != "OK":
            raise RuntimeError(f"Gmail search failed: {status}")
        ids = data[0].split()
        return ids

    def get_messages(self) -> List[bytes]:
        """Fetch raw RFC822 messages from Gmail matching the sender."""
        imap = IMAP4_SSL(self.imap_host)
        try:
            imap.login(self.username, self.app_password)
            imap.select("INBOX")
            message_ids = self._search_matching_message_ids(imap)

            if not message_ids:
                return []

            raw_messages = []
            for msg_id in message_ids:
                status, msg_data = imap.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    raise RuntimeError(f"Failed to fetch message {msg_id}: {status}")
                if not msg_data or not msg_data[0]:
                    continue
                raw = msg_data[0][1]
                raw_messages.append(raw)
            return raw_messages
        finally:
            imap.close()
            imap.logout()

    def forward_message(self, raw_message: bytes) -> None:
        """Forward one raw email to the configured recipient."""
        message = BytesParser(policy=policy.default).parsebytes(raw_message)
        original_subject = message.get("Subject", "No Subject")

        forwarded = message
        forwarded["From"] = self.username
        forwarded["To"] = self.forward_to
        forwarded["Reply-To"] = self.username
        forwarded["Subject"] = f"Fwd: {original_subject}"

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.app_password)
            smtp.send_message(
                forwarded,
                from_addr=self.username,
                to_addrs=[self.forward_to],
            )

    def run(self) -> int:
        messages = self.get_messages()
        for raw_message in messages:
            self.forward_message(raw_message)
        return len(messages)


def main():
    username = os.getenv("GMAIL_USERNAME")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    filter_sender = os.getenv("FILTER_SENDER", "example1@test.com")
    forward_to = os.getenv("FORWARD_TO", "sender2@test.com")

    if not username or not app_password:
        raise SystemExit(
            "Missing required environment variables: GMAIL_USERNAME and GMAIL_APP_PASSWORD."
        )

    agent = GmailInboxForwarder(
        username=username,
        app_password=app_password,
        filter_sender=filter_sender,
        forward_to=forward_to,
    )

    count = agent.run()
    print(f"Forwarded {count} message(s) from {filter_sender} to {forward_to}.")


if __name__ == "__main__":
    main()
