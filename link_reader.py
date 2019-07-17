import json
print("OK")

#Transformando JSON em lista de links legível para o script do spider `vivareal_spider`:
link_list = list()
links_wrapper = open("links.jl", "r")
links = links_wrapper.read()
links_wrapper.close()
data = [json.loads(str(item)) for item in links.strip().split('\n')]
for item in data:
    for link in item["Links"]:
        link_list.append(link)
with open('vivareal/spiders/links_readable.txt', 'w') as f:
    for item in link_list:
        f.write(item+",")



test = open('vivareal/spiders/links_readable.txt', 'r')
test = test.read()
test = test.split(",")
print("Teste: \n")
print(test[0:40])
print(len(test))
        
        