from flask import Flask, request
import os

app = Flask(__name__)

# 파일 저장 경로
UPLOAD_FOLDER = './received_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # 파일 저장
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    print(f"파일이 성공적으로 저장되었습니다: {file_path}")
    return 'File uploaded successfully', 200

if __name__ == '__main__':
    # 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)
