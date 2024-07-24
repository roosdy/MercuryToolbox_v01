# main.py
import tkinter as tk
from tkinter import ttk
import pystray
from PIL import Image, ImageTk
import threading
from ui.components.email_tab import setup_email_tab
from ui.components.chatbot_tab import setup_chatbot_tab
from config.email_config import EMAIL_CONFIG
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class ModularCommunicationSuite:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modular Communication Suite")
        self.root.geometry("800x600+300+300")  # width x height + x + y
        self.root.withdraw()  # Hide the window initially

        self.create_notebook()
        self.setup_tray()

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Setup email tab with config
        self.email_tab = setup_email_tab(self.notebook, EMAIL_CONFIG)

        # Setup chatbot tab
        self.chatbot_tab = setup_chatbot_tab(self.notebook)

        # Welcome tab
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        ttk.Label(welcome_frame, text="Welcome to the Modular Communication Suite!", font=("Arial", 16)).pack(pady=20)
        ttk.Label(welcome_frame, text="Use the tabs above to access different features.").pack()

        # Dashboard tab (placeholder for now)
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        ttk.Label(dashboard_frame, text="Dashboard content coming soon...").pack(pady=20)

    def setup_tray(self):
        # For now, let's use a dummy icon to avoid the FileNotFoundError
        image = Image.new('RGB', (64, 64), color = 'red')
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Exit", self.quit_window)
        )
        self.icon = pystray.Icon("name", image, "Modular Communication Suite", menu)
        self.icon.run_detached()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)

    def hide_window(self):
        self.root.withdraw()

    def quit_window(self):
        self.icon.stop()
        self.root.quit()

    def run(self):
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)  # Hide instead of close
        self.root.mainloop()

if __name__ == "__main__":
    # You can access the OpenAI API key like this:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Warning: OPENAI_API_KEY not found in .env file")
    
    app = ModularCommunicationSuite()
    app.run()