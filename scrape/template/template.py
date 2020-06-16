import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json


class TemplateSpider(scrapy.Spider):
    # spider name
    name = 'spider_name'
    allowed_domains = ['xxxxxx.xxxxxx.com']


    # base URL
    start_url = 'https://www.xxxxxxxxx.com/'
    # start_urls = ['http://www.xxxxxxxxx.com/']

    # custom headers
    # headers = {
    #     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    # }

    # custom settings
    custom_settings = {
        # uncomment below settings to slow down the scraper
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        # 'DOWNLOAD_DELAY': 1,
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv'
    }

    # crawler's entry point
    def start_requests(self):
        # loop over page range ( change "10" to whatever number of pages to crawl)
        for page in range(1, 10):
            # parse params
            # init next page
            # update string query parameters
            # init next page URL
            # next_page = self.start_url + urllib.parse.urlencode(self.params)

            # crawl next page URL
            # yield scrapy.Request(url=next_page, headers=self.headers, callback=self.parse)

    def parse(self, response):
        pass

    def parse_data(self, response):
        '''
        # store response to local HTML file
        with open('res.html', 'w') as f:
            f.write(response.text)
        '''

        '''
        # local HTML content
        content = ''

        # read local HTML file
        with open('res.html', 'r') as f:
            for line in f.read():
                content += line

        # init scrapy selector
        response = Selector(text=content)
        '''

        # extract feature list
        extracted_data = {

        }

        # write output
        # yield {'url': url}

        # store output to JSON file
        # with open('output.json', 'a') as f:
        #     f.write(json.dumps(extracted_data, indent=2) + '\n')

# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(TemplateSpider)
    process.start()

    # debug data extraction logic
    # TemplateSpider.parse(TemplateSpider, '')
    # scrapy shell -s USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36" "site.url"