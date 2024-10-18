import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QFormLayout, QTabWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import requests
import socketio
import logging
import json
import os

# 로그 파일 경로 설정
LOG_FILE_PATH = 'chat_log.json'

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 서버 URL 상수 정의
SERVER_URL = 'http://172.20.10.7:5000'

sio = socketio.Client()

# JSON 로그 기록 함수
def log_message(data):
    # 파일이 없으면 빈 리스트를 초기화
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'w') as f:
            json.dump([], f)

    # 파일에서 기존 데이터를 읽어와서 새로운 메시지를 추가
    with open(LOG_FILE_PATH, 'r') as f:
        logs = json.load(f)
    
    # 메시지를 기록 (타임스탬프 제외)
    log_entry = {
        'username': data['username'],
        'message': data['message']
    }
    logs.append(log_entry)

    # 업데이트된 로그를 파일에 다시 저장
    with open(LOG_FILE_PATH, 'w') as f:
        json.dump(logs, f, indent=4)

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Authentication')
        self.setGeometry(100, 100, 400, 300)
        
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(self.register_tab, "Register")
        
        self.init_login_tab()
        self.init_register_tab()
        
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #fff;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background: #fff;
                border-bottom-color: #fff;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
    
    def init_login_tab(self):
        layout = QFormLayout()
        self.login_username_input = QLineEdit(self)
        self.login_password_input = QLineEdit(self)
        self.login_password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.login)
        layout.addRow('Username:', self.login_username_input)
        layout.addRow('Password:', self.login_password_input)
        layout.addWidget(self.login_button)
        self.login_tab.setLayout(layout)
    
    def init_register_tab(self):
        layout = QFormLayout()
        self.register_username_input = QLineEdit(self)
        self.register_password_input = QLineEdit(self)
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_button = QPushButton('Register', self)
        self.register_button.clicked.connect(self.register)
        layout.addRow('Username:', self.register_username_input)
        layout.addRow('Password:', self.register_password_input)
        layout.addWidget(self.register_button)
        self.register_tab.setLayout(layout)
    
    def login(self):
        username = self.login_username_input.text()
        password = self.login_password_input.text()
        try:
            response = requests.post(f'{SERVER_URL}/login', json={'username': username, 'password': password})
            if response.status_code == 200:
                self.accept()
            else:
                error_message = response.json().get('error', 'Login failed')
                self.login_username_input.setText('')
                self.login_password_input.setText('')
                self.show_error_message(error_message)
        except requests.exceptions.ConnectionError:
            self.show_error_message('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.')

    def show_error_message(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle('Error')
        error_layout = QVBoxLayout()
        error_label = QLabel(message)
        error_layout.addWidget(error_label)
        error_dialog.setLayout(error_layout)
        error_dialog.exec_()

    def register(self):
        username = self.register_username_input.text()
        password = self.register_password_input.text()
        response = requests.post(f'{SERVER_URL}/register', json={'username': username, 'password': password})
        if response.status_code == 201:
            self.tabs.setCurrentIndex(0) 
        else:
            self.register_username_input.setText('')
            self.register_password_input.setText('')

class ChatApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        sio.connect(SERVER_URL)
        sio.on('receive_message', self.receive_message)

    def initUI(self):
        self.setWindowTitle('Chat App')
        self.setGeometry(100, 100, 400, 600)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont('Arial', 12))

        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText('Enter your message...')
        self.message_input.setFont(QFont('Arial', 12))
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton('Send', self)
        self.send_button.setFont(QFont('Arial', 12))
        self.send_button.clicked.connect(self.send_message)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chat_display)
        main_layout.addLayout(input_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
            QLineEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton {
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def send_message(self):
        message = self.message_input.text()
        if message:
            print(f"Sending message: {message}")
            self.message_input.clear()
            sio.emit('send_message', {'username': self.username, 'message': message})

    def receive_message(self, data):
        self.chat_display.append(f"{data['username']}: {data['message']}")
        # 메시지를 JSON 파일에 기록
        log_message(data)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    auth_dialog = AuthDialog()
    if auth_dialog.exec_() == QDialog.Accepted:
        username = auth_dialog.login_username_input.text()
        chat_app = ChatApp(username)
        chat_app.show()
        sys.exit(app.exec_())
