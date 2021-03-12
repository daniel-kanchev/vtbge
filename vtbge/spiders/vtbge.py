import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from vtbge.items import Article


class VtbgeSpider(scrapy.Spider):
    name = 'vtbge'
    start_urls = ['https://vtb.ge/ge/about-the-bank/news']

    def parse(self, response):
        links = response.xpath('//a[@class="item item-news"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="box box-ml box-blue caps m-l-15  "]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()[2]').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="inner-news-meta-date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="inner-text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
