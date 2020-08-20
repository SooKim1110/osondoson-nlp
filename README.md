# 참교육 NLP Model

## 1. 감정 분류 모델
### BERT 모델 이용한 한국어 다중 감성분류(multi-class sentiment)
##### 구현에는 KoBERT와 Huggingface Transformers 사용

✔ 각 문장을 상담 상황과 관련된 7가지 감정(행복, 중립, 공포, 분노, 우울, 자살, 불안)으로 분류  
✔ 분류된 문장들의 감정 정보를 활용하여 내담자의 우울 정도 및 위험 여부 파악 

<img src="/uploads/e701583d02f979d60c6bbda77c9c01e4/Flow1.png"  width="800" >

#### 사용 데이터셋

정신 건강 의미어 데이터   
웰니스 대화 스크립트 데이터    
1388 댓글 상담실 데이터 
 
 
#### 결과 예시

##### 입력 상담 내용

```
예전에 서울에서 4학년 때 왕따를 당했어요. 그 후 계속 은따. 6학년에서 중학교 올라갈 즈음에 인천으로 이사왔어요. 
그때는 얘들이랑 잘 지냈는데 중학교 가서 중1 때 한 얘가 저에게 배신을 했어요. 
예전에 왕따당한 트라우마가 더 심해져서 더 이상 친구를 사귀지 못하고 현재 중3까지도 친구가 없어. 
차라리 죽고싶어요. 가만히 있어도 심장이 뛰네요. 
```


##### 결과
```
{
  "danger_alarm": true,
  "danger_sentences": [
    " 차라리 죽고싶어요"
  ],
  "danger_sentences_num": 1,
  "gloom_idx": 75.85022449493408,
  "label_list": [
    "우울",
    "우울",
    "중립",
    "중립",
    "우울",
    "자살",
    "불안"
  ],
  "label_num_list": [
    3,
    2,
    1,
    1,
    0,
    0,
    0
  ]
}
```

## References

- [Huggingface Transformers](https://github.com/huggingface/transformers)
- [네이버 영화리뷰 감정분석 with Hugging Face BERT](https://colab.research.google.com/drive/1tIf0Ugdqg4qT7gcxia3tL7und64Rv1dP#scrollTo=P58qy4--s5_x)
- [KoBERT](https://github.com/SKTBrain/KoBERT)
- [KoBERT Transformers](https://github.com/monologg/KoBERT-Transformers)
