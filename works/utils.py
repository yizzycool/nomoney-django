import os, json, math, monpa
from collections import Counter
from scipy.stats import chi2_contingency
import numpy as np
from ckiptagger import WS#, POS


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
STOPWORDS_PATH = os.path.join(BASE_PATH, 'data/stopwords')
WC_PATH = os.path.join(BASE_PATH, 'data/zh.wc')

stopwords = open(STOPWORDS_PATH).read().strip().splitlines()
stopwords = list(map(lambda x: x.strip(), stopwords))

wc_counter = Counter(json.load(open(WC_PATH)))
wc_total = sum(wc_counter.values())

special_tag = ['Na', 'Nb', 'Nc', 'LOC', 'PER', 'ORG']

ws = WS(os.path.join(BASE_PATH, "data/data"))

#pos = POS(os.path.join(BASE_PATH, "data/data"))
#ner = NER(os.path.join(BASE_PATH, "data/data"))

def extract_tokens_pos(text):
    """text = text.strip().replace('\r\n', '，').replace('\n', '，')
    w = ws([text], sentence_segmentation=True, segment_delimiter_set = {",", "，", "。", ":", "：", "?", "？", "!", "！", ";", "；", "\n"})[0]
    p = pos([w])[0]
    word_lists = [(token, tag) for token, tag in zip(w, p) if 'CATEGORY' not in tag and 'SPACE' not in tag and token.lower() not in stopwords]
    return word_lists"""
    lines = text.strip().splitlines()
    w = ws(lines, sentence_segmentation=True, segment_delimiter_set = {",", "，", "。", ":", "：", "?", "？", "!", "！", ";", "；", "\n"})
    w = [tok for tokens in w for tok in tokens]
    word_lists = []
    for line in lines:
        result_pseg = monpa.pseg(line)
        for token, tag in result_pseg:
            if 'CATEGORY' not in tag and 'SPACE' not in tag and token.lower() not in stopwords and (token in w or len(token) >= 3):
                word_lists.append([token, tag])
    return word_lists
    """lines = text.strip().splitlines()
    word_lists = []
    for line in lines:
        result_pseg = monpa.pseg(line)
        for token, tag in result_pseg:
            if 'CATEGORY' not in tag and token.lower() not in stopwords:
                word_lists.append([token, tag])
    return word_lists"""


def extract_tokens(text):
    return [tok for tok, pos in extract_tokens_pos(text)]


def chi_square_test(tok_pos):
    #print(tok_pos)
    if len(tok_pos) == 0: return []
    chi, words_done = [], []
    tok, pos = list(zip(*tok_pos))
    data_len = len(tok)
    for idx in range(len(tok_pos)):
        if pos[idx] not in special_tag or tok[idx] in words_done or len(tok[idx])<2:
            continue
        data_wc = tok.count(tok[idx])
        corpus_wc = wc_counter[tok[idx]]
        obs = np.array(
            [
                [ data_wc, data_len - data_wc ],
                [ corpus_wc + 1, wc_total - corpus_wc]
            ]
        )
        chi2, p, _, _ = chi2_contingency(obs)
        if p < 0.05:
            chi.append([tok[idx], math.log2(chi2), p])
            words_done.append(tok[idx])
    chi = sorted(chi, key=lambda x: (x[1], x[2]), reverse=True)
    #print(chi)
    if len(chi) > 0:
        max_value = chi[0][1]#max([c[1] for c in chi if wc_counter[c[0]] > 0] + [0])
        #print(max_value)
        chi = list(filter(lambda x: x[1] > (max_value / 2.), chi))
    #print(chi)
    return chi[:5]