from analyze_server import app
from flask import jsonify, request
import json
import torch
import re
from transformers import BertForSequenceClassification, AutoTokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import tensorflow as tf
from analyze_server.module import dbModule
from pymysql.err import IntegrityError

tokenizer = AutoTokenizer.from_pretrained('beomi/kcbert-base')
model = BertForSequenceClassification.from_pretrained('analyze_server/bert_emotion.h5')
label_val = ['우울', '중립', '불안', '공포', '분노', '자살', '행복']

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
    #여러 문장 분류
    prob_list = [0 for i in range(7)]
    label_num_list = [0 for i in range(7)]
    danger_sentences = []
    label = []

    ############# 감정 분석 #############
    text = request.form['text'].strip()
    sentences = re.split('(?<=[\.\?\!])\s*', text)
    del sentences[-1]

    # text가 빈 경우 예외 처리
    if len(sentences) == 0:

        # 11월 1일 추가
        emergency = {
                "gloom_score": 0,
                "danger_sentences": ["안정"],
                "danger_alarm": []
        }
        emergency = str(emergency).replace("'", '"')
        sentiment = {
            "radar_chart": [0,0,0,0,0,0],
            "pie_chart": [0.0, 0.0, 0.0, 0.0],
            "trend_line": ["중립"]
        }
        sentiment = str(sentiment).replace("'",'"')

        counsel_id = request.form['counsel_id']
        db_class = dbModule.Database()

        sql = "INSERT INTO sys.db_counseling_analysis(counseling_id_id, emergency, sentiment) \
            VALUES('%s','%s','%s') ON DUPLICATE KEY UPDATE emergency ='%s', sentiment = '%s' " \
            % (counsel_id, emergency, sentiment, emergency, sentiment)
        try:
            db_class.execute(sql)
            db_class.commit()
        except IntegrityError as ex:
            return jsonify(emergency,sentiment,{'ERROR': str(ex)}), 409
        finally:
            db_class.close()
        return jsonify({'ERROR': "text is empty"}), 400

    # 문장별 감정 태깅
    for sentence in sentences:
        logits = test_sentences([sentence]).tolist()
        logits = [float(x) for x in logits[0]]
        prob = tf.nn.softmax(logits)
        for i in range(7):
            prob_list[i] += float(prob[i])
        label_idx = int(np.argmax(logits))
        label.append(label_val[label_idx])
        label_num_list[label_idx] += 1
        if label_idx == 5:
            danger_sentences.append(sentence)

    # 결과 콘솔 확인용 코드
    print(list(zip(sentences,label)))

    # 감정 파이차트
    total_num = len(sentences)
    pos = (label_num_list[6]/total_num) * 100
    neu = (label_num_list[1]/total_num) * 100
    neg = 100 - pos - neu
    pie_chart = [pos, neu, neg, total_num]

    ############# 응급 상황 분석 #############

    for i in range(7):
        prob_list[i] /= len(sentences)

    # 우울 지수 - 우울, 불안, 자살 항목 확률 합
    gloom_score = 100 * (float(prob_list[0]*0.8 + prob_list[2]*0.7 + prob_list[5]*1.5))
    gloom_score = round(gloom_score, 2)

    # 위험 여부 - 우울지수와 자살 항목 문잘 표현 횟수로 결정
    danger_alarm = ""
    if gloom_score > 85 and len(danger_sentences) >= 3:
        danger_alarm = "긴급"
    elif gloom_score > 70 and len(danger_sentences) >= 2:
        danger_alarm = "위험"
    elif gloom_score > 60 and len(danger_sentences) >= 1:
        danger_alarm = "주의"
    elif gloom_score > 50:
        danger_alarm = "보통"
    else:
        danger_alarm = "안정"

    emergency = {
            "gloom_score": gloom_score,
            "danger_sentences": danger_sentences,
            "danger_alarm": danger_alarm
    }
    emergency = str(emergency).replace("'", '"')

    #'중립' 레이블 삭제하기
    del label_num_list[1]

    sentiment = {
        "radar_chart": label_num_list,
        "pie_chart": pie_chart,
        "trend_line": label
    }
    sentiment = str(sentiment).replace("'",'"')

    counsel_id = request.form['counsel_id']
    db_class = dbModule.Database()

    sql = "INSERT INTO sys.db_counseling_analysis(counseling_id_id, emergency, sentiment) \
          VALUES('%s','%s','%s') ON DUPLICATE KEY UPDATE emergency ='%s', sentiment = '%s' " \
          % (counsel_id, emergency, sentiment, emergency, sentiment)
    try:
        db_class.execute(sql)
        db_class.commit()
    except IntegrityError as ex:
        return jsonify(emergency,sentiment,{'ERROR': str(ex)}), 409
    finally:
        db_class.close()

    return jsonify(emergency,sentiment), 201


