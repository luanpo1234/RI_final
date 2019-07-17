 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tfidf_similarity as s
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import variation as cv
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.collocations import *
import pandas as pd
import re
import string
import matplotlib.pyplot as plt

from df_processer import df

def repl_accents(text):
    accents = ["áãâçéêíóôõú", "aaaceeiooou"]
    for n in range(len(accents[0])):
        text = text.replace(accents[0][n], accents[1][n])
    return text

def preprocess(text, stem=False, tokenize=True):
    stopwords = nltk.corpus.stopwords.words('portuguese') + ["sendo"]
    stopwords = [repl_accents(w) for w in stopwords]
    stemmer = SnowballStemmer("portuguese")
    #Tirar pontuação:
    text = text.translate(str.maketrans('', '', string.punctuation))
    #Transformar em minúsculas:
    text = text.lower()
    #Eliminar dígitos:
    text = text.translate(str.maketrans('', '', string.digits))
    #Tirar acentos:
    text = repl_accents(text)
    #Tokenizar:
    text = nltk.word_tokenize(text)
    #Tirar stopwords:
    text = [w for w in text if w not in stopwords]
    #Usar stemmer se stem=True:
    if stem == True:
        text = [stemmer.stem(w) for w in text]
    #Foi preciso tokenizar antes para fazer as transformações:
    if tokenize == False:
        text = " ".join(text)
    return text

def get_freqs(text, stem=False, bgs=False):
    text = preprocess(text, stem=stem)
    if bgs == True:
        text = nltk.bigrams(text)
    freqs = nltk.FreqDist(text)
    return freqs

def get_freqs_terms(freqs_lists, terms, normalize=False):
    """
    freqs_lists: `list` com `FreqDists` do NLTK
    terms: `list` de termos no formato `str`
    normalize: se `True`, retorna valores relativos (somados a 1)
    
    Retona `dict` {termo: `list` com frequência do termo em cada item de `freqs_lists`}
    """
    def norml(lst):
        try:
            return [float(el)/sum(lst) for el in lst]
        except ZeroDivisionError:
            return [0, 0, 0, 0, 0]
    res = {}
    for term in terms:
        res[term] = [lst[term] for lst in freqs_lists]
    if normalize == True:
        #Normaliza para valores relativos (sempre soma para 1)
        res = {el: norml(res[el]) for el in res}
    return res

def term_freq_plot(ranges, terms, title="", save_fig=None):
    """
    """
    fig, ax = plt.subplots()
    for key in terms.keys():
        ax.plot(ranges, terms[key], label=key)
    ax.legend()
    plt.title(title)
    plt.xlabel("Faixa de preço em milhares de R$")
    plt.ylabel("Frequência dos termos")
    if save_fig:
        plt.savefig(save_fig)
    else:
        plt.show()

def get_direction(freqs_lists):
    asc, desc, mid = [], [], []
    for el in freqs_lists:
        if el[1][0] == min(el[1]):
            asc.append(el)
        elif el[1][0] == max(el[1]):
            desc.append(el)
        else:
            mid.append(el)
    return asc, desc, mid

def test_coocurrence(df_, col, w1, w2):
    count_1 = 0
    count_2 = len(df_.loc[col.str.contains(w1)])
    for el in col:
        if len(re.findall(w1, el)) > 0 and len(re.findall(w2, el)) == 0:
            count_1 += 1
    prop = count_1/count_2
    print("Presença de {} sem {}: {}".format(w1, w2, prop))
    return prop

def find_ngrams(n_grams, n, words, min_freq=1, term=None):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()
    if n_grams == 2:
        finder = BigramCollocationFinder.from_words(nltk.word_tokenize(words))
    elif n_grams == 3:
        finder = TrigramCollocationFinder.from_words(nltk.word_tokenize(words))
    # Ngrams incluindo `term`
    if term:
        filter_ = lambda *w: term not in w
        finder.apply_ngram_filter(filter_)
    ## Bigramas
    finder.apply_freq_filter(min_freq)
    if n_grams == 2:
        return finder.nbest(bigram_measures.likelihood_ratio, n)
    #Trigramas
    if n_grams == 3:
        return finder.nbest(trigram_measures.likelihood_ratio, n)

#Criando nova coluna no df com texto de descrição pré-processado:
print("Pré-processando df.desc...")
df["preprocessed_desc"] = [preprocess(el, tokenize=False) for el in df.desc]

#Pré-processando df.amenities:
print("Pré-processando df.amenities...")
df['amenities'] = df['amenities'].map(lambda x: [repl_accents(el) for el in x])

#Separando dados do df em 5 faixas de preço:
dfs_per_range = []
quants = (0, .2, .4, .6, .8, 1)
for n in range(len(quants)-1):
    dfs_per_range.append(df.loc[(df.price >= df.price.quantile(quants[n]))\
                                & (df.price < df.price.quantile(quants[n+1]))])

for el in dfs_per_range:
    print(len(el), max(el.price))

#Faixas de preço em formato legível p/ gráficos:
PRICE_RANGES = ["89-300", "300-440", "440-600", "600-985", "985+"]

#Será usado para calcular semelhança cosseno tf*idf:
docs_per_range = []
#Pegando tokens de todos os documentos em cada faixa de preço 
#unificados em lista de frequências:
#Palavras individuais:
words_per_range = []
#Bigramas:
bgs_per_range = []
#df.amenities:
amens_per_range = []

for el in enumerate(dfs_per_range):
    print("Processando dataframe {}/{}...".format(el[0]+1, len(dfs_per_range)))
    vocab = " ".join(el[1].preprocessed_desc)
    docs_per_range.append(vocab)
    w_freq = get_freqs(vocab)
    bgs_freq = get_freqs(vocab, bgs=True)
    words_per_range.append(w_freq)
    bgs_per_range.append(bgs_freq)
    #Pegando valores em 'amenities':
    amens = []
    for item in el[1].amenities:
        amens += item
    amens_per_range.append(nltk.FreqDist(amens))

#Pesquisa de similaridade de cosseno TF*IDF:
print("Pesquisa de similaridade...")
cos_sim, vectorizer, data = s.vectorize_sim_search(docs_per_range[0], \
                                                   docs_per_range, stop_words=None)
most_sim = [x[0] for x in s.get_most_similar(data, cos_sim, len(data))][1:]

plt.bar(PRICE_RANGES, most_sim)
plt.title("Similaridade entre as descrições por faixa de preço")
plt.ylabel("Similaridade de cosseno TF * IDF")
plt.xlabel("Faixa de preço em milhares de R$")
#plt.show()
plt.savefig("img/cos_sim.png")

#Como são poucos documentos grande e semelhantes, IDF não é muito útil para a análise:
tfidf = TfidfVectorizer(use_idf=True)
tfidf_matrix = tfidf.fit_transform(df.preprocessed_desc)
idf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
print("idf max e min: ", min(idf.values()), max(idf.values()))

#Freqs de TF*IDF considerando cada anúncio como um documento:
tfidf_freqs = []
for el in words_per_range:
    d = {}
    for term in el.keys():
        try:
            d[term] = el[term] * idf[term]
        except KeyError:
            continue
    tfidf_freqs.append(sorted(d.items(), key = lambda x:x[1], reverse=True))

#Fluxo para cálculo de diferença entre frequências:
def freqs_flow(tokens_per_range, min_freq):
    tpr = [d.items() for d in tokens_per_range]
    top_tpr = []
    for el in tpr:
        top_tpr.extend([x[0] for x in el if x[1] >= min_freq])
    top_unique = set(top_tpr)
    freqs_terms = get_freqs_terms(tokens_per_range, top_unique)
    cv_freqs = {term:cv(freqs_terms[term]) for term in freqs_terms.keys()}
    cv_freqs = sorted(cv_freqs.items(), key = lambda x:x[1], reverse=True)
    #Organizando listas de freqs por distancia maior x menor:
    diff_freqs = [el for el in freqs_terms.items() if min(el[1]) <= max(el[1])*.3]
    diff_freqs = sorted(diff_freqs, key = lambda x:cv(x[1]), reverse=True)
    return top_tpr, top_unique, freqs_terms, diff_freqs

top_wpr, top_unique, freqs_terms, diff_freqs = freqs_flow(words_per_range, 50)
top_bpr, top_unique_b, freqs_bgs, diff_freqs_bgs = freqs_flow(bgs_per_range, 50)

#Só roda uma vez para salvar items pro dict de tags:
#with open('tag_dict.csv', 'w') as f:
#    for item in diff_freqs:
#        f.write("%s\n" % item[0])
#with open('bg_tag_dict.csv', 'w') as f:
#    for item in diff_freqs_bgs:
#        f.write("%s\n" % str(item[0][0] + " " + item[0][1]))

#Gerando DFs, unindo tags de palavras individuais e bigramas:
df2 = pd.read_excel('bg_tag_dict.xlsx', names=['item', 'tag'])
df3 = pd.read_excel('tag_dict.xlsx', names=['item', 'tag'])
df2 = pd.concat([df2, df3])

#Testando coocorrências:
print("Coocorrências de palavras selecionadas:")
print(test_coocurrence(df, df.preprocessed_desc, "raia", "piscina"))
print(test_coocurrence(df, df.preprocessed_desc, "ar", "condicionado"))
print(test_coocurrence(df, df.preprocessed_desc, "lazer", "completo|area"))
print(find_ngrams(2, 30, " ".join(df.preprocessed_desc), min_freq=50, term="lazer"))

#Testando funções de plotar termos  por faixa de preço:
if __name__=="__main__":
    freqs_terms = get_freqs_terms(words_per_range, \
                                  [el for el in list(df3.loc[df3.tag == "FIN"]["item"])])
    print("Plotando...")
    print(freqs_terms)
    term_freq_plot(PRICE_RANGES, freqs_terms, save_fig='img/fin_freqs',\
                   title = "Termos financeiros por faixa de preço")