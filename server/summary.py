from server import app
from flask import jsonify, request
from konlpy.tag import Komoran
from collections import Counter, defaultdict
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.preprocessing import normalize
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


@app.route('/summary', methods=['POST'])
def summary():
    text = request.form['text']

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
        frequent_words = []
        for word in keywords:
            if (word[1] >= 2):
                frequent_words.append(word[0])

    else:
        # 키워드 방식 2) TextRank 기반 키워드 추출 - 긴 고민에 적합 (분석 시간이 오래걸림)
        sents = text.split('.')
        keywords = textrank_keyword(sents, komoran_tokenize, 2, 2, 2, 0.85, 30, 10)
        frequent_words = []
        for i, word in enumerate(keywords):
            if i > 10:
                break
            if word[1] >= 0.3:
                frequent_words.append(word[0].split('/')[0])

    # 주요 문장 추출
    main_sentences = []


    return jsonify({'frequent_words': frequent_words, 'main_sentences': main_sentences})

