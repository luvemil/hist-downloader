import scrapy
from get_forex_data.items import ForexHistoryItem

class ForexSpider(scrapy.Spider):
    """docstring for ForexCrawler"""
    name = "forexhistory"
    allowed_domains = ["http://www.histdata.com"]

    def parse_currency_page(self,response):
        req = scrapy.FormRequest.from_response(response, formname="file_down",
                                               dont_click=True)
        req.headers['Referer'] = response.url
        req.meta['item'] = response.meta['item']
        yield req
