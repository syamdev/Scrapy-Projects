import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import json


class WillandbearSpider(CrawlSpider):
    # spider name
    name = 'Willandbear'
    allowed_domains = ['willandbear.com']

    # Start URL
    start_urls = ['https://willandbear.com/collections/all/']

    # custom headers
    # headers = {
    #     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    # }

    # custom settings
    custom_settings = {
        # uncomment below settings to slow down the scraper
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1,
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv',
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'DEPTH_LIMIT': 1,
    }

    # Rules
    rules = (
        # link should match this pattern and create new requests
        Rule(
            LxmlLinkExtractor(
                allow='https://willandbear.com/collections/all/products/',
                unique=True),
            callback='parse_product_page',
            follow=True
        ),
    )

    def parse_product_page(self, response):
        self.logger.info('Hi, this is an product page! %s', response.url)
        gallery = response.xpath('//*[@class="gallery-cell"]')
        images = gallery.xpath('.//*[@class="image__container"]/img/@data-src').getall()
        image_list = []
        for image in images:
            img = image.split('?')
            image_url = 'https:' + img[0]
            image_list.append(image_url)

        yield {
            'product_url': response.url,
            'image_list': image_list,
        }


# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(WillandbearSpider)
    process.start()
