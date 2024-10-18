import time
import hashlib
import json
from langchain_ollama import ChatOllama
import pyautogui as auto
import keyboard

def calculate_content_hash(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return hashlib.md5(content.encode('utf-8')).hexdigest()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("Current data:", data)
    except json.JSONDecodeError:
        print("Error decoding JSON file. Make sure the file format is correct.")
    except Exception as e:
        print(f"An error occurred: {e}")

def monitor_file(file_path, interval=1):
    last_hash = calculate_content_hash(file_path)
    if last_hash is None:
        return

    while True:
        time.sleep(interval)
        current_hash = calculate_content_hash(file_path)
        if current_hash and current_hash != last_hash:
            print(f"Content of {file_path} has been modified.")
            read_json(file_path)
            last_hash = current_hash
            
            def get_last_line_of_json(file_path):
                try:
                    with open(file_path, 'r') as file:
                        lines = file.readlines()
                        if not lines:
                            print("The file is empty.")
                            return None
                        last_line = lines[-1].strip()
                        return json.loads(last_line)
                except FileNotFoundError:
                    print("Chat data file not found.")
                    return None
                except json.JSONDecodeError:
                    print("Error decoding JSON data.")
                    return None

            def get_messages_by_user(username, file_path='chat_data.json'):
                messages = []
                last_entry = get_last_line_of_json(file_path)
                
                # 파일의 마지막 줄이 있고, 그 줄이 특정 유저의 메시지라면 추가합니다.
                if last_entry and last_entry.get('username') == username:
                    messages.append(last_entry['message'])
                
                return messages

            if __name__ == '__main__':
                # 원하는 유저의 이름을 여기에 입력하세요
                username = '민주호'
                user_messages = get_messages_by_user(username)

                if user_messages:
                    for msg in user_messages:
                        print(msg)

                        bar = auto.locateCenterOnScreen('message_bar.png', confidence=0.8)
                        auto.click(bar)

                        def stream_response(chatmodel, prompt):
                            response_stream = chatmodel.stream(prompt) 
                            for response in response_stream:
                                text_chunk = response.content
                                for char in text_chunk:
                                    keyboard.write(char)
                                    time.sleep(0.0025)  # 각 문자 사이에 지연 시간을 두어 안정적으로 입력
                            auto.press('enter')

                        if __name__ == '__main__':
                            chatmodel = ChatOllama(model="qwen2.5:3b") 
                            stream_response(chatmodel, msg)
                    # auto.KEYBOARD_KEYS()
                            
                else:
                    print(f"No messages found for user: {username}")

if __name__ == "__main__":
    path_to_watch = "chat_data.json"  # 감지할 JSON 파일의 경로를 입력하세요
    monitor_file(path_to_watch, interval=1)
