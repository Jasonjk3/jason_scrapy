
import scrapy
from scrapy import cmdline
import time

class MasterTestSpider(scrapy.Spider):
    """
    scrapy-redis  主机测试程序
    """
    name = 'master_test'
    allowed_domains = ['baidu.com']
    start_urls = ['https://www.baidu.com/']
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.ItemRedisPipeline': 300}
    }

    def __init__(self,keyword='', **kwargs):
        """
        初始化命令行参数
        :param keyword:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.keyword = keyword

    def parse(self, response):
        print('keyword = ',self.keyword)

        for i in range(1,20):
            item={}
            item['url'] = 'https://www.baidu.com/'
            item['category']='音乐'
            print(item)
            yield item
            time.sleep(10)


if __name__ == '__main__':
    cmdline.execute("scrapy crawl master_test -a keyword=百度".split())
