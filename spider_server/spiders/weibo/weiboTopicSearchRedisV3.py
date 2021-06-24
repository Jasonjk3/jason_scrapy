import json

from scrapy import Request, cmdline
from scrapy_redis.spiders import RedisSpider

from spider_server.items import WeiboTopicItem
from spider_server.libs.util import url_encode
import datetime
class WeiboTopicSearchRedisV3(RedisSpider):
    """
    redis slave 爬虫
    微博 weibo.com V3
    微博话题搜索
    """
    name = 'weiboTopicSearchRedisV3'
    allowed_domains = ['weibo.cn', 'weibo.com']
    base_url = "https://weibo.com"
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.MyMongoDBPipeline': 300,
                           'spider_server.pipelines.KafkaMQPipeline': 255,
                           'spider_server.pipelines.ItemRedisPipeline': 250},
        'DOWNLOAD_DELAY': 5,
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},
    }
    redis_key = "weiboTopicSearchRedisV3:start_urls"
    redis_name = "weiboCommentsV2"
    headers = {
        'referer': 'https://weibo.com/u/7589466762/home?wvr=5',
        'Accept': '*/*'
    }

    def make_requests_from_url(self, item):
        """
            获取微博热门话题的标题，拼接成url
        """
        try:
            data = json.loads(item) # 从redis中取出是string类型，需转回dict对象
            title = data.get('title') # 取出url
            url = f'https://s.weibo.com/weibo?q={url_encode(title)}'
            self.logger.info(f"request url -> {url}")
        except Exception as e:
            self.logger.error('redis队列中取出的数据异常，请检查')
            raise e
        return Request(url, dont_filter=True,meta={"data":data},headers=self.headers) # 将对象传入meta.data中

    def parse(self, response):  # 解析微博
        """
        解析本页的数据
        """
        # print(response)
        # print(response.text)
        item=WeiboTopicItem()
        item['topic'] = response.xpath('//div[@class="info"]/div[@class="title"]/h1/a/text()').get()
        item['read_num'] = response.xpath('//div[@class="info"]/div[@class="total"]/span[1]/text()').get()
        item['discussion_num'] = response.xpath('//div[@class="info"]/div[@class="total"]/span[2]/text()').get()
        item['topic_lead'] = response.xpath('//div[@class="card card-topic-lead s-pg16"]/p/text()').get()
        item['tags'] = response.xpath('//div[@class="card-content s-pg16"]/dl//a[@class="tag"]/text()').getall()
        item['top_item_id'] = response.xpath('//div[@id="pl_feedlist_index"]//div[@class="card-wrap" and @action-type="feed_list_item"][1]/@mid').get()
        item['top_item_username'] = response.xpath('//div[@class="card-wrap" and @action-type="feed_list_item"][1]//div[@class="info"]/div[2]/a/text()').get()
        item['top_item_content'] = response.xpath('//div[@class="card-wrap" and @action-type="feed_list_item"][1]//p[@class="txt"]').xpath('string(.)').get()
        item['top_item_repost'] = response.xpath('''//div[@class="card-wrap" and @action-type="feed_list_item"][1]//a[contains(text(),'转发')]/text()''').get()
        item['top_item_comment'] = response.xpath('''//div[@class="card-wrap" and @action-type="feed_list_item"][1]//a[contains(text(),'评论')]/text()''').get()
        item['top_item_like'] = response.xpath('''//div[@class="card-wrap" and @action-type="feed_list_item"][1]//div[@class="card-act"]//li[4]/a/em/text()''').get()
        item['items_id'] = response.xpath('//div[@id="pl_feedlist_index"]//div[@class="card-wrap" and @action-type="feed_list_item"]/@mid').getall()
        item['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d')
        item['detail_url'] = response.url
        self.logger.info(item)
        yield item

if __name__ == '__main__':
    cmdline.execute("scrapy crawl weiboTopicSearchRedisV3".split())
