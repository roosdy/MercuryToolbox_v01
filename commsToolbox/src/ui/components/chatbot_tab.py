import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from openai import OpenAI
from dotenv import load_dotenv
import os
from tkinter import filedialog

load_dotenv()

class ChatbotTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.messages = []

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_widgets(self):
        self.chat_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=20)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        self.message_entry = ttk.Entry(input_frame, width=70)
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)

        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        clear_button = ttk.Button(button_frame, text="Clear Chat", command=self.clear_chat)
        clear_button.grid(row=0, column=0, padx=5)

        save_button = ttk.Button(button_frame, text="Save Chat", command=self.save_chat)
        save_button.grid(row=0, column=1, padx=5)

        summarize_button = ttk.Button(button_frame, text="Summarize Chat", command=self.summarize_chat)
        summarize_button.grid(row=0, column=2, padx=5)

    def send_message(self, event=None):
        user_message = self.message_entry.get()
        if user_message:
            self.display_message("You", user_message)
            self.message_entry.delete(0, tk.END)
            self.messages.append({"role": "user", "content": user_message})
            threading.Thread(target=self.get_ai_response, daemon=True).start()

    def get_ai_response(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,  # Pass in the messages list
                temperature=1,
                max_tokens=1500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Correct access to the content of the response
            ai_message = response.choices[0].message.content  # Note the dot instead of brackets
            self.messages.append({"role": "assistant", "content": ai_message})
            self.display_message("AI", ai_message)

        except Exception as e:
            self.display_message("System", f"Error: {str(e)}")

    def summarize_chat(self):
        if not self.messages:
            self.display_message("System", "No chat to summarize.")
            return

        try:
            summary_request = "Please provide a brief summary of the conversation so far in brisk bullet points, formatted in an easy to read block."
            self.messages.append({"role": "user", "content": summary_request})
            
            # Use the same model for summarizing
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages
            )
            
            # Accessing the summary content correctly
            summary = response.choices[0].message.content  
            self.display_message("AI", f"Chat Summary:\n{summary}")
            
            # Remove the summary request and response from the messages list
            self.messages = self.messages[:-2]
        except Exception as e:
            self.display_message("System", f"Error generating summary: {str(e)}")

    def display_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.messages = []

    def save_chat(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                chat_content = self.chat_display.get(1.0, tk.END)
                file.write(chat_content)
            self.display_message("System", f"Chat saved to {file_path}")

def setup_chatbot_tab(notebook):
    chatbot_tab = ChatbotTab(notebook)
    notebook.add(chatbot_tab, text="Chatbot")
    return chatbot_tab

# An example of how to create the main application window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chatbot Application")
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill="both")
    setup_chatbot_tab(notebook)

    root.mainloop()