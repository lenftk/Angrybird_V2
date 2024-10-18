import requests
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 서버의 chat_data.json 파일 경로
FILE_PATH = 'chat_data.json'
# 클라이언트가 파일을 받는 URL
CLIENT_UPLOAD_URL = 'http://172.0.0.1:7985/upload'

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("chat_data.json"):
            print("파일이 변경되었습니다. 파일을 전송합니다.")
            send_file(event.src_path)

def send_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(CLIENT_UPLOAD_URL, files=files)
            if response.status_code == 200:
                print("파일이 성공적으로 전송되었습니다.")
            else:
                print(f"파일 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"파일 전송 중 오류가 발생했습니다: {e}")

def start_file_watcher():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    print("파일 감시를 시작합니다.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    start_file_watcher()
