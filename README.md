# [오손도손: 또래 상담 플랫폼] 상담 분석 모델 & 상담 가이드 챗봇 
<div align="center">
  <br/><br/>
  <img src="/uploads/63d16d51d142269079f28574e9208535/Screen_Shot_2020-11-04_at_4.56.35_PM.png" width="500" > <br/><br/>
  오손도손은 청소년들이 온라인 상에서 쉽고 편하게 또래 상담을 하여 고민을 해소할 수 있도록 돕는 <b>'또래상담 플랫폼'</b>입니다. <br/><br/>
  특히, 상담 내용 음성인식을 통해 <b>청소년들의 감정을 지속적으로 파악/관리하는 상담 분석 기능</b>과 <b>문제 상황별 상담 가이드를 제공하는 챗봇 기능</b>을 통해 <br/><br/>
  내담 학생, 또래 상담자, 담당 교사 모두가 <b>효율적이고 전문적인 상담</b>을 할 수 있도록 돕습니다.  <br/><br/>
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
### 1-(1) 감정 분석 (한국어 다중 감성분류 multi-class sentiment classification)
##### 구현에는 KcBERT와 Huggingface Transformers 사용

✔ 각 문장을 상담 상황과 관련된 7가지 감정(행복, 중립, 공포, 분노, 우울, 자살, 불안)으로 분류  
✔ 분류된 문장들의 감정 정보를 활용하여 내담자의 우울 정도 및 위험 여부, 위험 표현 문장 파악 

<img src="/uploads/68ad9ffb9ec768dd2b3bc7cec0d24d3f/감정분석.png"  width="800" >

#### 사용 데이터셋

정신 건강 의미어 데이터 (AI Hub)
웰니스 대화 스크립트 데이터 (AI Hub)
1388 댓글 상담실 데이터 (크롤링)
 
 
#### 결과 예시
입력 문장 
```
예전에 서울에서 4학년 때 왕따를 당했어요. 그 후 계속 은따. 6학년에서 중학교 올라갈 즈음에 인천으로 이사왔어요. 
그때는 얘들이랑 잘 지냈는데 중학교 가서 중1 때 한 얘가 저에게 배신을 했어요. 
예전에 왕따당한 트라우마가 더 심해져서 더 이상 친구를 사귀지 못하고 현재 중3까지도 친구가 없어. 
차라리 죽고싶어요. 가만히 있어도 심장이 뛰네요. 
```

## References

- [Huggingface Transformers](https://github.com/huggingface/transformers)
- [네이버 영화리뷰 감정분석 with Hugging Face BERT](https://colab.research.google.com/drive/1tIf0Ugdqg4qT7gcxia3tL7und64Rv1dP#scrollTo=P58qy4--s5_x)
- [KoBERT](https://github.com/SKTBrain/KoBERT)
- [KoBERT Transformers](https://github.com/monologg/KoBERT-Transformers)