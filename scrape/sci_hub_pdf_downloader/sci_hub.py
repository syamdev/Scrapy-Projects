import scrapy
from scrapy.crawler import CrawlerProcess
import os
from scrapy.selector import Selector
import json


class ScihubSpider(scrapy.Spider):
    # spider name
    name = 'sci_hub'

    # base URL
    start_url = 'https://sci-hub.tw/10.1017/S0272263110000124'

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # custom settings
    custom_settings = {
        # uncomment below settings to slow down the scraper
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        # 'DOWNLOAD_DELAY': 1,
        # 'FEED_FORMAT': 'csv',
        # 'FEED_URI': 'output.csv'
    }

    # crawler's entry point
    def start_requests(self):
        # crawl start page
        yield scrapy.Request(url=self.start_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        title = response.xpath('//title/text()').get().split(' | ')[1]
        pdf_click = response.xpath('//a[contains(@onclick, "location.href")]/@onclick').get()
        pdf_link = pdf_click.replace("location.href='", "").replace("?download=true'", "")

        yield scrapy.Request(
            url=response.urljoin(pdf_link),
            meta={'title': title},
            callback=self.save_pdf
        )

    def save_pdf(self, response):
        title = response.meta['title']
        """ Save pdf files """
        pdf_path = response.url.split('/')[-1]
        self.logger.info('Saving PDF %s', pdf_path)
        with open(pdf_path, 'wb') as file:
            file.write(response.body)

        os.rename(pdf_path, title + '.pdf')
        self.logger.info('Renaming PDF %s', title + '.pdf')

# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(ScihubSpider)
    process.start()
