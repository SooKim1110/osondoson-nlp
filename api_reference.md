BaseUrl =>  <b>host:port/api</b>

|           기능              |        URL         | 메소드   | 요청값  |
| :-----------------------:  | :----------------: | :----: | :----: |
|         감정 분석            |     /sentiment     |  POST  |  body  |
|         음성 분석            |     /voice         |  POST  |  body  |
|       상담 내용 분석          |     /summary       |  POST  |  body  |
|       응급 상황 분석          |     /emergency     |  POST  |  body  |


### 감정 분석

url : <b>/sentiment</b>

method : <b>POST</b>


> Request

```java
{
  text: String
}
```

> Response

```java
{
    "danger_alarm": true,
    "danger_sentences": [
        " 차라리 죽고싶어요",
        " 사실 궁금해서 자해를 시도했어요"
    ],
    "danger_sentences_num": 2,
    "gloom_idx": 63.508033752441406,
    "label_list": [
        "우울",
        "우울",
        "중립",
        "중립",
        "우울",
        "자살",
        "불안",
        "자살"
    ],
    "label_num_list": [
        3,
        2,
        1,
        2,
        0,
        0,
        0
    ]
}
```

### 음성 분석


### 상담 내용 분석 

### 응급 상황 분