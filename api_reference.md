BaseUrl =>  <b>host:port/api</b>

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
}
```

> Response

 예시 
```java
{
    "emergency": {
        "danger_alarm": [
            "주의"
        ],
        "danger_sentences": [
            " 차라리 죽고싶어요",
            " 사실 궁금해서 자해를 시도했어요"
        ],
        "gloom_score": 63.508033752441406
    },
    "label_key": [
        "우울",
        "중립",
        "불안",
        "자살",
        "행복",
        "분노",
        "공포"
    ],
    "sentiment": {
        "pie_chart": [
            0.0,
            75.0,
            25.0
        ],
        "radar_chart": [
            3,
            2,
            1,
            2,
            0,
            0,
            0
        ]
    }
}
}
```

### 음성 분석



### 상담 내용 분석 

url : <b>/sentiment</b>

method : <b>POST</b>

> Request

```java
{
  text: String
}
```

> Response

 예시 
```java
{
    "main_sentences": [
        "예전에 서울에서 4학년 때 왕따를 당했어요",
        " 6학년에서 중학교 올라갈 즈음에 인천으로 이사왔어요",
        " 사실 궁금해서 자해를 시도했어요"
    ],
    "main_words": [
        "예전",
        "학년",
        "왕따",
        "중학교",
        "친구"
    ]
}

```
