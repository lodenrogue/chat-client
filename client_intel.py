import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from socketio.client import Client as SocketIOClient

app = QApplication(sys.argv)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Chat Client')
        self.setGeometry(200, 200, 400, 400)

        # Create the main layout
        layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        # Create the chat display area
        self.chat_display = QTextBrowser()
        layout.addWidget(self.chat_display)

        # Create the input field for usernames
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        layout.addWidget(self.username_input)

        # Create the input field for messages
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        # Create the send button
        send_button = QPushButton('Send')
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        self.show()

        # Connect to the chat server
        server = self.get_server()
        print(f'Connecting to {server}')
        
        self.socketio = SocketIOClient()
        self.socketio.on('message', self.handle_message)
        self.socketio.on('connect', self.handle_connect)
        self.socketio.on('disconnect', self.handle_disconnect)
        self.socketio.connect(server)

    def send_message(self):
        self.username = self.username_input.text()
        message = self.message_input.text()
        self.message_input.clear()
        self.socketio.emit('message', {'username': self.username, 'message': message})

    def handle_message(self, data):
        username = data['username']
        message = data['message']
        display_message = f"<b>{username}</b>: {message}<br>"
        self.chat_display.append(display_message)

        if self.username != username:
            self.play_notification_sound()

    def handle_connect(self):
        self.chat_display.append("<b>Connected to the chat server.</b><br>")

    def handle_disconnect(self):
        self.chat_display.append("<b>Disconnected from the chat server.</b><br>")

    def closeEvent(self, event):
        # Disconnect from the chat server before exiting
        self.socketio.disconnect()
        event.accept()

    def get_server(self):
        with open("server", "r") as f:
            host = f.read().strip()
            return f'http://{host}:4389'

    def play_notification_sound(self):
        subprocess.Popen('say -v Bells "beep"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == '__main__':
    chat_window = ChatWindow()
    sys.exit(app.exec_())
