from flask import Flask, jsonify, request
import torch
from transformers import BertForSequenceClassification
from server.tokenization_kobert import KoBertTokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np

app = Flask(__name__)

tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
model = BertForSequenceClassification.from_pretrained('bert-emotion.h5')
label_val = ['공포', '놀람', '슬픔', '분노', '혐오', '우울', '행복', '중립', '자살', '불안']

def convert_input_data(sentences):
    # 토크나이저로 문장을 토큰으로 분리
    tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]

    # 입력 토큰의 최대 시퀀스 길이
    MAX_LEN = 128

    # 토큰을 숫자 인덱스로 변환
    input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]

    # 문장을 MAX_LEN 길이에 맞게 자르고, 모자란 부분을 패딩 0으로 채움
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    # 어텐션 마스크 초기화
    attention_masks = []

    # 어텐션 마스크를 패딩이 아니면 1, 패딩이면 0으로 설정
    # 패딩 부분은 BERT 모델에서 어텐션을 수행하지 않아 속도 향상
    for seq in input_ids:
        seq_mask = [float(i > 0) for i in seq]
        attention_masks.append(seq_mask)

    # 데이터를 파이토치의 텐서로 변환
    inputs = torch.tensor(input_ids)
    masks = torch.tensor(attention_masks)

    return inputs, masks


def test_sentences(sentences):
    # 평가모드로 변경
    model.eval()

    # 문장을 입력 데이터로 변환
    inputs, masks = convert_input_data(sentences)


    # 그래디언트 계산 안함
    with torch.no_grad():
        # Forward 수행
        outputs = model(inputs,
                        token_type_ids=None,
                        attention_mask=masks)

    # 로스 구함
    logits = outputs[0]
    return logits

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    sentence = request.form['sentence']
    logits = test_sentences([sentence]).tolist()
    logits = [float(x) for x in logits[0]]
    return jsonify({'logits': logits, 'max_label': int(np.argmax(logits)), 'label': label_val[np.argmax(logits)]})


