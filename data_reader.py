import re
import json

"""
Lê e preprocessa dados do JSON retirados do site (retira tags HTML, etc.).
Retorna outro JSON com os dados trabalhados para serem carregados em um DataFrame.
"""

#Carregando dados do JSON em lista de dicts `data`:
wrapper = open("vivareal.jl", "r")
x = wrapper.read()
wrapper.close()
data = [json.loads(str(item)) for item in x.strip().split('\n')]

#Métodos de processamento dos datapoints em formato bruto:
def get_li_text(list_):
    """
    """
    try:
        text = list_[0]
    except IndexError:
        return None
    res = re.findall("<li.*?>(.*?)<\/li>", text)
    return res

def get_digits(list_):
    if len(list_) < 1:
        return None
    try:
        text = list_[0]
    except IndexError:
        return None
    #Eliminando pontos para pegar valor numérico
    text = text.replace(".", "")
    print("get_digits")
    res = re.findall("\d+", text)
    try:
        return int(res[0])
    except IndexError:
        return None

def get_digits_from_span(list_):
    try:
        text = list_[0]
    except IndexError:
        return None
    res = re.findall("<span>(\d+)</span>", text)
    try:
        return int(res[0])
    except IndexError:
        return None

def get_neighborhood(list_):
    try:
        text = list_[0]
    except IndexError:
        return None
    print(text)
    res = re.findall("-\s(.*?)\,", text)
    if len(res) == 0:
        res = re.findall("(.*?)\,", text)
    #Para casos de erro
    if len(res) > 0:
        return res[0]
    else:
        return "ERRO" + text

def get_joined_list(list_):
    res = ""
    res += " ".join(list_)
    return res

#`dict` para atribuir método certo a cada key:
METHODS_DICT = {"bedrooms": get_digits_from_span, "bathrooms": get_digits_from_span, "area": get_digits_from_span, \
                "parking": get_digits_from_span, "price": get_digits, "condo": get_digits, "iptu": get_digits,
                "amenities": get_li_text, "desc": get_joined_list, "address": get_neighborhood}

d_final = {}
for key in data[0].keys():
    index = 0
    for item in data:
        try:
            d_final[key].append(METHODS_DICT[key](item[key]))
        except KeyError:
            d_final[key] = [METHODS_DICT[key](item[key])]
        print(index, item[key], key)
        index += 1
    print(d_final)
        
with open("d_final.json", "w") as json_file:  
    json.dump(d_final, json_file)