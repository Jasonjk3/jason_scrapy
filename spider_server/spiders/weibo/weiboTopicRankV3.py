# -*- coding: utf-8 -*-
import json

import scrapy
from lxml import etree
from scrapy import Request, cmdline

from spider_server.libs import util, extractor

class WeiboTopicRankV3(scrapy.Spider):
    """
    微博热门话题排行榜
    weibo.com V3
    """
    name = 'weiboTopicRankV3'
    allowed_domains = ['weibo.cn', 'weibo.com']
    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.ItemRedisPipeline': 300},
        'DOWNLOAD_DELAY': 5,
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},
    }
    redis_name = 'weiboTopicSearchRedisV3' # 发送数据到微博话题搜索队列
    page=1

    def start_requests(self):  # 发送请求之前的回调函数
        url = "https://d.weibo.com/231650?cfs=920&Pl_Discover_Pt6Rank__3_filter=&Pl_Discover_Pt6Rank__3_page=1"
        yield Request(url=url,callback=self.parse,dont_filter=True)
    def parse(self, response):
        # print(response)
        # 将html 解析js 代码
        temp = extractor.extract_html(response.text, 'script')
        data = ''
        for row in temp:
            if '标题栏筛选项' in row: # 找到目标js 并转成字典
                data = extractor.extract_json_to_dict(row)
        if data =='':
            return
        try:
            html = etree.HTML(data.get('html')) # 拿到JS中的HTML代码
        except Exception as e:
            self.logger.error(f'html 解析异常 - {e}')
            return
        divs = html.xpath('//div[@class="WB_innerwrap"]/div/ul//li')

        def clean(text):
            text.replace(r'\n', '')
            text.replace(r'\t', '')
            return text.strip()

        for li in divs:
            item = {}
            # item['subtitle'] = clean(li.xpath('.//div[@class="subtitle"]/text()')[0])
            # item['title'] = clean(li.xpath('.//a[@class="S_txt1"]/text()')[0])
            url = li.xpath('.//a[@class="S_txt1"]/@href')[0]
            url = url.split('=')[-1]
            item['title'] = util.url_decode(url)
            item['tag'] = clean(li.xpath('.//a[@class="W_btn_b W_btn_tag"]/text()')[-1])
            print(item)
            yield item
        self.page+=1
        next_url = f"https://d.weibo.com/231650?cfs=920&Pl_Discover_Pt6Rank__3_filter=&Pl_Discover_Pt6Rank__3_page={self.page}"
        yield Request(next_url,dont_filter=True,callback=self.parse)
if __name__ == '__main__':
    # 方便测试
    cmdline.execute("scrapy crawl weiboTopicRankV3".split())