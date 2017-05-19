"""
usage:
    time scrapy runspider imicrobe_test/crawler.py > count_open_files_crawl_log.txt
"""

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class GoodLinkSpider(scrapy.Spider):
    name = "goodlink"

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 0.25
    }

    def start_requests(self):
        # this will be redirected to https://10.0.2.2:8443
        urls = [
            'http://10.0.2.2:8000/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #page = response.url.split("/")[-2]
        #filename = '-{}.html'.format(page)
        #with open(filename, 'wt') as f:
        #    f.write(response.body)
        #self.log('Followed URL {}'.format(response.url))
        if response.url.startswith('https://10.0.2.2'):
            for link in response.css('a::attr(href)').extract():
                if link is not None:
                    link_url = response.urljoin(link)
                    #self.log('found link url: {}'.format(link_url))
                    request = scrapy.Request(link_url, callback=self.parse)
                    if request.url.startswith('https://10.0.2.2'):
                        yield request

    def error(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)