import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import json


class IdsoSpider(CrawlSpider):
    # spider name
    name = 'idso'
    allowed_domains = ['idsecurityonline.com']

    # Start URL
    start_urls = ['https://www.idsecurityonline.com/site_map/']

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
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'

    }

    # Rules
    rules = (
        # Extract link from this path only
        Rule(
            LxmlLinkExtractor(
                # allow_domains=['idsecurityonline.com'],
                allow='https://www.idsecurityonline.com/fargo/',
                deny='search_results',
                unique=True),
            follow=True
        ),
        # link should match this pattern and create new requests
        Rule(
            LxmlLinkExtractor(
                allow='https://www.idsecurityonline.com/[\w-]+\.htm$',
                unique=True),
            callback='parse_product_page',
            follow=True
        ),
    )

    # # crawler's entry point
    # def start_requests(self):
    #     yield scrapy.Request(url=self.start_url callback=self.parse)

    # def parse(self, response):
    #     links = LxmlLinkExtractor(allow_domains=['idsecurityonline.com']).extract_links(response)
    #     for link in links:
    #         yield {'url': link}

    def parse_product_page(self, response):
        self.logger.info('Hi, this is an product page! %s', response.url)
        product_name = response.xpath('//h1/text()').get()
        img = response.xpath('//*[@class="pict_zoom"]/*/@href').get()
        img_url = response.urljoin(img)
        retail_price = response.xpath('//*[@class="retail_price2show js_msrp_container"]/text()').get()
        sale_price1 = response.xpath('//*[@class="sale_price2show js_price_container"]/text()')
        if not sale_price1:
            sale_price = 'N/A'
        else:
            sale_price = response.xpath('//*[@class="sale_price2show js_price_container"]/text()').get()
        json_string = response.xpath('//script[contains(text(), "ecomm_prodid")]/text()').get().replace('\r\n',
                                                                                                        '').replace(
            '];', '').replace('dataLayer = [', '').replace("'", '"').strip()
        json_product = json.loads(json_string)
        category = response.xpath('//*[@class="breadcrumb"]/li[2]//*/text()').get()
        # product_type = response.xpath('//*[@class="breadcrumb"]/li[position()>=last()-1]//*/text()').get()
        product_type = json_product['ecomm_prodcategory']
        sku = response.xpath('//*[@class="js_sku"]/text()').get()
        item_number = json_product['ecomm_prodid']
        manufacture = json_product['ecomm_brand']
        desc_list = response.xpath('//*[@class="col-12 col-md"]/descendant::text()').getall()
        desc = '\n'.join(line.rstrip("\r\n") for line in desc_list).strip()
        description = desc.replace('\n\r\n', '')

        yield {
            'product_name': product_name,
            'img_url': img_url,
            'retail_price': retail_price,
            'sale_price': sale_price,
            'category': category,
            'product_type': product_type,
            'sku': sku,
            'item_number': item_number,
            'manufacture': manufacture,
            'description': description
        }


# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(IdsoSpider)
    process.start()
