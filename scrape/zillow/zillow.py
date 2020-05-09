import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import urllib


class ZillowSpider(scrapy.Spider):
    # spider name
    name = 'zillow'

    # base URL
    # html url: https://www.zillow.com/denver-co/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A2%7D%2C%22usersSearchTerm%22%3A%22Denver%2C%20CO%22%2C%22mapBounds%22%3A%7B%22west%22%3A-105.27808513281248%2C%22east%22%3A-104.43213786718748%2C%22south%22%3A39.497442204124155%2C%22north%22%3A40.03053035952518%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A11093%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%2C%22isMapVisible%22%3Afalse%7D
    # json url: https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A2%7D%2C%22usersSearchTerm%22%3A%22Denver%2C%20CO%22%2C%22mapBounds%22%3A%7B%22west%22%3A-105.27808513281248%2C%22east%22%3A-104.43213786718748%2C%22south%22%3A39.497442204124155%2C%22north%22%3A40.03053035952518%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A11093%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%2C%22isMapVisible%22%3Afalse%7D&includeMap=false&includeList=true
    # json unquote: https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState={"pagination":{"currentPage":2},"usersSearchTerm":"Denver, CO","mapBounds":{"west":-105.27808513281248,"east":-104.43213786718748,"south":39.497442204124155,"north":40.03053035952518},"regionSelection":[{"regionId":11093,"regionType":6}],"filterState":{"sort":{"value":"globalrelevanceex"}},"isListVisible":true,"isMapVisible":false}&includeMap=false&includeList=true
    base_json_url = 'https://www.zillow.com/search/GetSearchPageState.htm?'

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # custom settings
    custom_settings = {
        # settings to slow down the spider
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 5,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    }

    # json_url decode: urllib.parse.unquote(base_url)
    params = {
        'searchQueryState': '{"pagination":{"currentPage":2},"usersSearchTerm":"Denver, CO","mapBounds":{"west":-105.27808513281248,"east":-104.43213786718748,"south":39.497442204124155,"north":40.03053035952518},"regionSelection":[{"regionId":11093,"regionType":6}],"filterState":{"sort":{"value":"globalrelevanceex"}},"isListVisible":true,"isMapVisible":false}'
    }

    # crawler's entry point
    def start_requests(self):
        # loop over page range ( change "10" to whatever number of pages to crawl)
        for page in range(1, 10):
            # parse params
            parsed_params = json.loads(self.params['searchQueryState'])

            # init next page
            parsed_params['pagination']['currentPage'] = str(page)

            # update string query parameters
            self.params['searchQueryState'] = json.dumps(parsed_params).replace(' ', '')

            # init next page URL
            next_page = self.base_json_url + urllib.parse.urlencode(self.params) + '&includeMap=false&includeList=true'
            print(next_page)

            # crawl next page URL
            yield scrapy.Request(url=next_page, headers=self.headers, callback=self.parse)
            # break

    def parse(self, response):
        jsonresponse = json.loads(response.body)

        # # store output to JSON file
        # json_object = json.dumps(jsonresponse, indent=4)
        # with open("response.json", "w") as f:
        #     f.write(json_object)

        # # testing to get data from json file
        # with open('response.json') as json_file:
        #     data = json.load(json_file)
        #     for p in jsonresponse['searchResults']['listResults']:
        #         print('statusText: ' + p['statusText'])
        #         print('price: ' + p['price'])
        #         print('address: ' + p['address'])
        #         print('description: ' + p['description'])
        #         print('')

        for item in jsonresponse['searchResults']['listResults']:
            # nestedDict.get('key1', '').get('key2').get('key3')
            detailUrl = item.get('detailUrl', '')
            statusText = item.get('statusText', '')
            price = item.get('price', '')
            address = item.get('address', '')
            addressStreet = item.get('addressStreet', '')
            addressState = item.get('addressState', '')
            addressCity = item.get('addressCity', '')
            addressZipcode = item.get('addressZipcode', '')
            description = item.get('description', '')
            beds = item.get('beds', '')
            baths = item.get('baths', '')
            area = item.get('area', '')
            latitude = item.get('latLong', '').get('latitude')
            longitude = item.get('latLong', '').get('longitude')
            brokerName = item.get('brokerName', '')
            brokerPhone = item.get('brokerPhone', '')
            yearBuilt = item.get('hdpData').get('homeInfo').get('yearBuilt')
            lotSize = item.get('hdpData').get('homeInfo').get('lotSize')
            homeType = item.get('hdpData').get('homeInfo').get('homeType')
            homeStatus = item.get('hdpData').get('homeInfo').get('homeStatus')
            zestimate = item.get('hdpData').get('homeInfo').get('zestimate')
            rentZestimate = item.get('hdpData').get('homeInfo').get('rentZestimate')
            festimate = item.get('hdpData').get('homeInfo').get('festimate')
            hiResImageLink = item.get('hdpData').get('homeInfo').get('hiResImageLink')

            yield {'detailUrl': detailUrl,
                   'statusText': statusText,
                   'price': price,
                   'address': address,
                   'addressStreet': addressStreet,
                   'addressState': addressState,
                   'addressCity': addressCity,
                   'addressZipcode': addressZipcode,
                   'description': description,
                   'beds': beds,
                   'baths': baths,
                   'area': area,
                   'latitude': latitude,
                   'longitude': longitude,
                   'brokerName': brokerName,
                   'brokerPhone': brokerPhone,
                   'yearBuilt': yearBuilt,
                   'lotSize': lotSize,
                   'homeType': homeType,
                   'homeStatus': homeStatus,
                   'zestimate': zestimate,
                   'rentZestimate': rentZestimate,
                   'festimate': festimate,
                   'hiResImageLink': hiResImageLink, }

            # yield {'detailUrl': item['detailUrl'],
            #        'statusText': item['statusText'],
            #        'price': item['price'],
            #        'address': item['address'],
            #        'addressStreet': item['addressStreet'],
            #        'addressState': item['addressState'],
            #        'addressCity': item['addressCity'],
            #        'addressZipcode': item['addressZipcode'],
            #        # 'description': item['description'],
            #        'beds': item['beds'],
            #        'baths': item['baths'],
            #        'area': item['area'],
            #        'latitude': item['latLong']['latitude'],
            #        'longitude': item['latLong']['longitude'],
            #        # 'brokerName': item['brokerName'],
            #        # 'brokerPhone': item['brokerPhone'],
            #        'yearBuilt': item['hdpData']['homeInfo']['yearBuilt'],
            #        'lotSize': item['hdpData']['homeInfo']['lotSize'],
            #        'homeType': item['hdpData']['homeInfo']['homeType'],
            #        'homeStatus': item['hdpData']['homeInfo']['homeStatus'],
            #        'zestimate': item['hdpData']['homeInfo']['zestimate'],
            #        # 'rentZestimate': item['hdpData']['homeInfo']['rentZestimate'],
            #        'festimate': item['hdpData']['homeInfo']['festimate'],
            #        'hiResImageLink': item['hdpData']['homeInfo']['hiResImageLink'], }

# main driver
if __name__ == '__main__':
    # run spider
    process = CrawlerProcess()
    process.crawl(ZillowSpider)
    process.start()

    # debug data extraction logic
    # ZillowSpider.parse(ZillowSpider, '')
