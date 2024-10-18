import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# BERT 모델과 토크나이저 로드
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
model = BertModel.from_pretrained('bert-base-multilingual-cased')

def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

def calculate_similarity(sentence, words):
    sentence_embedding = get_bert_embedding(sentence)
    word_embeddings = [get_bert_embedding(word) for word in words]
    
    similarities = [cosine_similarity(sentence_embedding, word_embedding)[0][0] for word_embedding in word_embeddings]
    percentages = [similarity * 100 for similarity in similarities]
    
    return dict(zip(words, percentages))

# 사용자 입력 받기
sentence = "과일은 맛있다."
words = ["사과", "컴퓨터", "인공지능"]

# 유사도 계산
similarities = calculate_similarity(sentence, words)

# 결과 출력
print("\n결과:")
for word, similarity in similarities.items():
    print(f"'{word}'와(과) 문장의 유사도: {similarity:.2f}%")