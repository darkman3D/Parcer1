import scrapy
from scrapy.http import Request


class NixSpider(scrapy.Spider):
    name = "nix"
    allowed_domains = ["nix.dn.ua"]
    start_urls = ["https://nix.dn.ua/"]

    def parse(self, response):
        # Парсинг категорий
        categories = response.css('ul.navbar-nav > li > a::attr(href)').getall()
        for category_url in categories:
            yield Request(url=response.urljoin(category_url), callback=self.parse_category)

    def parse_category(self, response):
        products = response.css('div.product-thumb')
        for product in products:
            # Извлечение данных о товаре внутри категории
            name = product.css('.product-thumb .caption > a::text').get()
            category = product.xpath('//*[@id="menu"]/div[2]/ul/li[1]/a/text()').get()
            price = product.css('.product-thumb .price::text').get()
            link = response.urljoin(product.css('.product-thumb .caption > a::attr(href)').get())
            
            if price is None:
                price = 'Нет цены'
            if name is None:
                name = 'Нет имени'
            if link is None:
                link = 'Нет ссылки'
            if category is None:
                category = 'Нет категории'

            yield {
                'name': name,
                'category': category,
                'price': price,
                'link': link
            }

        # Переход к следующей странице категории, если есть
        next_page = response.css('ul.pagination li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)

    def closed(self, reason):
        self.logger.info('Spider closed: %s', reason)
