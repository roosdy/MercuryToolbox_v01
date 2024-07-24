# src/models/email_account.py
import imaplib
import email
from email.header import decode_header

class EmailAccount:
    def __init__(self, email, password, imap_server, smtp_server, imap_port=993, smtp_port=587):
        self.email = email
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.imap_port = imap_port
        self.smtp_port = smtp_port

    def fetch_emails(self, limit=10):
        emails = []
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select('inbox')
            
            _, search_data = mail.search(None, 'ALL')
            for num in search_data[0].split()[-limit:]:
                _, msg_data = mail.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        email_body = response_part[1]
                        email_msg = email.message_from_bytes(email_body)
                        subject, encoding = decode_header(email_msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")
                        sender = email_msg["From"]
                        emails.append({"subject": subject, "sender": sender, "raw": email_msg})
            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error fetching emails: {e}")
        return emails

    def to_dict(self):
        return {
            'email': self.email,
            'password': self.password,
            'imap_server': self.imap_server,
            'smtp_server': self.smtp_server,
            'imap_port': self.imap_port,
            'smtp_port': self.smtp_port
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def __str__(self):
        return self.email