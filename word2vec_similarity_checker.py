from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 한국어 Word2Vec 모델 로드 (처음 실행 시 다운로드 됨)
model = KeyedVectors.load_word2vec_format('https://github.com/Kyubyong/wordvectors/raw/master/ko/ko.vec.gz', binary=False)

def calculate_similarity(sentence, words):
    def get_sentence_vector(sent):
        words = sent.split()
        vectors = [model[word] for word in words if word in model]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(model.vector_size)

    sentence_vector = get_sentence_vector(sentence)
    word_vectors = [get_sentence_vector(word) for word in words]
    
    similarities = [cosine_similarity([sentence_vector], [word_vector])[0][0] for word_vector in word_vectors]
    percentages = [similarity * 100 for similarity in similarities]
    
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