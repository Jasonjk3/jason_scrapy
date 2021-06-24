import json
import re
import scrapy
from scrapy import cmdline, Request
from scrapy_redis.spiders import RedisSpider

from spider_server.items import WeiboItem, WeiboCommentsItem

class WeiboCommentsV2Spider(RedisSpider):  # scrapy-redis分布式爬虫要继承RedisSpider类
    """
    微博V2   m.weibo.cn
    指定微博的详情页评论
    """
    # 爬虫名
    name = 'weiboCommentsV2'
    # 允许域名范围
    allowed_domains = ['weibo.cn', 'weibo.com']
    # scrapy-redis的必需定义，spidername:start_urls 其中spidername为爬虫的名字,start_urls固定
    redis_key = "weiboCommentsV2:start_urls"
    redis_name = "weiboUserDetailV3"
    # 自定义设置
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.MyMongoDBPipeline': 300,
                           'spider_server.pipelines.KafkaMQPipeline': 255,
                           'spider_server.pipelines.ItemRedisPipeline': 251},
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},  # cookie池
        'DOWNLOAD_DELAY': 10
    }
    base_url = "https://m.weibo.cn"
    headers = {
        'referer': 'https://weibo.com/u/7589466762/home?wvr=5',
        'Accept': '*/*'
    }
    page = 0

    def make_requests_from_url(self, item):
        """
            获取微博热门话题的标题，拼接成url
        """
        try:
            data = json.loads(item) # 从redis中取出是string类型，需转回dict对象
            item_id = data.get('top_item_id') # 取出url
            url = f'https://m.weibo.cn/comments/hotflow?id={item_id}&mid={item_id}&max_id_type=0'
            self.logger.info(f"request url -> {url}")
        except Exception as e:
            self.logger.error('redis队列中取出的数据异常，请检查')
            raise e
        return Request(url, dont_filter=True,meta={"data":data,'item_id':item_id},headers=self.headers) # 将对象传入meta.data中

    # 解析微博
    def parse(self, response, **kwargs):
        # print(response)
        # print(response.text)
        try:
            data = json.loads(response.text)['data']
            next_id = data['max_id']
            self.page+=1
        except:
            return
        for c in data['data']:
            row = self.info_parser(c)
            item=WeiboCommentsItem()
            item.update(row)
            item['item_id'] = response.meta['item_id']
            self.logger.info(item)
            yield item

        item_id = response.meta['item_id']
        next_url = f'https://m.weibo.cn/comments/hotflow?id={item_id}&mid={item_id}&max_id_type=0&max_id={next_id}'
        yield Request(url=next_url,meta={'item_id':item_id})
    def info_parser(self,data):
        id, time, text = data['id'], data['created_at'], data['text']
        user = data['user']
        uid, username, following, followed, gender = \
            user['id'], user['screen_name'], user['follow_count'], user['followers_count'], user['gender']
        return {
            'comment_id':id,
            'createtime': time,
            'text': text,
            'uid': uid,
            # 'username': username,
            # 'following': following,
            # 'followed': followed,
            # 'gender': gender,
            'like_count':data['like_count']
        }
if __name__ == '__main__':
    # 方便测试
    cmdline.execute("scrapy crawl weiboCommentsV2".split())
