from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity(sentence, words):
    vectorizer = TfidfVectorizer()
    all_texts = [sentence] + words
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    percentages = cosine_similarities * 100
    return dict(zip(words, percentages))

# 사용자 입력 받기
sentence = "나는 컴퓨팅 기술을 이용하여 전기전자 회로를 분석했다."
words = ["사과", "컴퓨터", "인공지능"]

# 유사도 계산
similarities = calculate_similarity(sentence, words)

# 결과 출력
print("\n결과:")
for word, similarity in similarities.items():
    print(f"'{word}'와(과) 문장의 유사도: {similarity:.2f}%")