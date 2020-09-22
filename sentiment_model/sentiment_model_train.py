# -*- coding: utf-8 -*-
"""bert_emotion_koBERT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K8D9MOy4yHo-NeoRUE0boVPVjuqTGQb4
"""

# 2020.8.10 수정 전 colab 원본 ver.

import tensorflow as tf
import torch

from transformers import BertForSequenceClassification, AdamW
from transformers import get_linear_schedule_with_warmup
from server.api.tokenization_kobert import KoBertTokenizer
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from google.colab import drive


import pandas as pd
import numpy as np
import random
import time
import datetime

# 구글 드라이브에서 데이터 로드
drive.mount('/content/drive', force_remount=True)

# 데이터셋 3개 불러오기
data1 = pd.read_excel("/content/drive/My Drive/Colab Notebooks/대화_단발성.xlsx")
data2 = pd.read_excel("/content/drive/My Drive/Colab Notebooks/정신건강_분류.xlsx");
data3 =pd.read_excel("/content/drive/My Drive/Colab Notebooks/웰니스대화_분류.xlsx");
#data2.dropna(axis = 0, inplace = True)

data = pd.concat([data1, data2, data3])
data

# label 확인
group = ["놀람", "분노", "슬픔", "중립", "혐오", "행복","우울","불안","자살","공포"]
seriesObj = data.apply(lambda x: False if x['Emotion'] in group else True , axis=1)
numOfRows = (seriesObj[seriesObj == True].index)


print(data.iloc[numOfRows])
seriesObj.describe()

import re
tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
# 텍스트 전처리
# 문장 앞 뒤 공백은 토크나이저가 처리
def punctuation(text):
  re_pattern = r'[\s]*\.{2,}'
  new_text = re.sub(re_pattern, '...', text)
  re_pattern = r'[\s]*~+'
  new_text = re.sub(re_pattern, '~', new_text)
  re_pattern = r'[\s]*\.'
  new_text = re.sub(re_pattern, '.', new_text)
  re_pattern = r'[\s]*\?+'
  new_text = re.sub(re_pattern, '?', new_text)
  re_pattern = r'[\s]*;+'
  new_text = re.sub(re_pattern, ';', new_text)
  re_pattern = r'[\s]*\!+'
  new_text = re.sub(re_pattern, '!', new_text)
  return new_text

def crying(text):
  re_pattern = r'[\s]*([ㅠ|ㅜ]+)'
  new_text = re.sub(re_pattern, 'ㅠㅠ', text)
  new_text = re.sub(re_pattern, 'ㅠㅠ', new_text)
  return new_text

def scared(text):
  re_pattern = r'[\s]*([ㄷ]+)'
  new_text = re.sub(re_pattern, 'ㄷㄷ', text)
  new_text = re.sub(re_pattern, 'ㄷㄷ', new_text)
  return new_text

def laughing(text):
  re_pattern = r'[\s]*([ㅋ|ㅎ]+)'
  new_text = re.sub(re_pattern, 'ㅋㅋ', text)
  new_text = re.sub(re_pattern, 'ㅋㅋ', new_text)
  return new_text

def preprocess_text(text):
  new_text = punctuation(text)
  new_text = crying(new_text)
  new_text = scared(new_text)
  new_text = laughing(new_text)
  return new_text

data['Sentence'] = data['Sentence'].apply(preprocess_text)
data

train, test = train_test_split(data,random_state=2000, test_size = 0.01)

#전처리 (BERT 입력형식에 맞도록)
sentences = train['Sentence']
sentences = ["[CLS] " + str(sentence) + " [SEP]" for sentence in sentences]
sentences[:10]

# 라벨 추출
labels = train['Emotion'].values
labels, label_val = pd.factorize(labels)
print(label_val)

#KoBert 토크나이저로 문장 -> 토큰
tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
tokenized_texts = [tokenizer.tokenize(word) for word in sentences]

print(sentences[0])
print(tokenized_texts[0])

sen = '[CLS] 나는 우리가 이제 그만 했으면 좋겠어. [SEP]'
tokenized_text = [tokenizer.tokenize(sen)]

print(sen)
print(tokenized_text)

MAX_LEN = 128
input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]

input_ids = pad_sequences(input_ids, maxlen = MAX_LEN, dtype = "long", truncating = "post", padding="post")
input_ids[0]

attention_masks = []

for seq in input_ids:
  seq_mask = [float(i>0) for i in seq]
  attention_masks.append(seq_mask)

print(attention_masks[0])

train_inputs, validation_inputs, train_labels, validation_labels = train_test_split(input_ids,labels,random_state=2000, test_size = 0.1)

train_masks, validation_masks, _, _ = train_test_split(attention_masks, input_ids, random_state = 2000, test_size = 0.1)

train_inputs = torch.tensor(train_inputs)
train_labels = torch.tensor(train_labels)
train_masks = torch.tensor(train_masks)
validation_inputs = torch.tensor(validation_inputs)
validation_labels = torch.tensor(validation_labels)
validation_masks = torch.tensor(validation_masks)

# 배치 사이즈
batch_size = 32

# 파이토치의 DataLoader로 입력, 마스크, 라벨을 묶어 데이터 설정
# 학습시 배치 사이즈 만큼 데이터를 가져옴
train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

validation_data = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)

# 테스트셋 전처리

sentences = test['Sentence']
sentences = ["[CLS] " + str(sentence) + " [SEP]" for sentence in sentences]

labels = test['Emotion'].values
labels = pd.factorize(labels)[0]

tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]

MAX_LEN = 128

input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]
input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

attention_masks = []
for seq in input_ids:
  seq_mask = [float(i>0) for i in seq]
  attention_masks.append(seq_mask)

test_inputs = torch.tensor(input_ids)
test_labels = torch.tensor(labels)
test_masks = torch.tensor(attention_masks)

print(test_inputs[0])
print(test_labels[0])
print(test_masks[0])

batch_size = 16

test_data = TensorDataset(test_inputs, test_masks, test_labels)
test_sampler = RandomSampler(test_data)
test_dataloader = DataLoader(test_data, sampler=test_sampler, batch_size=batch_size)

# 모델 생성
device_name = tf.test.gpu_device_name()

# GPU 디바이스 이름 검사
if device_name == '/device:GPU:0':
    print('Found GPU at: {}'.format(device_name))
else:
    raise SystemError('GPU device not found')

if torch.cuda.is_available():    
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
    print('We will use the GPU:', torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")
    print('No GPU available, using the CPU instead.')

model = BertForSequenceClassification.from_pretrained("monologg/kobert", num_labels=10)
model.cuda()

# 옵티마이저 설정
optimizer = AdamW(model.parameters(),
                  lr = 2e-5, # 학습률
                  eps = 1e-8 # 0으로 나누는 것을 방지하기 위한 epsilon 값
                )

# 에폭수
epochs = 2

# 총 훈련 스텝 : 배치반복 횟수 * 에폭
total_steps = len(train_dataloader) * epochs

# 학습률을 조금씩 감소시키는 스케줄러 생성
scheduler = get_linear_schedule_with_warmup(optimizer, 
                                            num_warmup_steps = 0,
                                            num_training_steps = total_steps)

def flat_accuracy(preds, labels):
    
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()

    return np.sum(pred_flat == labels_flat) / len(labels_flat)

def format_time(elapsed):

    # 반올림
    elapsed_rounded = int(round((elapsed)))
    
    # hh:mm:ss으로 형태 변경
    return str(datetime.timedelta(seconds=elapsed_rounded))

# 재현을 위해 랜덤시드 고정
seed_val = 42
random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

# 그래디언트 초기화
model.zero_grad()

# 에폭만큼 반복
for epoch_i in range(0, epochs):
    
    # ========================================
    #               Training
    # ========================================
    
    print("")
    print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, epochs))
    print('Training...')

    # 시작 시간 설정
    t0 = time.time()

    # 로스 초기화
    total_loss = 0

    # 훈련모드로 변경
    model.train()
        
    # 데이터로더에서 배치만큼 반복하여 가져옴
    for step, batch in enumerate(train_dataloader):
        # 경과 정보 표시
        if step % 500 == 0 and not step == 0:
            elapsed = format_time(time.time() - t0)
            print('  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(step, len(train_dataloader), elapsed))

        # 배치를 GPU에 넣음
        batch = tuple(t.to(device) for t in batch)
        
        # 배치에서 데이터 추출
        b_input_ids, b_input_mask, b_labels = batch

        # Forward 수행                
        outputs = model(b_input_ids, 
                        token_type_ids=None, 
                        attention_mask=b_input_mask, 
                        labels=b_labels)
        
        # 로스 구함
        loss = outputs[0]

        # 총 로스 계산
        total_loss += loss.item()

        # Backward 수행으로 그래디언트 계산
        loss.backward()

        # 그래디언트 클리핑
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # 그래디언트를 통해 가중치 파라미터 업데이트
        optimizer.step()

        # 스케줄러로 학습률 감소
        scheduler.step()

        # 그래디언트 초기화
        model.zero_grad()

    # 평균 로스 계산
    avg_train_loss = total_loss / len(train_dataloader)            

    print("")
    print("  Average training loss: {0:.2f}".format(avg_train_loss))
    print("  Training epcoh took: {:}".format(format_time(time.time() - t0)))
        
    # ========================================
    #               Validation
    # ========================================

    print("")
    print("Running Validation...")

    #시작 시간 설정
    t0 = time.time()

    # 평가모드로 변경
    model.eval()

    # 변수 초기화
    eval_loss, eval_accuracy = 0, 0
    nb_eval_steps, nb_eval_examples = 0, 0

    # 데이터로더에서 배치만큼 반복하여 가져옴
    for batch in validation_dataloader:
        # 배치를 GPU에 넣음
        batch = tuple(t.to(device) for t in batch)
        
        # 배치에서 데이터 추출
        b_input_ids, b_input_mask, b_labels = batch
        
        # 그래디언트 계산 안함
        with torch.no_grad():     
            # Forward 수행
            outputs = model(b_input_ids, 
                            token_type_ids=None, 
                            attention_mask=b_input_mask)
        
        # 로스 구함
        logits = outputs[0]

        # CPU로 데이터 이동
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        
        # 출력 로짓과 라벨을 비교하여 정확도 계산
        tmp_eval_accuracy = flat_accuracy(logits, label_ids)
        eval_accuracy += tmp_eval_accuracy
        nb_eval_steps += 1

    print("  Accuracy: {0:.2f}".format(eval_accuracy/nb_eval_steps))
    print("  Validation took: {:}".format(format_time(time.time() - t0)))

print("")
print("Training complete!")
model.save_pretrained("bert-emotion.h5")
print("Saved model to disk")
#-----------모델 트레이닝 및 저 완료--------------------------


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
        seq_mask = [float(i>0) for i in seq]
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

    # 데이터를 GPU에 넣음
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)
            
    # 그래디언트 계산 안함
    with torch.no_grad():     
        # Forward 수행
        outputs = model(b_input_ids, 
                        token_type_ids=None, 
                        attention_mask=b_input_mask)

    # 로스 구함
    logits = outputs[0]

    # CPU로 데이터 이동
    logits = logits.detach().cpu().numpy()

    return logits



model = model.to(device)
logits = test_sentences(['성적이 낮다고 오늘도 부모님한테 혼났어...난 왜 잘하는게 하나도 없을까'])
print(logits)
print(label_val[np.argmax(logits)])

logits = test_sentences(['나 요즘 너무 우울해...'])
print(logits)
print(label_val[np.argmax(logits)])

model.save_pretrained("bert-emotion.h5") 
print("Saved model to disk")

model = BertForSequenceClassification.from_pretrained("bert-emotion.h5")

model = model.to(device)

logits = test_sentences(['차라리 죽고싶어'])
print(logits)
print(label_val[np.argmax(logits)])

logits = test_sentences(['내가 왜 왕따를 당하고 있는지 모르겠어'])
print(logits)
print(label_val[np.argmax(logits)])

logits = test_sentences(['새로운 곳에 혼자 적응하는게 힘들어'])
print(logits)
print(label_val[np.argmax(logits)])

logits = test_sentences(['그냥 집에만 있고 싶어'])
print(logits)
print(label_val[np.argmax(logits)])

logits = test_sentences(['요즘 밥을 제대로 안 먹게 되는 것 같아'])
print(logits)
print(np.argmax(logits))
print(label_val[np.argmax(logits)])

logits = test_sentences(['차라리 죽어버리면 마음이 편할 것 같아'])
print(logits)
print(label_val[np.argmax(logits)])