from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModel
from flask_cors import CORS
import torch
import json
import hashlib
import time
import threading
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Flask 애플리케이션 생성
app = Flask(__name__)
CORS(app)

# 그래프에 사용할 데이터 저장을 위한 전역 변수
graph_data = {"user_input": "", "similarities": [0, 0, 0, 0]}
last_processed_message = None  # 마지막으로 처리된 메시지를 저장

# Hugging Face 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("skt/kobert-base-v1")
model = AutoModel.from_pretrained("skt/kobert-base-v1")

# 특정 파일의 내용 해시 계산
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

# JSON 파일에서 특정 사용자의 메시지를 가져오는 함수
def get_messages_by_user(username, file_path='chat_data.json'):
    messages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                entry = json.loads(line)
                if entry.get('username') == username:
                    messages.append(entry['message'])
    except FileNotFoundError:
        print("Chat data file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON data.")
    return messages

# 파일 변경을 감지하는 함수
def monitor_file(file_path, username, interval=1):
    last_hash = calculate_content_hash(file_path)
    if last_hash is None:
        return

    while True:
        time.sleep(interval)
        current_hash = calculate_content_hash(file_path)
        if current_hash and current_hash != last_hash:
            print(f"Content of {file_path} has been modified.")
            user_messages = get_messages_by_user(username, file_path)
            if user_messages:
                # 가장 최신 메시지를 처리
                latest_message = user_messages[-1]
                process_message(latest_message)
            last_hash = current_hash

# 메시지를 처리하고 유사도를 계산하는 함수
def process_message(test_sentence):
    global graph_data, last_processed_message

    # 이전에 처리된 메시지와 동일한지 확인
    if test_sentence == last_processed_message:
        print("Duplicate message detected. Skipping processing.")
        return

    last_processed_message = test_sentence  # 최신 메시지로 업데이트

    test_words = ["전화번호", "놀러가자", "사귈래", "사진"]

    # 입력된 문장의 임베딩 생성
    sentence_inputs = tokenizer(
        test_sentence,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    # GPU 사용 가능한지 확인하고, 가능하면 GPU로 이동
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sentence_inputs = {key: value.to(device) for key, value in sentence_inputs.items()}
    model.to(device)

    # 'token_type_ids'를 사용하지 않고 'input_ids'와 'attention_mask'만으로 모델 호출
    with torch.no_grad():
        sentence_embedding = model(
            input_ids=sentence_inputs['input_ids'],
            attention_mask=sentence_inputs['attention_mask']
        ).last_hidden_state.mean(dim=1)

    similarities = []
    for word in test_words:
        word_inputs = tokenizer(
            word,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        word_inputs = {key: value.to(device) for key, value in word_inputs.items()}

        with torch.no_grad():
            word_embedding = model(
                input_ids=word_inputs['input_ids'],
                attention_mask=word_inputs['attention_mask']
            ).last_hidden_state.mean(dim=1)

        # 텐서의 차원을 맞춰 유사도를 계산
        cosine_similarity = torch.nn.functional.cosine_similarity(
            sentence_embedding, word_embedding, dim=1
        ).item()
        similarity_percentage = (cosine_similarity + 1) * 50
        similarities.append(similarity_percentage)

    graph_data = {"user_input": test_sentence, "similarities": similarities}

# '/get_graph_data' 엔드포인트: 현재 그래프 데이터를 반환
@app.route('/get_graph_data', methods=['GET'])
def get_graph_data():
    global graph_data
    return jsonify(graph_data)

# '/' 엔드포인트: 그래프를 표시하는 HTML 페이지를 렌더링
@app.route('/', methods=['GET'])
def index():
    return render_template('graph.html', user_input=graph_data['user_input'], similarities=graph_data['similarities'])

# 파일 모니터링을 백그라운드에서 실행
def start_file_monitoring(username, file_path='chat_data.json'):
    monitoring_thread = threading.Thread(target=monitor_file, args=(file_path, username))
    monitoring_thread.daemon = True
    monitoring_thread.start()

if __name__ == '__main__':
    # 특정 유저의 이름 설정
    username = '민주호'
    start_file_monitoring(username)

    # Flask 애플리케이션 실행
    app.run(host='0.0.0.0', port=1557)
