# [오손도손: 또래 상담 플랫폼] 상담 분석 모델 & 상담 가이드 챗봇 

<div align="center">
  <br/><br/>
  <img src="/uploads/057ae484d0500c30b75db919b68d885c/Screen_Shot_2020-11-04_at_6.39.38_PM.png" width="600" > <br/><br/>
  오손도손은 청소년들이 온라인 상에서 쉽고 편하게 또래 상담을 하여 고민을 해소할 수 있도록 돕는 <b>'또래상담 플랫폼'</b>입니다. <br/><br/>
  특히, 상담 내용 음성인식을 통해 <b>청소년들의 감정을 지속적으로 파악/관리하는 상담 분석 기능</b>과 <b>문제 상황별 상담 가이드를 제공하는 챗봇 기능</b>을 통해 <br/><br/>
  내담 학생, 또래 상담자, 담당 교사 모두가 <b>효율적이고 전문적인 상담</b>을 할 수 있도록 돕습니다.  <br/><br/>
  <br/><br/>
</div>


## 프로젝트 디렉토리 구조 :open_file_folder:
    .
    ├── analyze_server                 # 상담 분석 서버
    ├── chatbot_server                 # 상담 가이드 챗봇 서버 
    ├── sentiment_model                # 감정 분석 모델 소스 코드 (훈련, 전처리 등)
    ├── docs                           # 관련 문서 (API 문서 등)
    ├── etc                            # 기타
    └── README.md


<br/><br/>
## 1. 상담 분석 모델 :clipboard:

## 1-1) 감정 분석 (한국어 다중 감성분류 multi-class sentiment classification) :smiley:
#### KcBERT와 Huggingface Transformers 사용하여 감정 분석 모델 구현 
> - 각 문장을 상담 상황과 관련된 7가지 감정(행복, 중립, 공포, 분노, 우울, 자살, 불안)으로 분류  
> - 분류된 문장들의 감정 정보를 활용하여 내담자의 우울 정도, 응급 상황 및 위험 표현 문장 파악 
> - 훈련에 사용된 데이터셋 => 정신 건강 의미어 데이터 (AI Hub), 웰니스 대화 스크립트 데이터 (AI Hub), 1388 댓글 상담실 데이터 (크롤링)

<div align="center">
  <img src="/uploads/68ad9ffb9ec768dd2b3bc7cec0d24d3f/감정분석.png"  width="800" >
</div>
<br/><br/>

## 1-2) 주요 내용 분석 (주요 단어, 문장 추출) :memo:
- TextRank 를 이용한 주요 단어, 문장 추출 (extractive summarization)
- 내담 학생이 말한 상담 내용 안에서 주요 단어와 문장을 골라내어, 담당 교사가 빠르게 학생의 상황을 파악할 수 있음 

<br/><br/>
## 1-3) 상담 분석 결과 예시
##### 입력 상담 내용
```
예전에 서울에서 4학년 때 왕따를 당했어. 그 후 계속 은따. 6학년에서 중학교 올라갈 즈음에 인천으로 이사왔어. 그때는 애들이랑 잘 지냈는데 중학교 가서 중1 때 한 애가 저에게 배신을 했어.
예전에 왕따당한 트라우마가 더 심해져서 더 이상 친구를 사귀지 못하고 현재 중3까지도 친구가 없어. 차라리 죽고싶다 진짜. 요즘엔 가만히 있어도 심장이 뛰어.
사실 궁금해서 자해를 시도하기도 했어. 내 이야기 들어줘서 고마워! 조금 괜찮아진 것 같아.
```
##### 분석 결과 
<div align="center">
<img src="/uploads/ef8ae78f7bbd0248df7b163a1282bb2a/Screen_Shot_2020-11-04_at_8.44.56_PM.png" width="700">
</div>

<br/><br/>
## 2. 상담 가이드 챗봇 :speech_balloon:
#### Rasa 챗봇 프레임워크를 토대로 한국어 형태소 분석기 Mecab & fastText 한국어 임베딩을 활용하여 챗봇 학습
> - 또래 상담자에게 문제 상황별 1) 관련 기관 2) 예시 답변 3) 콘텐츠(영상, 글)을 추천하여 알려주어 더욱 전문적인 또래 상담이 가능하도록 함
> - 머신 러닝 기반으로 학생의 질문 의도를 분류하기 때문에 오탈자나 신조어 등이 포함된 질문에도 비교적 정확하게 답을 할 수 있음 
<br/><br/>
##### 상담 가이드 챗봇 사용 예시
<div align="center">
<img src="/uploads/fee077b3f29067f3474dc2b0a41ec681/chatbot-gif2.gif" width="700">
<p>(* 시연을 위해 오타 등을 포함한 질문을 입력하였습니다.)</p>
</div>


<br/><br/>
## References

- [Huggingface Transformers](https://github.com/huggingface/transformers)
- [네이버 영화리뷰 감정분석 with Hugging Face BERT](https://colab.research.google.com/drive/1tIf0Ugdqg4qT7gcxia3tL7und64Rv1dP#scrollTo=P58qy4--s5_x)
- [KoBERT](https://github.com/Beomi/KcBERT)
- [Rasa Open Source](https://github.com/rasahq/rasa/)