from server import app
from flask import jsonify, request
import torch
import re
from transformers import BertForSequenceClassification
from .tokenization_kobert import KoBertTokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import tensorflow as tf


tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
model = BertForSequenceClassification.from_pretrained('server/bert_emotion.h5')
label_val = ['우울', '중립', '불안', '자살', '행복', '분노', '공포']

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


# @app.route('/sentence', methods=['POST'])
# def analyze_sentiment_sentence():
#     sentence = request.form['sentence']
#     logits = test_sentences([sentence]).tolist()
#     logits = [float(x) for x in logits[0]]
#     return jsonify({'logits': logits, 'max_label': int(np.argmax(logits)), 'label': label_val[np.argmax(logits)]})

@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    #여러 문장
    prob_list = [0 for i in range(7)]
    label_list = []
    label_num_list = [0 for i in range(7)]
    gloom_idx = 0
    danger_sentences = []
    danger_sentences_num = 0


    sentences = request.form['sentences'].split('.')
    del sentences[-1]

    for sentence in sentences:
        logits = test_sentences([sentence]).tolist()
        logits = [float(x) for x in logits[0]]
        prob = tf.nn.softmax(logits)
        for i in range(7):
            prob_list[i] += float(prob[i])
        label_idx = int(np.argmax(logits))
        label_num_list[label_idx] += 1
        if label_idx == 3:
            danger_sentences.append(sentence)
            danger_sentences_num += 1
        label_list.append(label_val[label_idx])


    for i in range(7):
        prob_list[i] /= len(sentences)

    gloom_idx = 100 * (float(prob[0] + prob[2] + prob[3]))
    if gloom_idx > 60 and danger_sentences_num >= 1:
        danger_alarm = True
    else:
        danger_alarm = False



    return jsonify({'label_list': label_list,
                    'label_num_list': label_num_list,
                    'danger_alarm': danger_alarm,
                    'gloom_idx': gloom_idx,
                    'danger_sentences': danger_sentences,
                    'danger_sentences_num': danger_sentences_num
                    })


