import scrapy
import datetime
from scrapy import Request, cmdline


class WeiboSearchV1Spider(scrapy.Spider):
    """
    微博 weibo.cn
    微博高级搜索页
    """
    name = 'weiboSearchV1'
    allowed_domains = ['weibo.cn', 'weibo.com']
    base_url = "https://weibo.cn"
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.UrlRedisPipeline': 300},
        'DOWNLOAD_DELAY': 5,
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},
    }
    redis_name = 'weiboDetail' # push到weiboDetail 队列

    def __init__(self, keyword='', start_time=None, end_time=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        self.headers = {
            'referer': 'https://weibo.cn/search/mblog?advanced=mblog&f=s',
            'content-type': 'application/x-www-form-urlencoded',
            'Accept': '*/*'
        }

        # 搜索的起始日期，自行修改   微博的创建日期是2009-08-16 也就是说不要采用这个日期更前面的日期了
        if start_time:
            self.date_start = datetime.datetime.strptime(start_time, '%Y%m%d').strftime("%Y%m%d")
        else:
            self.date_start = ''

        # 搜索的结束日期 TODO 结束时间应该小于开始时间
        if end_time is None:
            self.date_end = datetime.datetime.now().strftime("%Y%m%d")
        else:
            self.date_end = datetime.datetime.strptime(end_time, '%Y%m%d').strftime("%Y%m%d")

        self.url_format = "https://weibo.cn/search/mblog?advancedfilter=1&keyword={}&starttime={}&endtime={}&sort=time"

    def start_requests(self):  # 发送请求之前的回调函数
        self.url = self.url_format.format(self.keyword, self.date_start, self.date_end)
        yield Request(self.url, callback=self.parse_tweet, dont_filter=True, headers=self.headers)

    def parse_tweet(self, response):  # 解析微博
        """
        解析本页的数据
        """
        tweet_nodes = response.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:

                # 评论url
                url = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/@href').get()
                yield {'url': url}

            except Exception as e:
                self.logger.error(e)

        # 翻页
        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield Request(url, callback=self.parse_tweet, dont_filter=True)


if __name__ == '__main__':
    cmdline.execute("scrapy crawl weiboSearchV1 -a keyword=火星".split())
