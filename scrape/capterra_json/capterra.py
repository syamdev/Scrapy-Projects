import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json


class TemplateSpider(scrapy.Spider):
    # spider name
    name = 'spider_name'

    # base URL
    start_url = 'https://www.capterra.com/directoryPage/rest/v1/category?htmlName=ab-testing-software'

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # custom settings
    custom_settings = {
        # uncomment below settings to slow down the scraper
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1,
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv'
    }

    # crawler's entry point
    def start_requests(self):
        # crawl page URL
        yield scrapy.Request(url=self.start_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        jsonresponse = json.loads(response.body)
        category = jsonresponse['pageData']['categoryData']['longName']
        products = jsonresponse['pageData']['categoryData']['products']

        for item in products:
            name = item['product_name']
            reviews = item['total_reviews']
            rating = item['rating']
            url = item['product_url']

            yield {
                'Category': category,
                'Name': name,
                'Reviews': reviews,
                'How_many_Stars': rating,
                'URL': url,
            }


# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(TemplateSpider)
    process.start()
