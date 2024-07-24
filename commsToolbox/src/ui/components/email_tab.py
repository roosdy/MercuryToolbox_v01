import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import imaplib
import email
from email.header import decode_header
import threading
import time
import chardet
from bs4 import BeautifulSoup
import html2text
import re
import base64

class EmailTab(ttk.Frame):
    def __init__(self, parent, email_config):
        super().__init__(parent)
        self.email_config = email_config
        self.imap_connection = None
        self.is_connected = False
        self.is_refreshing = False
        self.create_widgets()
        self.connect_to_gmail()
        self.start_refresh_timer()

    def create_widgets(self):
        # Control frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(control_frame, text="Status: Disconnected")
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(control_frame, text="Refresh", command=self.refresh_emails)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)

        # Main paned window
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Email list frame
        email_list_frame = ttk.Frame(main_paned)
        main_paned.add(email_list_frame, weight=1)

        self.email_list = ttk.Treeview(email_list_frame, columns=("subject", "from", "date"), show="headings")
        self.email_list.heading("subject", text="Subject")
        self.email_list.heading("from", text="From")
        self.email_list.heading("date", text="Date")
        self.email_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        email_scrollbar = ttk.Scrollbar(email_list_frame, orient=tk.VERTICAL, command=self.email_list.yview)
        email_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.email_list.configure(yscrollcommand=email_scrollbar.set)

        # Email content frame
        email_content_frame = ttk.Frame(main_paned)
        main_paned.add(email_content_frame, weight=2)

        self.email_content = scrolledtext.ScrolledText(email_content_frame)
        self.email_content.pack(fill=tk.BOTH, expand=True)

        self.email_list.bind('<<TreeviewSelect>>', self.on_email_select)

    def on_email_select(self, event):
        selected_items = self.email_list.selection()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        email_data = self.email_list.item(selected_item, "values")
        self.email_content.delete(1.0, tk.END)
        self.email_content.insert(tk.END, f"Subject: {email_data[0]}\nFrom: {email_data[1]}\nDate: {email_data[2]}\n\nLoading content...")
        
        threading.Thread(target=self._fetch_email_content, args=(email_data,), daemon=True).start()

    def connect_to_gmail(self):
        self.update_status("Connecting...")
        try:
            self.imap_connection = imaplib.IMAP4_SSL(self.email_config['IMAP_SERVER'])
            self.imap_connection.login(self.email_config['EMAIL_ADDRESS'], self.email_config['EMAIL_PASSWORD'])
            self.is_connected = True
            self.update_status("Connected")
            self.refresh_emails()
        except Exception as e:
            self.update_status(f"Connection Error: {str(e)}", is_error=True)

    def refresh_emails(self):
        if self.is_refreshing:
            return
        self.is_refreshing = True
        self.update_status("Refreshing...")
        self.refresh_button.config(state=tk.DISABLED)
        threading.Thread(target=self._refresh_emails_thread, daemon=True).start()

    def _refresh_emails_thread(self):
        try:
            if not self.is_connected:
                self.connect_to_gmail()
            
            self.imap_connection.select("INBOX")
            _, message_numbers = self.imap_connection.search(None, "ALL")
            
            email_list = []
            for num in reversed(message_numbers[0].split()):  # Reverse to get newest first
                _, msg_data = self.imap_connection.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        email_body = response_part[1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject = self._decode_header(email_message["subject"])
                        sender = self._decode_header(email_message["from"])
                        date = email_message["date"]
                        
                        email_list.append((subject, sender, date))
                
                if len(email_list) >= 20:  # Limit to last 20 emails
                    break
            
            self.email_list.delete(*self.email_list.get_children())
            for email_data in email_list:
                self.email_list.insert("", "end", values=email_data)
            
            self.update_status("Emails refreshed")
        except Exception as e:
            self.update_status(f"Refresh Error: {str(e)}", is_error=True)
        finally:
            self.is_refreshing = False
            self.refresh_button.config(state=tk.NORMAL)

    def _decode_header(self, header):
        decoded_header = decode_header(header)
        return ' '.join([self._decode_string(part, encoding) for part, encoding in decoded_header])

    def _decode_string(self, string, encoding=None):
        if isinstance(string, bytes):
            if encoding:
                try:
                    return string.decode(encoding)
                except UnicodeDecodeError:
                    pass
            
            # Try common encodings
            for enc in ['utf-8', 'iso-8859-1', 'windows-1252']:
                try:
                    return string.decode(enc)
                except UnicodeDecodeError:
                    pass
            
            # If all else fails, use replace error handler
            return string.decode('utf-8', errors='replace')
        return str(string)

    def _fetch_email_content(self, email_data):
            try:
                self.imap_connection.select("INBOX")
                
                # Use a more robust search method
                subject = email_data[0]
                escaped_subject = re.sub(r'(["\()])', r'\\\1', subject)
                search_criteria = f'(SUBJECT "{escaped_subject}")'
                _, message_numbers = self.imap_connection.search(None, search_criteria)
                
                if message_numbers[0]:
                    for num in message_numbers[0].split():
                        _, msg_data = self.imap_connection.fetch(num, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                email_body = response_part[1]
                                email_message = email.message_from_bytes(email_body)
                                
                                if self._match_email(email_message, email_data):
                                    body = self._get_email_body(email_message)
                                    
                                    self.email_content.delete(1.0, tk.END)
                                    content = f"Subject: {email_data[0]}\nFrom: {email_data[1]}\nDate: {email_data[2]}\n\n{body}"
                                    self.email_content.insert(tk.END, content)
                                    return

                raise Exception("Email not found")
            except Exception as e:
                self.email_content.delete(1.0, tk.END)
                self.email_content.insert(tk.END, f"Error loading email content: {str(e)}")

    def _match_email(self, email_message, email_data):
            subject = self._decode_header(email_message["subject"])
            sender = self._decode_header(email_message["from"])
            date = email_message["date"]
            return (subject == email_data[0] and
                    sender == email_data[1] and
                    date == email_data[2])

    def _get_email_body(self, email_message):
            body = ""
            html_content = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = self._decode_content(part)
                    elif content_type == "text/html":
                        html_content = self._decode_content(part)
            else:
                content_type = email_message.get_content_type()
                if content_type == "text/plain":
                    body = self._decode_content(email_message)
                elif content_type == "text/html":
                    html_content = self._decode_content(email_message)

            if html_content:
                body = self._html_to_plain_text(html_content)
            
            return body

    def _decode_header(self, header):
            decoded_header = decode_header(header)
            return ' '.join([self._decode_string(part) for part, encoding in decoded_header])

    def _decode_string(self, string, encoding=None):
            if isinstance(string, bytes):
                if encoding:
                    try:
                        return string.decode(encoding)
                    except UnicodeDecodeError:
                        pass
                
                # Try common encodings
                for enc in ['utf-8', 'iso-8859-1', 'windows-1252']:
                    try:
                        return string.decode(enc)
                    except UnicodeDecodeError:
                        pass
                
                # If all else fails, use replace error handler
                return string.decode('utf-8', errors='replace')
            return str(string)

    def _decode_content(self, part):
            content = part.get_payload(decode=True)
            charset = part.get_content_charset()

            if charset is None:
                detected = chardet.detect(content)
                charset = detected['encoding']

            try:
                return content.decode(charset or 'utf-8', errors='replace')
            except (LookupError, TypeError):
                return content.decode('utf-8', errors='replace')

    def _html_to_plain_text(self, html_content):
            h = html2text.HTML2Text()
            h.ignore_links = False
            return h.handle(html_content)

    def update_status(self, message, is_error=False):
            self.status_label.config(text=f"Status: {message}", foreground="red" if is_error else "black")

    def start_refresh_timer(self):
            self.refresh_emails()
            self.after(300000, self.start_refresh_timer)  # 300000 ms = 5 minutes

def setup_email_tab(notebook, email_config):
    email_tab = EmailTab(notebook, email_config)
    notebook.add(email_tab, text="Email")
    return email_tab
