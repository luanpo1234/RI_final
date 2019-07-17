# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 09:09:25 2019

@author: luanpo1234
"""
import pandas as pd
import matplotlib.pyplot as plt
import json

#Carregando dados do JSON em lista de dicts `data`:
wrapper = open("d_final.json", "r")
x = wrapper.read()
wrapper.close()
data = [json.loads(str(item)) for item in x.strip().split('\n')]
#Extraindo `dict`. `data` é uma `list` com o `dict` desejado como único item:
data = data[0]

df = pd.DataFrame(data)

#Removendo datapoints duplicados, subset exclui "amenities", que retorna erro:
print("Tamanho com duplicatas: ", df.shape[0])
df = df.drop_duplicates(subset=['address', 'area', 'bathrooms', 'bedrooms', \
                                'condo', 'desc', 'iptu', 'parking', 'price'])
print("Tamanho sem duplicatas: ", df.shape[0])

print("\nValores máximos antes do processamento: \n\n", df._get_numeric_data().max())
#Removendo espaços indesejados em nomes de bairros e características:
df["address"] = df["address"].str.strip()
df["amenities"].fillna("", inplace=True)
df['amenities'] = df['amenities'].map(lambda x: [el.strip().lower() for el in x])

#Substituindo valores de quarto, condomínio e IPTU absurdos por `None`. DPs não serão retirados
#pois ainda podem ser úteis:
df.loc[(df.bedrooms > 3000), "bedrooms"] = None
df.loc[(df.condo > 3000), "condo"] = None
df.loc[(df.iptu > 50000), "iptu"] = None

#Substituindo valores de bairro marcados como ERRO e iniciados por RUA
#por `None`:
df.loc[((df.address.str.contains("ERRO"))|(df.address.str.contains("Rua"))\
        |(df.address.str.contains("Avenida"))), "address"] = None
print("\nValores máximos após o processamento: \n\n", df._get_numeric_data().max())
media_por_bairro = [(el, df.loc[df.address==el].price.mean(), df.loc[df.address==el].\
                     price.count()) for el in df.address.unique() if el is not None]


#Muitos bairros têm poucas observações; abaixo somente aqueles com n>40, ordenados por preço:
mb = sorted([el for el in media_por_bairro if el[2] >= 30], key = lambda x: x[1])
if __name__== "__main__":
    bairros_baratos, bairros_caros = mb[0:5], mb[-5:][::]
    
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.bar([el[0] for el in bairros_baratos], [el[1]/1000 for el in bairros_baratos]\
            , label="5 bairros mais baratos")
    ax.bar([el[0] for el in bairros_caros], [el[1]/1000 for el in bairros_caros]\
            , label="5 bairros mais caros")
    ax.legend()
    plt.title("Bairros mais baratos e mais caros de Belo Horizonte")
    plt.xlabel("Bairro")
    plt.ylabel("Preço médio em milhares de R$")
    plt.savefig("img/bairros_valor.png")