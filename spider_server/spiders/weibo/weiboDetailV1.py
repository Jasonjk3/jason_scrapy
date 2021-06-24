import re

from scrapy import cmdline
from scrapy_redis.spiders import RedisSpider

from spider_server.items import WeiboItem


class WeiboDetailV1Spider(RedisSpider):  # scrapy-redis分布式爬虫要继承RedisSpider类
    """
    微博 weibo.cn
    每条微博的详情页
    """
    # 爬虫名
    name = 'weiboDetailV1'
    # 允许域名范围
    allowed_domains = ['weibo.cn', 'weibo.com']
    # scrapy-redis的必需定义，spidername:start_urls 其中spidername为爬虫的名字,start_urls固定
    redis_key = "weiboDetail:start_urls"
    # 自定义设置
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.MyMongoDBPipeline': 300},  # 最终结果往MQ发送
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},  # cookie池
        'DOWNLOAD_DELAY': 10
    }
    base_url = "https://weibo.cn"

    # 解析微博
    def parse(self, response, **kwargs):
        """
        解析本页的数据 TODO 内容没爬到
        """

        tweet_item = WeiboItem()

        tweet_repost_url = response.xpath('.//a[contains(text(),"转发")]/@href').extract()[0]
        user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)

        # 微博URL
        tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_tweet_id.group(2),
                                                                   user_tweet_id.group(1))

        # 发表该微博用户id
        tweet_item['user_id'] = user_tweet_id.group(2)

        # 微博id
        tweet_item['id'] = '{}_{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))

        # create_time_info = ''.join(response.xpath('.//span[@class="ct"]').xpath('string(.)').extract())
        # if "来自" in create_time_info:
        #     # 微博发表时间
        #     tweet_item['created_at'] = create_time_info.split('来自')[0].strip()
        #     # 发布微博的工具
        #     tweet_item['tool'] = create_time_info.split('来自')[1].strip()
        # else:
        #     tweet_item['created_at'] = create_time_info.strip()

        # 点赞数
        like_div = response.xpath('.//a[contains(text(),"赞")]/text()').extract()[0]
        like_num = re.search('\d+', like_div)
        if like_num:
            tweet_item['like_num'] = int(like_num.group())
        else:
            tweet_item['like_num'] = 0

        # 转发数
        repost_div = response.xpath('.//a[contains(text(),"转发")]/text()').extract()[0]
        repost_num = re.search('\d+', repost_div)
        if repost_num:
            tweet_item['repost_num'] = int(repost_num.group())
        else:
            tweet_item['repost_num'] = 0
        # 评论数
        comment_div = response.xpath(
            './/span[contains(text(),"评论") and not(contains(text(),"原文"))]/text()').extract()[0]
        comment_num = re.search('\d+', comment_div)
        if comment_num:
            tweet_item['comment_num'] = int(comment_num.group())
        else:
            tweet_item['comment_num'] = 0
        # 图片
        images = response.xpath('.//img[@alt="图片"]/@src')
        if images:
            tweet_item['image_url'] = images.extract()[0]

        # 视频
        # videos = response.xpath(
        #     './/a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
        # if videos:
        #     tweet_item['video_url'] = videos.extract()[0]

        # 定位信息
        map_node = response.xpath('.//a[contains(text(),"显示地图")]')
        if map_node:
            tweet_item['location'] = True

        # 原始微博，只有转发的微博才有这个字段
        repost_node = response.xpath('.//a[contains(text(),"原文评论")]/@href')
        if repost_node:
            tweet_item['origin_weibo'] = repost_node.extract()[0]

        # 微博内容
        tweet_item['content'] = \
            ''.join(response.xpath('.//div[@id="M_"]/div[1]').xpath('string(.)').extract()) \
                .replace(u'\xa0', '').replace(u'\u3000', '').replace(' ', '')

        if 'location' in tweet_item:
            tweet_item['location'] = \
                response.xpath('.//span[@class="ctt"]/a[last()]/text()').extract()[0]
        yield tweet_item


if __name__ == '__main__':
    # 方便测试
    cmdline.execute("scrapy crawl weiboDetailV1".split())
