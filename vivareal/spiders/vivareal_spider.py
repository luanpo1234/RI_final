import scrapy
import re

path = "links_readable.txt"

#Lista de links obtida no spider `links_spider` e trabalhada em `links_reader`
links_wrapper = open(path, "r")
link_list = links_wrapper.read()
link_list = link_list.split(",")

#Testando se o número de links está correto:
print(len(link_list))

class VivarealSpider(scrapy.Spider):
    name = "vivareal_spider"
    allowed_domains = ["vivareal.com.br"]
    #Percorrer links coletados para todos os anúncios de BH:
    start_urls = ["https://www.vivareal.com.br/" + path for path in link_list]
    
    
    def parse(self, response):
        print("Processing: " + response.url)
        description = response.xpath("//p[@class='description__text']/text()").extract()
        price = response.xpath("//h3[contains(@class, 'price__price-info')]/text()").extract()
        condo = response.xpath("//span[contains(@class, 'js-condominium')]/text()").extract()
        iptu = response.xpath("//span[contains(@class, 'js-iptu')]/text()").extract()
        area = response.xpath("//div[@class='js-features']//li[contains(@class, 'js-area')]").extract()
        bedrooms = response.xpath("//div[@class='js-features']//li[contains(@class, 'js-bedrooms')]").extract()
        bathrooms = response.xpath("//div[@class='js-features']//li[contains(@class, 'js-bathrooms')]").extract()
        parking = response.xpath("//div[@class='js-features']//li[contains(@class, 'js-parking')]").extract()
        amenities = response.xpath("//div[contains(@class, 'js-amenities-modal')]//ul[contains(@class, 'amenities__list')]").extract()
        address = response.xpath("//p[contains(@class, 'map__address')]/text()").extract()
        print("teste",  description, "preco", price, "condo", condo, "iptu", iptu, "area", area, "bedrooms",\
              bedrooms, "bathrooms", bathrooms, "vagas", parking, "amenities", amenities, "endereco", address)
        results = {"desc": description, "price": price, "condo": condo, "iptu": iptu, "area": area, "bedrooms": bedrooms,\
                   "bathrooms": bathrooms, "parking": parking, "amenities": amenities, "address": address}
        yield results
        
def remove_tags(text):
    re.sub(r'[^ \w\.]', '', text)
    return text