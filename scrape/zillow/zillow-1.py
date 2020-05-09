# source: https://github.com/maksimKorzh/scrapy-tutorials/blob/master/src/zillow/zillow.py
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import urllib
import json


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    base_url = 'https://www.zillow.com/co/2_p/?'

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    }

    # url decode: urllib.parse.unquote(base_url)
    params = {
        'searchQueryState': '{"pagination":{"currentPage":2},"usersSearchTerm":"colorado","mapBounds":{"west":-112.318144125,"east":-98.782987875,"south":34.586573217246666,"north":43.203914800444515},"regionSelection":[{"regionId":10,"regionType":2}],"isMapVisible":true,"mapZoom":6,"filterState":{"sort":{"value":"globalrelevanceex"}},"isListVisible":true}'
    }

    def start_requests(self):
        for page in range(1, 8):
            parsed_params = json.loads(self.params['searchQueryState'])

            # init next page
            parsed_params['pagination']['currentPage'] = str(page)

            # update string query parameters
            self.params['searchQueryState'] = json.dumps(parsed_params).replace(' ', '')

            # init next page URL
            next_page = self.base_url + urllib.parse.urlencode(self.params)

            # crawl next page URL
            yield scrapy.Request(url=next_page, headers=self.headers, callback=self.parse_links)

    def parse_links(self, res):
        # extract card links
        card_links = res.css('ul[class="photo-cards photo-cards_wow photo-cards_short"]')
        card_links = card_links.css('li')
        card_links = card_links.css('a.list-card-link::attr(href)')

        for card in card_links:
            # crawl property listing
            yield res.follow(url=card.get(), headers=self.headers, callback=self.parse_listing)
            break

    def parse_listing(self, res):
        # store listing HTML to local
        '''
        with open('res.html', 'w') as f:
            f.write(res.text)
        return
        '''

        # local listing HTML content
        # content = ''

        # load local listing HTML file to extract data from it
        # with open('res.html', 'r') as f:
        #     for line in f.read():
        #         content += line

        # init scrapy selector
        res = Selector(text=content)
        # print(res)

        # extract feature list
        features = {
            'price': ''.join(res.css('div[class="ds-chip"]')
                                .css('h3[class="ds-price"] *::text')
                                .getall()),

            'address': ''.join(res.css('div[class="ds-chip"]')
                                  .css('h1[class="ds-address-container"] *::text')
                                  .getall()),

            'bedrooms': ' '.join(res.css('div[class="ds-chip"]')
                                    .css('span[class="ds-bed-bath-living-area"] *::text')
                                    .getall())
                                    .replace('  ', '|')
                                    .replace('| ', ':')
                                    .split()[0]
                                    .replace(':bd', ''),

            'bathrooms': ' '.join(res.css('div[class="ds-chip"]')
                                     .css('span[class="ds-bed-bath-living-area"] *::text')
                                     .getall())
                                     .replace('  ', '|')
                                     .replace('| ', ':')
                                     .split()[1]
                                     .replace(':ba', ''),

            'floor_area': ' '.join(res.css('div[class="ds-chip"]')
                                      .css('span[class="ds-bed-bath-living-area"] *::text')
                                      .getall())
                                      .replace('  ', '|')
                                      .replace('| ', ':')
                                      .split()[2]
                                      .replace(':', ' '),

            'zestimate': ''.join(res.css('div[class="ds-chip"]')
                                    .css('div[class="ds-chip-removable-content"] *::text')
                                    .getall())
                                    .split('\u00ae:')[-1],

            'description': '\n'.join(res.css('div[class="ds-overview-section"] *::text')
                              .getall()).replace('\nRead more', ''),

            'agent_info': {

                'agent_name': res.css('ul[class="cf-listing-agent-info"] *::text')
                    .getall()[0],

                'agent_phone': res.css('ul[class="cf-listing-agent-info"] *::text')
                    .getall()[1]
            },

            'facts_and_features': {},

            'tax_history': {},

            'monthly_cost': {},

            'nearby_schools': [
                ' '.join(Selector(text=school).css(' *::text').getall()) for school in
                res.css('ul[class="ds-nearby-schools-list"]')
                    .css('li[class="sc-cMhqgX ikQQNx"]')
                    .getall()
            ],

            'coordinates': {
                'latitude': '',
                'longitude': ''
            }

        }

        # try to extract facts and features
        try:
            facts = res.css('ul[class="ds-home-fact-list"]')
            facts = '|'.join(facts.css('li *::text').getall()).replace(':|', ':').split('|')

            # loop over facts
            for fact in facts:
                features['facts_and_features'][fact.split(':')[0]] = fact.split(':')[1]
        except:
            pass

        # try to extract tax history
        try:
            tax_history = ''.join([' '.join(Selector(text=ul).css('li *::text').getall()) for ul in
                                   res.css('ul[class="sc-dqBHgY kQzYMy"]').getall() if 'Tax assessed value:' in ul])

            # store tax history
            features['tax_history'] = {
                'Tax assessed value': tax_history.split('Tax assessed value:')[1].split()[0],
                'Annual tax amount': tax_history.split('Annual tax amount:')[1].split()[0]
            }

        except:
            pass

        # try to extract monthly cost
        try:
            monthly_cost = res.css('div[class="sc-1b8bq6y-6 kKSvPL"] *::text').getall()
            monthly_cost = '|'.join(monthly_cost).replace('|$', ':$').replace('Chevron Down', '')
            monthly_cost = [item.replace('|', ' ').strip().replace('Utilities ', 'Utilities:') for item in
                            monthly_cost.split('||')]

            # loop over monthly cost table
            for item in monthly_cost:
                features['monthly_cost'][item.split(':')[0]] = item.split(':')[1]
        except:
            pass

        # try to extract coordinates
        script = [script for script in res.css('script[type="application/ld+json"]').getall() if 'latitude' in script][
            0]
        script = Selector(text=script).css('::text').get()
        script = json.loads(script)

        # store coordinates
        features['coordinates']['latitude'] = script['geo']['latitude']
        features['coordinates']['longitude'] = script['geo']['longitude']

        # store output to JSON file
        with open('zillow.json', 'a') as f:
            f.write(json.dumps(features, indent=2) + '\n')

# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(ZillowSpider)
    process.start()

    # debug data extraction logic
    # ZillowSpider.parse_listing(ZillowSpider, '')