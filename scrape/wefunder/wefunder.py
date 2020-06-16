import scrapy
from scrapy.crawler import CrawlerProcess
from nameparser import HumanName


class WefunderSpider(scrapy.Spider):
    # spider name
    name = 'wefunder'
    allowed_domains = ['wefunder.com']

    # base URL
    # start_url = 'https://wefunder.com/worldtree/investors'
    # start_urls = ['http://www.xxxxxxxxx.com/']

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # custom settings
    custom_settings = {
        # uncomment below settings to slow down the scraper
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1,
        # 'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv'
    }

    # crawler's entry point
    def start_requests(self):
        # import url per line from txt file
        with open('company_url_list.txt') as f:
            for line in f:
                if not line.strip():
                    continue
                # start crawl URL
                yield scrapy.Request(url=line, headers=self.headers, callback=self.parse)

    def parse(self, response):
        investors = response.xpath('//*[@data-type="investor"]')

        for investor in investors:
            fullname = investor.xpath('.//*[@class="name"]/text()').get()
            name = HumanName(fullname)
            firstname = name.first
            lastname = name.last

            rel_url = investor.xpath('.//*[@class="name"]/@href').get()
            profile_url = response.urljoin(rel_url)
            bio_desc = investor.xpath('.//*[@class="bio"]/text()').get(default='N/A').strip()

            yield scrapy.Request(profile_url,
                                 headers=self.headers,
                                 callback=self.parse_data,
                                 meta={'firstname': firstname,
                                       'lastname': lastname,
                                       'bio_desc': bio_desc,
                                       'profile_url': profile_url})

    def parse_data(self, response):
        profile_bio_desc = response.xpath('//*[@class="bio"]/text()').get(default='N/A').strip()
        website_url = response.xpath('//*[@class="my-link"]/a/@href').get(default='N/A')

        # networks = response.xpath('//*[@class="networks"]/a/@href').getall()
        # twitter = response.xpath('//*[@class="networks"]/a[contains(@href, "twitter")]/@href').get(default='N/A')
        facebook = response.xpath('//*[@class="networks"]/a[contains(@href, "facebook")]/@href').get(default='N/A')
        linkedin = response.xpath('//*[@class="networks"]/a[contains(@href, "linkedin")]/@href').get(default='N/A')
        location = ''.join(response.xpath('//*[@class="location"]/text()').getall()).strip()
        number_investments = response.xpath('//h3[contains(text(), "Investment")]/text()').get(default='N/A').split()[0]

        company_path = response.xpath('//*[@class="portfolio"]/a/*[@class="company"]/text()')
        if company_path:
            company_get = response.xpath('//*[@class="portfolio"]/a/*[@class="company"]/text()').getall()
            company_join = '[]'.join(item.strip() for item in company_get).strip()
            company_list = company_join.replace('[][]', ', ').replace('[]', '')
        else:
            company_list = 'N/A'

        content = response.xpath('//*[@class="contain-width"]')
        check_invest_in = response.xpath('//h3[contains(text(), "I want to invest in")]')
        check_good_at = response.xpath('//h3[contains(text(), "I am good at")]')
        check_interested_in = response.xpath('//h3[contains(text(), "Interested in")]')
        check_using_Wefunder = response.xpath('//h3[contains(text(), "I am using Wefunder for")]')

        if check_invest_in:
            invest_in_text = content.xpath('.//div[preceding-sibling::h3[1][contains(., "I want to invest in")]]/text()').getall()
            invest_in = ','.join(invest_in_text).strip()
        else:
            invest_in = 'N/A'

        if check_good_at:
            good_at_text = content.xpath('.//div[preceding-sibling::h3[1][contains(., "I am good at")]]/text()').getall()
            good_at = ', '.join(good_at_text).strip()
        else:
            good_at = 'N/A'

        if check_interested_in:
            interested_in_text = content.xpath('.//div[preceding-sibling::h3[1][contains(., "Interested in")]]/text()').getall()
            interested_in = ', '.join(interested_in_text).strip()
        else:
            interested_in = 'N/A'

        if check_using_Wefunder:
            using_Wefunder_text = content.xpath('.//div[preceding-sibling::h3[1][contains(., "I am using Wefunder for")]]/text()').getall()
            using_Wefunder = ', '.join(using_Wefunder_text).strip()
        else:
            using_Wefunder = 'N/A'

        yield {'firstname': response.meta['firstname'],
               'lastname': response.meta['lastname'],
               'bio_desc': response.meta['bio_desc'],
               'profile_bio_desc': profile_bio_desc,
               'website_url': website_url,
               'facebook': facebook,
               'linkedin': linkedin,
               'location': location,
               'invest_in': invest_in,
               'good_at': good_at,
               'interested_in': interested_in,
               'using_Wefunder': using_Wefunder,
               'number_investments': number_investments,
               'company_invested_in': company_list,
               'profile_url': response.meta['profile_url']
               }


# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(WefunderSpider)
    process.start()

    # scrapy shell -s USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36" "site.url"
