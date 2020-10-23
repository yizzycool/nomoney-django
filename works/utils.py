import monpa, os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
STOPWORDS_PATH = os.path.join(BASE_PATH, 'data/stopwords')

stopwords = open(STOPWORDS_PATH).read().strip().splitlines()
stopwords = list(map(lambda x: x.strip(), stopwords))

def extract_tokens(text):
    lines = text.strip().splitlines()
    word_lists = []
    for line in lines:
        result_pseg = monpa.pseg(line)
        for token, tag in result_pseg:
            if 'CATEGORY' not in tag and token.lower() not in stopwords:
                word_lists.append(token)
    return word_lists
                