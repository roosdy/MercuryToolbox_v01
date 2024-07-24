# src/views/main_window.py

from PySide6.QtWidgets import (QMainWindow, QApplication, QStyle, QWidget, QVBoxLayout, QTabWidget,
                               QTextEdit, QSystemTrayIcon, QMenu)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QThreadPool, Slot
import os
import markdown

from src.views.email_tab import EmailTab
from src.views.chatbot_tab import ChatbotTab
from src.views.dashboard_tab import DashboardTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Communications Toolbox")
        self.threadpool = QThreadPool()
        self.email_accounts = []  # Add this line to keep track of email accounts
        self.setup_ui()
        self.setup_system_tray()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Home tab
        home_tab = QTextEdit()
        home_tab.setReadOnly(True)
        self.load_readme(home_tab)
        self.tab_widget.addTab(home_tab, "Home")
        
        # E-Mail tab
        self.email_tab = EmailTab()
        self.tab_widget.addTab(self.email_tab, "E-Mail")
        
        # Chatbot tab
        self.chatbot_tab = ChatbotTab()
        self.tab_widget.addTab(self.chatbot_tab, "Chatbot")
        
        # Dashboard tab
        self.dashboard_tab = DashboardTab(self.email_accounts)
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        
        main_layout.addWidget(self.tab_widget)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # In MainWindow's setup_ui method
        self.email_tab.emails_fetched.connect(self.update_dashboard)
        self.email_tab.email_marked.connect(self.update_dashboard)

    def load_readme(self, text_edit):
        readme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as file:
                content = file.read()
                html_content = markdown.markdown(content)
                text_edit.setHtml(html_content)
        else:
            text_edit.setPlainText("README.md not found.")

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.png")
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.tray_icon.setIcon(QIcon(pixmap))
        else:
            print(f"Failed to load icon: {icon_path}")
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        tray_menu = QMenu()
        open_action = tray_menu.addAction("Open")
        open_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Communications Toolbox",
            "Application minimized to tray",
            QSystemTrayIcon.Information,
            2000
        )

    def quit_application(self):
        self.threadpool.waitForDone()
        QApplication.quit()

    @Slot()
    def update_dashboard(self):
        emails = self.email_tab.get_all_emails()
        self.dashboard_tab.update_dashboard(emails)

    @Slot(int)
    def on_tab_changed(self, index):
        if self.tab_widget.tabText(index) == "Dashboard":
            self.update_dashboard()

    # Add these methods to handle email account management and updates
    def add_email_account(self, account):
        self.email_accounts.append(account)
        self.email_tab.add_account(account)
        self.dashboard_tab.update_account_count(len(self.email_accounts))

    def fetch_emails(self):
        emails = self.email_tab.fetch_emails()
        self.dashboard_tab.update_dashboard(emails)

    # You might want to call this method when switching to the Dashboard tab
    def update_dashboard(self):
        emails = self.email_tab.get_all_emails()
        self.dashboard_tab.update_dashboard(emails)