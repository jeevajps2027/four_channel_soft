import os
import sys
import threading
import time
import requests
from django.core.management import execute_from_command_line
from PySide6.QtCore import QUrl
from PySide6 import QtWidgets, QtWebEngineWidgets

# Global event to signal the server to stop
stop_event = threading.Event()

class WebWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("FOUR CHANNEL SOFTWARE")
        self.resize(1024, 768)  # Set the window size to something larger to be visible

        # Create a QWebEngineView widget to display the web page
        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        # Create a layout and add the browser
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.browser)

        # Load the Django server URL
        self.browser.setUrl(QUrl("http://127.0.0.1:8000/"))

        # Set the layout to the widget
        self.setLayout(layout)

        # Optional: set the size of the window and ensure it's visible
        self.setGeometry(100, 100, 1024, 768)

    def closeEvent(self, event):
        # Send a POST request to the shutdown endpoint
        try:
            requests.post("http://127.0.0.1:8000/shutdown/")
        except Exception as e:
            print(f"Error sending shutdown request: {e}")
        finally:
            stop_event.set()
            event.accept()


def start_web_window():
    app = QtWidgets.QApplication(sys.argv)
    window = WebWindow()
    window.show()  # Ensure window is shown
    sys.exit(app.exec())


def migrate_database():
    os.environ["DJANGO_SETTINGS_MODULE"] = "mini_soft.settings"
    
    # Run makemigrations
    sys.argv = ["manage.py", "makemigrations"]
    execute_from_command_line(sys.argv)
    
    # Run migrate
    sys.argv = ["manage.py", "migrate"]
    execute_from_command_line(sys.argv)


def start_django_server():
    # First, perform migrations
    migrate_database()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_soft.settings")
    sys.argv = ["manage.py", "runserver", "--noreload"]
    while not stop_event.is_set():
        try:
            execute_from_command_line(sys.argv)
        except SystemExit:
            break  # Exit gracefully if the server stops


def wait_for_server():
    url = "http://127.0.0.1:8000/"
    print("Waiting for Django server to start...")
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Django server is running.")
                break
        except requests.ConnectionError:
            pass

        time.sleep(1)  # Retry every second


if __name__ == "__main__":
    # Start the Django server in a separate thread
    django_thread = threading.Thread(target=start_django_server)
    django_thread.daemon = True
    django_thread.start()

    # Wait for the Django server to start
    wait_for_server()

    # Start the PySide6 window after the server starts
    start_web_window()
