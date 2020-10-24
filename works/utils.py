import monpa, os, json
from collections import Counter
from scipy.stats import chi2_contingency
import numpy as np

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
STOPWORDS_PATH = os.path.join(BASE_PATH, 'data/stopwords')
WC_PATH = os.path.join(BASE_PATH, 'data/zh.wc')

stopwords = open(STOPWORDS_PATH).read().strip().splitlines()
stopwords = list(map(lambda x: x.strip(), stopwords))

wc_counter = Counter(json.load(open(WC_PATH)))
wc_total = sum(wc_counter.values())


def extract_tokens_pos(text):
    lines = text.strip().splitlines()
    word_lists = []
    for line in lines:
        result_pseg = monpa.pseg(line)
        for token, tag in result_pseg:
            if 'CATEGORY' not in tag and token.lower() not in stopwords:
                word_lists.append([token, tag])
    return word_lists


def extract_tokens(text):
    return [tok for tok, pos in extract_tokens_pos(text)]


def chi_square_test(word_list):
    chi = []
    data_len = len(word_list)
    for token in list(set(word_list)):
        data_wc = word_list.count(token)
        corpus_wc = wc_counter[token]
        obs = np.array(
            [
                [ data_wc, data_len - data_wc ],
                [ corpus_wc + 1, wc_total - corpus_wc]
            ]
        )
        chi2, p, _, _ = chi2_contingency(obs)
        if p < 0.05:
            chi.append([token, chi2, p])
    return sorted(chi, key=lambda x: (x[1], x[2]), reverse=True)