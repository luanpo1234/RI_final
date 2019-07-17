import scrapy

class VivarealSpider(scrapy.Spider):
    name = "links_spider"
    allowed_domains = ["vivareal.com.br"]
    start_urls = ["https://www.vivareal.com.br/venda/minas-gerais/belo-horizonte/apartamento_residencial/"]

    def parse(self, response):
        print("Processing: " + response.url)
        links = response.xpath("//h2//a/@href").extract()
        print("Links", links)
        yield {"Links": links}
        
        next_page = response.xpath("//div[@class='js-results-pagination']//li[@class='pagination__item']//a[contains(@title, 'Próxima') and contains(@class, 'js-change-page')]/@href").extract_first()
        page_num = next_page.split("=")[-1]
        next_link = "?pagina=" + page_num + "#onde=BR-Minas_Gerais-NULL-Belo_Horizonte&tipos=apartamento_residencial"
        if next_page is not None:
            next_page = response.urljoin(next_link)
            print("Próxima", next_page, page_num)
            yield scrapy.Request(next_page, callback=self.parse)