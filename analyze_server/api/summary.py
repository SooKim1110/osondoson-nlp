from analyze_server import app
from flask import jsonify, request
from konlpy.tag import Komoran
from collections import Counter, defaultdict
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.preprocessing import normalize
import math
from analyze_server.module import dbModule
from pymysql.err import IntegrityError
import re

#코드 출처: https://lovit.github.io/nlp/2019/04/30/textrank/
def scan_vocab(sents, tokenize, min_count = 2):
    counter = Counter(w for sent in sents for w in tokenize(sent) if len(sent) != 0)
    counter = {w:c for w,c in counter.items() if c>= min_count}
    idx_to_vocab = [w for w, _ in sorted(counter.items(), key = lambda x:-x[1])]
    vocab_to_idx = {vocab:idx for idx, vocab in enumerate(idx_to_vocab)}
    return idx_to_vocab, vocab_to_idx

def co_occurence(tokens, vocab_to_idx, window = 2, min_cooccurrence = 2):
    counter = defaultdict(int)
    for s, tokens_i in enumerate(tokens):
        vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
        n = len(vocabs)
        for i,v in enumerate(vocabs):
            if window <= 0:
                b,e = 0,n
            else:
                b = max(0, i-window)
                e = min(i+window,n)
            for j in range(b,e):
                if i == j:
                    continue
                # 두 단어 같이 등장할 때마다 카운터 하나씩 늘
                counter[(v,vocabs[j])] += 1
                counter[(vocabs[j],v)] += 1
        counter = {k:v for k,v in counter.items() if v>= min_cooccurrence}
        n_vocabs = len(vocab_to_idx)

        rows,cols,data = [],[],[]
        # counter 형태 key: (단어 i, 단어 j) value: v
        for (i, j), v in counter.items():
            rows.append(i)
            cols.append(j)
            data.append(v)
        return csr_matrix((data,(rows,cols)), shape = (n_vocabs, n_vocabs))

def word_graph(sents, tokenize=None, min_count = 2, window = 2, min_cooccurrence = 2):
            idx_to_vocab, vocab_to_idx = scan_vocab(sents, tokenize, min_count)
            tokens = [tokenize(sent) for sent in sents]
            g = co_occurence(tokens, vocab_to_idx, window, min_cooccurrence)
            return g,idx_to_vocab

# 만들어진 cooccurrence 그래프에 pagerank 학습. column 합이 1이 되도록 normalize. A * R 은 col j에서 row i 로의 랭킹의 전달
def pagerank(x, df = 0.85, max_iter = 30):
    assert 0 < df < 1

    A = normalize(x, axis = 0, norm = 'l1')
    R = np.ones(A.shape[0]).reshape(-1,1)
    bias = (1-df) * np.ones(A.shape[0]).reshape(-1,1)

    for _ in range(max_iter):
        R = df * (A * R) + bias
    return R

def textrank_keyword(sents, tokenize, min_count, window, min_cooccurrence, df=0.85, max_iter=30, topk=10):
    g, idx_to_vocab = word_graph(sents, tokenize, min_count, window, min_cooccurrence)
    R = pagerank(g, df, max_iter).reshape(-1)
    idxs = R.argsort()[-topk:]
    keywords = [(idx_to_vocab[idx], R[idx]) for idx in reversed(idxs)]
    return keywords

def komoran_tokenize(sent):
    komoran = Komoran()
    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
    return words

def sent_graph(sents, tokenize, similarity, min_count = 2, min_sim = 0.3):
    _, vocab_to_idx = scan_vocab(sents,tokenize, min_count)
    tokens = [[w for w in tokenize(sent) if w in vocab_to_idx] for sent in sents]
    rows, cols, data = [], [], []
    n_sents = len(tokens)
    for i, tokens_i in enumerate(tokens):
        for j, tokens_j in enumerate(tokens):
            if i >= j:
                continue
            sim = similarity(tokens_i, tokens_j)
            if sim < min_sim:
                continue
            rows.append(i)
            cols.append(j)
            data.append(sim)
    return csr_matrix((data, (rows, cols)), shape = (n_sents, n_sents))

def textrank_sent_sim(s1,s2):
    n1 = len(s1)
    n2 = len(s2)
    if (n1 <= 1) or (n2 <= 1):
        return 0
    common = len(set(s1).intersection(set(s2)))
    base = math.log(n1) + math.log(n2)
    return common / base

def textrank_keysentence(sents, tokenize, min_count,min_sim, similarity, df = 0.85, max_iter = 30, topk = 3):
    g = sent_graph(sents, tokenize, textrank_sent_sim, min_count, min_sim)
    R = pagerank(g, df, max_iter).reshape(-1)
    idxs = R.argsort()[-topk:]
    keysents = [(idx, R[idx],sents[idx]) for idx in reversed(idxs)]
    return keysents

@app.route('/summary', methods=['POST'])
def analyze_summary():
    counsel_id = request.form['counsel_id']
    text = request.form['text'].strip()
    sents = re.split('(?<=[\.\?\!])\s*', text)
    del sents[-1]

    # text가 빈 경우 예외 처리
    if len(sents) == 0:
        db_class = dbModule.Database()

        main_words = {
            "main_words": ["비어있음"]
        }
        main_words = str(main_words).replace("'", '"')
        main_sentences = {
            "main_sentences": ["인식된 상담 텍스트가 없습니다."]
        }
        main_sentences = str(main_sentences).replace("'", '"')

        sql1 = "INSERT INTO sys.db_counseling_analysis(counseling_id_id, main_words, main_sentences) \
                VALUES('%s','%s','%s') ON DUPLICATE KEY UPDATE main_words = '%s', main_sentences = '%s' " \
              % (counsel_id,main_words,main_sentences,main_words, main_sentences)
        sql2 = "UPDATE sys.db_counseling SET analysis_complete = 1 \
                WHERE counseling_id = '%s'" \
                % (counsel_id)

        try:
            db_class.execute(sql1)
            db_class.execute(sql2)
            db_class.commit()
        except IntegrityError as ex:
            return jsonify(main_sentences, {'ERROR': str(ex)}), 409
        finally:
            db_class.close()
        return jsonify({'ERROR': "text is empty"}), 400

    #키워드 추출
    if len(text) < 300:
        # 키워드 방식 1) 형태소 분석 후 최다 빈도 단어 추출 - 짧은 고민에 적합
        komoran = Komoran()
        words = []
        for word in komoran.pos(text):
            if len(word[0]) < 2:
                continue
            if word[1] in ['VV','VA','NNG', 'NNP', 'XR']:
                words.append(word[0])

        count = Counter(words)
        keywords = count.most_common(10)
        main_words = []
        for word in keywords:
            if (word[1] >= 2):
                main_words.append(word[0])

    else:
        # 키워드 방식 2) TextRank 기반 키워드 추출 - 긴 고민에 적합
        keywords = textrank_keyword(sents, komoran_tokenize, 2, 2, 2, 0.85, 20, 10)
        main_words = []
        for i, word in enumerate(keywords):
            if i > 10:
                break
            if word[1] >= 0.3:
                main_words.append(word[0].split('/')[0])

    # 주요 문장 추출
    summarizer = textrank_keysentence(sents, komoran_tokenize,2,0.4,textrank_sent_sim,0.85,20,3)

    main_sentences = []
    for i in range(min(3,len(summarizer))):
        main_sentences.append(summarizer[i][2])

    main_words = {
        "main_words": main_words
    }
    main_words = str(main_words).replace("'", '"')

    main_sentences = {
        "main_sentences": main_sentences
    }
    main_sentences = str(main_sentences).replace("'", '"')

    db_class = dbModule.Database()

    sql = "INSERT INTO sys.db_counseling_analysis(counseling_id_id, main_words, main_sentences) \
           VALUES('%s','%s','%s') ON DUPLICATE KEY UPDATE main_words ='%s', main_sentences = '%s' " \
          % (counsel_id, main_words, main_sentences, main_words, main_sentences)
    sql2 = "UPDATE sys.db_counseling SET analysis_complete = 1 \
            WHERE counseling_id = '%s'" \
          % (counsel_id)
    try:
        db_class.execute(sql)
        db_class.execute(sql2)
        db_class.commit()
    except IntegrityError as ex:
        return jsonify(main_words, main_sentences, {'ERROR': str(ex)}), 409
    finally:
        db_class.close()

    return jsonify(main_words,main_sentences), 201


