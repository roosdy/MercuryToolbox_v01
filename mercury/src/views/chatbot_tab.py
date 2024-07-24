from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLineEdit, 
                               QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCursor
from openai import OpenAI
import os

class ChatbotTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.chat_history = []
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def setup_ui(self):
        layout = QVBoxLayout()

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        # Add widgets to main layout
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.setLayout(layout)

    @Slot()
    def send_message(self):
        user_message = self.message_input.text().strip()
        if user_message:
            self.display_message("You", user_message)
            self.chat_history.append({"role": "user", "content": user_message})
            self.message_input.clear()
            self.get_ai_response()

    def get_ai_response(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    *self.chat_history
                ],
                temperature=1,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            ai_message = response.choices[0].message.content.strip()
            self.chat_history.append({"role": "assistant", "content": ai_message})
            self.display_message("AI", ai_message)
        except Exception as e:
            self.display_message("System", f"Error: {str(e)}")

    def display_message(self, sender, message):
        self.chat_display.moveCursor(QTextCursor.End)
        self.chat_display.insertHtml(f"<b>{sender}:</b> {message}<br><br>")
        self.chat_display.moveCursor(QTextCursor.End)