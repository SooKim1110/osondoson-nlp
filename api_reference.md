BaseUrl =>  <b>3.34.247.202:3000/api</b>

|           기능              |        URL         | 메소드   | 요청값  |
| :-----------------------:  | :----------------: | :----: | :----: |
|    감정 분석 및 응급 상황 분석   |     /sentiment     |  POST  |  body  |
|       상담 내용 분석          |     /summary       |  POST  |  body  |
|         음성 분석            |     /voice         |  POST  |  body  |


### 감정 분석 및 응급 상황 분석

url : <b>/sentiment</b>

method : <b>POST</b>

> Request

```java
{
  text: String
  counsel_id: Integer
}
```

> Response

 예시 
```java
[
    {"gloom_score": 64.83251971658319, //0~100 사이의 점수
      "danger_sentences": ["차라리 죽고 싶어요"],
      "danger_alarm": "위험" //[긴급, 위험, 주의, 보통, 안정] 5단계 
    },
    {"radar_chart": [3, 2, 1, 2, 0, 0, 0], //순서대로 [우울, 중립, 불안, 공포, 분노, 자살, 행복] 문장의 개수
      "pie_chart": [0.0, 25.0, 75.0, 8] //순서대로 [긍정, 중립, 부정, 총 문장 개수]
    }
]

```

### 음성 분석
(+ 추후 추가)


### 상담 내용 분석 
url : <b>/sentiment</b>

method : <b>POST</b>

> Request

```java
{
  text: String
  counsel_id: Integer
}
```

> Response

 예시 
```java
[
    {"main_words": ["예전", "학년", "왕따", "중학교", "친구"]},
    {"main_sentences": ["예전에 서울에서 4학년 때 왕따를 당했어요", "6학년에서 중학교 올라갈 즈음에 인천으로 이사왔어요", "사실 궁금해서 자해를 시도했어요"]}
]

```