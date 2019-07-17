# -*- coding: utf-8 -*-

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def vectorize_sim_search(query, data, stop_words="english"):
    """
    query: `str`
    data: `list` de strings
    stop_words: `list` de stopwords (default é "english" do SKlearn)
    
    Retorna:
    cos_sim: primeiro elemento da array `cosine_similarity`
    tfidf_vectorizer: `TfidfVectorizer object`
    data: `data` atualizada com `query` na posição 0
    """
    #Inserindo consulta na posição 0:
    data = [query] + data
    tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf_matrix = tfidf_vectorizer.fit_transform(data)
    cos_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix)
    return cos_sim[0], tfidf_vectorizer, data

def get_most_similar(data, cos_sim, n):
    """
    data: `list` de strings (atualizada em `vectorize_sim_search()`)
    cos_sim: primeiro elemento da array `cosine_similarity`
    n: `int` com número de elementos a retornar
    
    Retorna:
    most_similar: `list` de tuples com `n` documentos mais similares, classificados do mais similar para o menos similar.
    Cada `tuple` contém um valor de similaridade `float` e um documento `str`.
    """
    sorted_indexes = []
    index = 0
    for el in cos_sim:
        sorted_indexes.append((index, el))
        index += 1
    #índices de `data`, organizando do mais similar para o menos similar
    sorted_indexes = sorted(sorted_indexes, key = lambda x: x[1], reverse = True)
    most_similar = []
    for n in range(n):
        most_similar.append((sorted_indexes[n][1], data[sorted_indexes[n][0]]))
    return most_similar