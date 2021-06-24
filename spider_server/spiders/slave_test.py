import datetime
from scrapy import cmdline, Request

from scrapy_redis.spiders import RedisSpider
import json


class SlaveTestSpider(RedisSpider):
    """
    scrapy-redis  从机测试程序
    """
    name = 'slave_test'
    redis_key = "master_test:start_urls"
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.RabbitMQPipeline': 300}
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make_requests_from_url(self, url):
        """
        Spider.make_requests_from_url method is deprecated:
        it will be removed and not be called by the default
        Spider.start_requests method in future Scrapy releases.
        Please override Spider.start_requests method instead.
        """
        try:
            data = json.loads(url) # 从redis中取出是string类型，需转回dict对象
            url = data.get('url') # 取出url
        except Exception as e:
            self.logger.error('redis队列中取出的数据异常，请检查')
            raise e
        return Request(url, dont_filter=True,meta={"data":data}) # 将对象传入meta.data中

    def parse(self, response):
        print(response.url)
        print(response.meta.get('data')) # 取出meta中的data对象
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        item={}
        item['url'] = response.url
        yield item




if __name__ == '__main__':
    cmdline.execute("scrapy crawl slave_test".split())
