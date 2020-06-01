import scrapy
from scrapy.crawler import CrawlerProcess
from nameparser import HumanName


class SecureAcceSpider(scrapy.Spider):
    # spider name
    name = 'secure_acce'

    # start URL
    start_url = 'https://secure.acce.org/index.php?src=directory&view=sponsors&submenu=BusinessDirectory&srctype=biz_directory_lister&pos=0,121,121'

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # custom settings
    custom_settings = {
        # uncomment below settings to slow down the scraper
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 2,
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv'
    }

    # crawler's entry point
    def start_requests(self):
        # crawl next page URL
        yield scrapy.Request(url=self.start_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        box = response.xpath('//*[@class="item clearSpace"]')
        for data in box:
            fullname = data.xpath('.//*[@class="sponsorInfo"]/div[2]/text()')
            if not fullname:
                firstname = 'N/A'
                lastname = 'N/A'
            else:
                name = HumanName(fullname.get())
                firstname = name.first
                lastname = name.last

            company = data.xpath('.//*[@class="sponsorInfo"]/*[@class="sponsorName"]/text()')
            if not company:
                company = 'N/A'
            else:
                company = data.xpath('.//*[@class="sponsorInfo"]/*[@class="sponsorName"]/text()').get()

            email_1 = data.xpath('.//*[@class="sponsorInfo"]/div//*/text()')
            if not email_1:
                email = 'N/A'
            else:
                email = email_1.get().replace("document.write( '", "").replace("' );", "").replace("' + '", "")

            phone = data.xpath('.//*[@class="sponsorInfo"]/div[3]/text()')
            if not phone:
                phone = 'N/A'
            else:
                phone = data.xpath('.//*[@class="sponsorInfo"]/div[3]/text()').get()

            rel_url = data.xpath('.//*[@class="sponsorInfo"]/p/a/@href').get()
            page_url = response.urljoin(rel_url)

            yield scrapy.Request(page_url,
                                 headers=self.headers,
                                 callback=self.parse_data,
                                 meta={'firstname': firstname,
                                       'lastname': lastname,
                                       'company': company,
                                       'email': email,
                                       'phone': phone})

    def parse_data(self, response):
        website = response.xpath('//a[contains(@href,"javascript:EncodeClick")]/text()')
        if not website:
            website = 'N/A'
        else:
            website = response.xpath('//a[contains(@href,"javascript:EncodeClick")]/text()').get()

        yield {
            'firstname': response.meta['firstname'],
            'lastname': response.meta['lastname'],
            'company': response.meta['company'],
            'email': response.meta['email'],
            'phone': response.meta['phone'],
            'website': website
        }


# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(SecureAcceSpider)
    process.start()
