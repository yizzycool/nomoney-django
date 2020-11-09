from os.path import join, abspath, dirname
p = dirname(dirname(abspath(__file__)))
print(p)
b = join(dirname(dirname(abspath(__file__))), 'data/stopwords')
print(b)
