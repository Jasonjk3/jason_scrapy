import json
import re

import scrapy
from lxml import etree
from scrapy import cmdline, Request
from scrapy_redis.spiders import RedisSpider

from spider_server.items import WeibUserItem
from spider_server.libs import extractor


class WeiboUserDetailV3Spider(RedisSpider):  # scrapy-redis分布式爬虫要继承RedisSpider类
    """
    微博 weibo.com
    用户详情页
    """
    # 爬虫名
    name = 'weiboUserDetailV3'
    # 允许域名范围
    allowed_domains = ['weibo.cn', 'weibo.com']
    # scrapy-redis的必需定义，spidername:start_urls 其中spidername为爬虫的名字,start_urls固定
    redis_key = "weiboUserDetailV3:start_urls"
    # 自定义设置
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.MyMongoDBPipeline': 300,
                           'spider_server.pipelines.KafkaMQPipeline': 255
                           },
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},  # cookie池
        'DOWNLOAD_DELAY': 10
    }

    headers = {
        'referer': 'https://weibo.com/u/7589466762/home?wvr=5',
        'Accept': '*/*'
    }

    def make_requests_from_url(self, data):
        try:
            item = json.loads(data) # 从redis中取出是string类型，需转回dict对象
            uid = item.get('uid') # 取出url
            url = f'https://weibo.com/u/{uid}?refer_flag=1001030106_&is_hot=1'
            self.logger.info(f"request url -> {url}")
        except Exception as e:
            self.logger.error('redis队列中取出的数据异常，请检查')
            raise e
        return Request(url, dont_filter=True,meta={'uid':uid},headers=self.headers,callback=self.parse) # 将对象传入meta.data中


    def parse(self, response):
        # print(response)
        try:
            item =WeibUserItem()

            item['username'] = re.findall(r"CONFIG\['onick']='(.+)'",response.text)[0]

            item['uid'] = response.meta['uid']
            # 将html 解析js 代码
            temp = extractor.extract_html(response.text, 'script')
            for row in temp:
                if '"domid":"Pl_Core_UserInfo__6"' in row:  # 详细信息
                    html = self.parse_html(row)
                    if html and len(html):
                        item = self.parse_personinfo(html, item)
                if '"domid":"Pl_Official_Headerv6__1' in row:  # 头部信息
                    html = self.parse_html(row)
                    if html and len(html):
                        item = self.parse_headinfo(html, item)

                if '"domid":"Pl_Core_T8CustomTriColumn__3' in row:  # 粉丝关注
                    html = self.parse_html(row)
                    if html and len(html):
                        item = self.parse_num(html, item)

            item['url'] = response.url
            self.logger.info(item)
            yield item
        except Exception as e:
            self.logger.error(f'parse error -> {e}')

    def clean(self, text):
        text.replace(r'\n', '')
        text.replace(r'\t', '')
        return text.strip()

    def parse_html(self, row):
        data = extractor.extract_json_to_dict(row)
        if data == '':
            return None
        try:
            html = etree.HTML(data.get('html'))  # 拿到JS中的HTML代码
            return html
        except Exception as e:
            self.logger.error(f'html 解析异常 - {e}')
            return None

    def parse_personinfo(self, html, item):
        """
        获取地区 学历 生日
        :param html:
        :param item:
        :return:
        """
        item['location'] = None
        item['edu'] = None
        item['birthday'] = None
        ul = html.xpath('//ul[@class="ul_detail"]//li')
        for li in ul:
            temp = li.xpath('./span[1]/em[@class="W_ficon ficon_cd_place S_ficon"]')
            if temp:  # 地区
                location = li.xpath('./span[2]/text()')[0]
                item['location'] = self.clean(location)
            temp = li.xpath('./span[1]/em[@class="W_ficon ficon_edu S_ficon"]')
            if temp:  # 学历
                edu = li.xpath('./span[2]/a/text()')[0]
                item['edu'] = edu

            temp = li.xpath('./span[1]/em[@class="W_ficon ficon_constellation S_ficon"]')
            if temp:  # 生日
                birthday = li.xpath('./span[2]/text()')[0]
                item['birthday'] = self.clean(birthday)
        return item

    def parse_headinfo(self, html, item):

        temp = html.xpath('//div[@class="pf_username"]//i[contains(@class,"W_icon icon_pf_male")]')
        if len(temp):
            item['gender'] = 'm'

        temp = html.xpath('//div[@class="pf_username"]//i[contains(@class,"W_icon icon_pf_female")]')
        if len(temp):
            item['gender'] = 'f'
        return item

    def parse_num(self, html, item):
        item['following'] = html.xpath('//table[@class="tb_counter"]//td[@class="S_line1"][1]/a/strong/text()')[0]  # 用户关注数
        item['followed'] = html.xpath('//table[@class="tb_counter"]//td[@class="S_line1"][2]/a/strong/text()')[0]  # 用户粉丝数
        item['post_num'] = html.xpath('//table[@class="tb_counter"]//td[@class="S_line1"][3]/a/strong/text()')[0]  # 用户粉丝数
        return item

if __name__ == '__main__':
    # 方便测试
    cmdline.execute("scrapy crawl weiboUserDetailV3".split())
