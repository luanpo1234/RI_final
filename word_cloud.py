from wordcloud import WordCloud
from text_processer import dfs_per_range as dfs
from text_processer import df2
from text_processer import df3
from text_processer import words_per_range
from text_processer import bgs_per_range
from text_processer import amens_per_range
from text_processer import idf as idf
from pprint import pprint
import grouped_color_func as gcf
import matplotlib.pyplot as plt

idf_sorted = sorted(idf.items(), key = lambda x:x[1])
#De 10056 elementos,tirando os 100 mais comuns:
sw = [el[0] for el in idf_sorted[:100]] +['apto', 'imoveis']

#Unindo freqs de palavras individuais e bigramas:
terms_per_range = []
for n in range(len(words_per_range)):
    wpr = words_per_range[n].copy()
    #Adaptando keys para o formato string para leitura na função `plot_wcs_from_freqs()`
    wpr.update({" ".join(k): v for k, v in bgs_per_range[n].items()})
    terms_per_range.append(wpr)

#Atribuicação de cores para cada categoria:
color_to_words = {
    'orange': df2.loc[df2.tag == "QUAL"]["item"],
    'brown': df2.loc[df2.tag == "CONV"]["item"],
    'blue': df2.loc[df2.tag == "CAR"]["item"],
    'purple': df2.loc[df2.tag == "BAI"]["item"],
    'red': df2.loc[df2.tag == "REC"]["item"],
    'green': df2.loc[df2.tag == "FIN"]["item"]
}

# Cor de elementos que não se encaixam em nenhuma categoria:
default_color = 'black'

#função para atribuição de cores, fonte: 
#https://amueller.github.io/word_cloud/auto_examples/colored_by_group.html
simple_color_func = gcf.SimpleGroupedColorFunc(color_to_words, default_color)

def get_list_items(df_, tags):
    lst = []
    for tag in tags:
        lst.extend(list(df_.loc[df_["tag"] == tag]["item"]))
    return lst

def plot_wcs_from_freqs(ranges, lst=None, stopwords=[""], collocations=False,
                        save_path=None, color_func=None):
    i = 1
    for el in ranges:
        d = {}
        for key in el.keys():
            if lst:
                if key in lst and key not in stopwords:
                    d[key] = el[key]
            elif key not in stopwords:
                    d[key] = el[key]
        wc = WordCloud(collocations=collocations, background_color="white")\
        .generate_from_frequencies(d)
        if color_func:
            wc.recolor(color_func=simple_color_func)
        if save_path:
            to_save = save_path + "_" + str(i) + ".png"
            wc.to_file(to_save)
            print(to_save, " salvo")
            i += 1
        else:
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.show()

def plot_wcs_from_text(ranges, col, stopwords=None, collocations=False,
                        save_path=None, color_func=None):
    i = 1
    for el in ranges:
        text = " ".join(el[col])
        wc = WordCloud(collocations=collocations, background_color="white",\
                       stopwords=stopwords).generate(text)
        if color_func:
            wc.recolor(color_func=simple_color_func)
        if save_path:
            to_save = save_path + "_" + str(i) + ".png"
            wc.to_file(to_save)
            print(to_save, " salvo")
            i += 1
        else:
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.show()

df3.dropna(inplace=True)
df2.dropna(inplace=True)
print("Número de termos com cada tag, sem incluir bigramas:\n\n")
print(df3.groupby(df3.tag).count())
print("Número de termos com cada tag, incluindo bigramas:\n\n")
print(df2.groupby(df2.tag).count())
###Gerando wordclouds:

#Sem filtro, sem bigramas:
plot_wcs_from_text(dfs, "preprocessed_desc", collocations=False,
                        save_path="img/wc", color_func=simple_color_func)

#Sem filtro, com bigramas:
plot_wcs_from_text(dfs, "preprocessed_desc", collocations=True,
                        save_path="img/wc_bigrams", color_func=simple_color_func)

#Com filtro de stopwords, sem bigramas:
plot_wcs_from_text(dfs, "preprocessed_desc", collocations=False, stopwords = sw,
                        save_path="img/wc_sw", color_func=simple_color_func)

#Com filtro de stopwords, com bigramas:
plot_wcs_from_text(dfs, "preprocessed_desc", collocations=True,
                        save_path="img/wc_sw_bigrams", color_func=simple_color_func)

#Incluindo somente termos marcados com tags, sem bigramas:
plot_wcs_from_freqs(words_per_range, list(df2["item"]), \
                    save_path="img/wc_tagged", color_func=simple_color_func)

#Incluindo somente termos marcados com tags, excluindo stopwords, sem bigramas:
plot_wcs_from_freqs(words_per_range, list(df2["item"]), stopwords=sw,
                    save_path="img/wc_tagged_sw", color_func=simple_color_func)

#Incluindo somente termos marcados com as tags CONV, QUAL e FIN, sem bigramas:
plot_wcs_from_freqs(words_per_range, get_list_items(df2, ["QUAL", "CONV", "FIN"]),\
                    collocations=True, \
                    save_path="img/wc_qcf", color_func=simple_color_func)


#Wordclouds de cada tag separadamente:
for el in df2.tag.unique():
    path = "img/wc_" + el.lower()
    plot_wcs_from_freqs(words_per_range, get_list_items(df2, [el]),\
                    collocations=True, save_path= path,\
                    color_func=simple_color_func)

#Wordclouds de termos marcados com tags incluindo bigramas:
plot_wcs_from_freqs(terms_per_range, list(df2["item"]),\
                    collocations=True, save_path="img/wc_tagged_sw", \
                    color_func=simple_color_func)

#Wordclouds de recursos (`amens_per_range`) excluindo palavras muito comuns
#em todas as faixas:
plot_wcs_from_freqs(amens_per_range, collocations=True,\
                    stopwords=['interfone', 'elevador', 'jardim', 'cozinha'],\
                    save_path = "img/amens_",
                    color_func=simple_color_func)
