from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget, 
                               QTextEdit, QSplitter, QHBoxLayout, QAbstractItemView, 
                               QFileDialog, QMessageBox, QMenu)
from PySide6.QtCore import Slot, Qt, QThreadPool, Signal, QRunnable, QObject
from PySide6.QtGui import QAction, QColor
from src.views.account_setup_window import AccountSetupWindow
from src.utils.ai_summarizer import summarize_email
from src.models.email_account import EmailAccount
import json
import os
import traceback
import sys

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class EmailTab(QWidget):
    emails_fetched = Signal()
    email_marked = Signal()

    def __init__(self):
        super().__init__()
        self.email_accounts = []
        self.emails_cache = []
        self.threadpool = QThreadPool()
        self.setup_ui()
        self.load_accounts()


    def setup_ui(self):
        main_layout = QHBoxLayout()

        # Left side: account list and buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.account_list = QListWidget()
        left_layout.addWidget(self.account_list)

        add_account_button = QPushButton("Add Email Account")
        add_account_button.clicked.connect(self.open_account_setup)
        left_layout.addWidget(add_account_button)

        remove_account_button = QPushButton("Remove Email Account")
        remove_account_button.clicked.connect(self.remove_account)
        left_layout.addWidget(remove_account_button)

        fetch_emails_button = QPushButton("Fetch Emails")
        fetch_emails_button.clicked.connect(self.fetch_emails)
        left_layout.addWidget(fetch_emails_button)

        left_widget.setLayout(left_layout)

        # Right side: email list, summary, and full content
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        email_splitter = QSplitter(Qt.Vertical)
        content_splitter = QSplitter(Qt.Horizontal)

        self.email_list = QListWidget()
        self.email_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        email_splitter.addWidget(self.email_list)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        content_splitter.addWidget(self.summary_text)

        self.full_email_content = QTextEdit()
        self.full_email_content.setReadOnly(True)
        content_splitter.addWidget(self.full_email_content)

        email_splitter.addWidget(content_splitter)
        right_layout.addWidget(email_splitter)

        self.email_list.itemClicked.connect(self.display_email)
        self.email_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.email_list.customContextMenuRequested.connect(self.show_email_context_menu)

        summarize_button = QPushButton("Summarize Selected Emails")
        summarize_button.clicked.connect(self.summarize_selected_emails)
        right_layout.addWidget(summarize_button)

        save_summary_button = QPushButton("Save Summary")
        save_summary_button.clicked.connect(self.save_summary)
        right_layout.addWidget(save_summary_button)

        right_widget.setLayout(right_layout)

        # Add left and right widgets to main layout
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 2)

        self.setLayout(main_layout)

    def open_account_setup(self):
        self.account_setup_window = AccountSetupWindow()
        self.account_setup_window.account_created.connect(self.add_account)
        self.account_setup_window.show()

    @Slot(object)
    def add_account(self, account):
        self.email_accounts.append(account)
        self.account_list.addItem(account.email)
        self.save_accounts()

    def remove_account(self):
        current_row = self.account_list.currentRow()
        if current_row >= 0:
            self.account_list.takeItem(current_row)
            del self.email_accounts[current_row]
            self.save_accounts()

    def save_accounts(self):
        accounts_data = [account.to_dict() for account in self.email_accounts]
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'email_accounts.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(accounts_data, f)

    def load_accounts(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'email_accounts.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                accounts_data = json.load(f)
            for account_data in accounts_data:
                account = EmailAccount.from_dict(account_data)
                self.email_accounts.append(account)
                self.account_list.addItem(account.email)

    def fetch_emails(self):
        if not self.email_accounts:
            return

        selected_account = self.email_accounts[self.account_list.currentRow()]
        
        # Use a worker thread for email fetching
        worker = Worker(selected_account.fetch_emails)
        worker.signals.result.connect(self.update_email_list)
        worker.signals.finished.connect(self.fetch_finished)
        self.threadpool.start(worker)
        self.emails_fetched.emit()

    @Slot(list)
    def update_email_list(self, emails):
        self.emails_cache = emails
        self.email_list.clear()
        for email in emails:
            self.email_list.addItem(f"{email['subject']} - From: {email['sender']}")
        self.emails_fetched.emit()  # Emit signal after updating the list

    @Slot()
    def fetch_finished(self):
        print("Email fetching completed")

    def display_email(self, item):
        index = self.email_list.row(item)
        if 0 <= index < len(self.emails_cache):
            email = self.emails_cache[index]
            content = self.get_email_content(email['raw'])
            self.full_email_content.setPlainText(content)

    def summarize_selected_emails(self):
        selected_items = self.email_list.selectedItems()
        if not selected_items:
            return

        selected_account = self.email_accounts[self.account_list.currentRow()]
        emails = selected_account.fetch_emails()
        
        summaries = []
        for item in selected_items:
            index = self.email_list.row(item)
            email_content = self.get_email_content(emails[index]['raw'])
            summary = summarize_email(email_content)
            summaries.append(f"Email: {item.text()}\n{summary}\n\n")

        self.summary_text.setText("\n".join(summaries))

    def get_email_content(self, email_message):
        content = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        content += payload.decode(charset, errors='replace')
                    except Exception as e:
                        content += f"[Error decoding part: {str(e)}]"
        else:
            try:
                payload = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset() or 'utf-8'
                content = payload.decode(charset, errors='replace')
            except Exception as e:
                content = f"[Error decoding email: {str(e)}]"
        return content

    def show_email_context_menu(self, position):
        menu = QMenu()
        urgent_action = QAction("Mark as Urgent", self)
        important_action = QAction("Mark as Important", self)
        on_track_action = QAction("Mark as On Track", self)
        unmarked_action = QAction("Remove Mark", self)

        urgent_action.triggered.connect(lambda: self.mark_email("urgent"))
        important_action.triggered.connect(lambda: self.mark_email("important"))
        on_track_action.triggered.connect(lambda: self.mark_email("on_track"))
        unmarked_action.triggered.connect(lambda: self.mark_email("unmarked"))

        menu.addAction(urgent_action)
        menu.addAction(important_action)
        menu.addAction(on_track_action)
        menu.addAction(unmarked_action)

        menu.exec_(self.email_list.mapToGlobal(position))

    def mark_email(self, category):
        item = self.email_list.currentItem()
        if item:
            if category == "urgent":
                item.setBackground(QColor(255, 0, 0, 100))  # Red
            elif category == "important":
                item.setBackground(QColor(255, 165, 0, 100))  # Orange
            elif category == "on_track":
                item.setBackground(QColor(0, 255, 0, 100))  # Green
            else:
                item.setBackground(QColor(255, 255, 255, 0))  # Transparent
            # Update the email in the cache with the new category
            index = self.email_list.row(item)
            if 0 <= index < len(self.emails_cache):
                self.emails_cache[index]['flag'] = category

        self.email_marked.emit()

    def get_all_emails(self):
        return self.emails_cache
    
    def save_summary(self):
        summary = self.summary_text.toPlainText()
        if not summary:
            QMessageBox.warning(self, "No Summary", "There is no summary to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Summary", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(summary)
                QMessageBox.information(self, "Summary Saved", f"Summary has been saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while saving the summary: {str(e)}")