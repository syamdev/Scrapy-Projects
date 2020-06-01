# ################################# #
# Using CrawlSpider & LinkExtractor #
# ################################# #
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import json


class QuotesSpider(CrawlSpider):
    name = "quotes"
    allowed_domains = ['quotes.toscrape.com']
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
        # 'FEED_FORMAT': 'csv',
        # 'FEED_URI': 'output.csv',
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

    }

    # Rules
    rules = (
        # Extract link from this path only
        Rule(
            LxmlLinkExtractor(
                # allow_domains=['quotes.toscrape.com'],
                allow='http://quotes.toscrape.com/page/',
                deny='http://quotes.toscrape.com/tag/',
                unique=True),
            follow=True
        ),
        # link should match this pattern and create new requests
        Rule(
            LxmlLinkExtractor(
                allow='http://quotes.toscrape.com/author/',
                unique=True),
            callback='parse_author_page',
            follow=True
        ),
    )

    def parse_author_page(self, response):
        yield {
            'author': response.xpath('//h3/text()').get().strip(),
        }


# run spider
process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start()
