import os, json, math, monpa
from collections import Counter
from scipy.stats import chi2_contingency
import numpy as np
from ckiptagger import WS#, POS, NER
from pathlib import Path

# path setting
BASE_PATH = Path(__file__).resolve().parent.parent
STOPWORDS_PATH = os.path.join(BASE_PATH, 'data/stopwords')
WC_PATH = os.path.join(BASE_PATH, 'data/zh.wc')

# open stopwords list
stopwords = open(STOPWORDS_PATH).read().strip().splitlines()
stopwords = list(map(lambda x: x.strip(), stopwords))

# open word count as dict
wc_counter = Counter(json.load(open(WC_PATH)))
wc_total = sum(wc_counter.values())

# POS tags that can be used as hashtag
special_tag = ['Na', 'Nb', 'Nc', 'LOC', 'PER', 'ORG']

# CKIP tagger init setting
ws = WS(os.path.join(BASE_PATH, "data/data"))
#pos = POS(os.path.join(BASE_PATH, "data/data"))
#ner = NER(os.path.join(BASE_PATH, "data/data"))


def extract_tokens(text):
    return [tok for tok, pos in extract_tokens_pos(text)]


def remove_stopwords():
    pass


def extract_tokens_pos(text):
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
    if len(chi) > 0:
        max_value = chi[0][1]
        chi = list(filter(lambda x: x[1] > (max_value / 2.), chi))
    return chi[:5]