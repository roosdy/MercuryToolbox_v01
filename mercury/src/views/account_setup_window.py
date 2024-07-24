from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
                               QMessageBox, QFileDialog, QHBoxLayout)
from PySide6.QtCore import Signal
from src.models.email_account import EmailAccount
import json

class AccountSetupWindow(QWidget):
    account_created = Signal(EmailAccount)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Account Setup")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.imap_server_input = QLineEdit()
        self.smtp_server_input = QLineEdit()
        self.imap_port_input = QLineEdit("993")
        self.smtp_port_input = QLineEdit("587")

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("IMAP Server:", self.imap_server_input)
        form_layout.addRow("SMTP Server:", self.smtp_server_input)
        form_layout.addRow("IMAP Port:", self.imap_port_input)
        form_layout.addRow("SMTP Port:", self.smtp_port_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Config")
        save_button.clicked.connect(self.save_config)
        button_layout.addWidget(save_button)

        load_button = QPushButton("Load Config")
        load_button.clicked.connect(self.load_config)
        button_layout.addWidget(load_button)

        create_account_button = QPushButton("Create Account")
        create_account_button.clicked.connect(self.create_account)
        button_layout.addWidget(create_account_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_config(self):
        config = {
            "email": self.email_input.text(),
            "password": self.password_input.text(),
            "imap_server": self.imap_server_input.text(),
            "smtp_server": self.smtp_server_input.text(),
            "imap_port": self.imap_port_input.text(),
            "smtp_port": self.smtp_port_input.text()
        }
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config, f)
            QMessageBox.information(self, "Config Saved", f"Config has been saved to {file_path}")

    def load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r') as f:
                config = json.load(f)
            self.email_input.setText(config.get("email", ""))
            self.password_input.setText(config.get("password", ""))
            self.imap_server_input.setText(config.get("imap_server", ""))
            self.smtp_server_input.setText(config.get("smtp_server", ""))
            self.imap_port_input.setText(str(config.get("imap_port", "")))
            self.smtp_port_input.setText(str(config.get("smtp_port", "")))
            # QMessageBox.information(self, "Config Loaded", "Configuration has been loaded successfully.")

    def create_account(self):
        email = self.email_input.text()
        password = self.password_input.text()
        imap_server = self.imap_server_input.text()
        smtp_server = self.smtp_server_input.text()
        imap_port = int(self.imap_port_input.text())
        smtp_port = int(self.smtp_port_input.text())

        if not all([email, password, imap_server, smtp_server]):
            QMessageBox.warning(self, "Incomplete Information", "Please fill in all fields.")
            return

        account = EmailAccount(email, password, imap_server, smtp_server, imap_port, smtp_port)
        self.account_created.emit(account)
        QMessageBox.information(self, "Account Created", f"Account for {email} has been created successfully.")
        self.close()

    def clear_fields(self):
        self.email_input.clear()
        self.password_input.clear()
        self.imap_server_input.clear()
        self.smtp_server_input.clear()
        self.imap_port_input.setText("993")
        self.smtp_port_input.setText("587")