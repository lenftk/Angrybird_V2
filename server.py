from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_app']

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = generate_password_hash(data['password'])
    db.users.insert_one({'username': username, 'password': password})
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.users.find_one({'username': data['username']})
    if user and check_password_hash(user['password'], data['password']): 
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} sent message: {data['message']}")
    emit('receive_message', data, broadcast=True)
    save_message_to_file(data)

def save_message_to_file(data):
    # 메시지를 JSON 파일에 저장
    try:
        with open('chat_data.json', 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open('chat_data.json', 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("chat_data.json"):
            with open(event.src_path, 'r', encoding='utf-8') as file:
                try:
                    data = file.read()
                    socketio.emit('file_update', {'data': data}, broadcast=True)
                    print("파일이 변경되어 클라이언트에 전송되었습니다.")
                except Exception as e:
                    print(f"파일을 읽는 중 오류가 발생했습니다: {e}")

def start_file_watcher():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    # 파일 감시 스레드를 별도로 시작
    threading.Thread(target=start_file_watcher, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
