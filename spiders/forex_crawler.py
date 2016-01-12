import scrapy
from get_forex_data.items import ForexHistoryItem
import re

class ForexSpider(scrapy.Spider):
    """docstring for ForexCrawler"""
    name = "forexhistory"
    allowed_domains = ["www.histdata.com"]

    start_urls = ["http://www.histdata.com/download-free-forex-data/?/ascii/1-minute-bar-quotes"]

    def parse(self, response):
        cur_pair_nodes = response.css("div.page-content").css("td")
        for cur_pair in cur_pair_nodes:
            url = response.urljoin(cur_pair.xpath("a/@href").extract()[0])
            req = scrapy.Request(url, callback=self.select_year)
            name = cur_pair.xpath("a//text()").extract()[0]
            name = name.replace("/", "")
            item = ForexHistoryItem()
            item['name'] = name
            item['year'] = "2016"
            req.meta['item'] = item
            yield req
        if len(cur_pair_nodes) == 0:
            yield None

    def select_year(self, response):
        year_regex = re.compile("(?:^|\D)2016(?:\s|$)")
        year_nodes = response.css("div.page-content").xpath(".//a")
        for year in year_nodes:
            # year is a <a> node
            m = year_regex.match(year.xpath(".//text()").extract()[0])
            if m:
                url = response.urljoin(year.xpath("@href").extract()[0])
                req = scrapy.Request(url, callback=self.parse_currency_page)
                if response.meta['item']:
                    req.meta['item'] = response.meta['item']
                yield req


    def parse_currency_page(self,response):
        req = scrapy.FormRequest.from_response(
            response,
            formname="file_down",
            dont_click=True,
            callback=self.save_values
        )
        req.headers['Referer'] = response.url
        req.meta['item'] = response.meta['item']
        yield req

    def save_values(self, response):
        item = response.meta['item']
        with open("data/values/%s.zip" % item['name'], "wb") as f:
            f.write(response.body)
        yield item
