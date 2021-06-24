# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request, cmdline


class WeiboHotRankV2Spider(scrapy.Spider):
    """
    微博热搜 m.weibo.cn
    """
    name = 'weiboHotRankV2'
    allowed_domains = ['m.weibo.cn', 'weibo.cn', 'weibo.com']
    start_urls = ['http://m.weibo.cn/']

    custom_settings = {
        'ITEM_PIPELINES': {'spider_server.pipelines.ItemRedisPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {'spider_server.middlewares.WeiboCookiesMiddleware': 200},  # cookie池
        'DOWNLOAD_DELAY': 10
    }
    base_url = "https://m.weibo.cn"
    redis_name = 'weiboHotRank'

    def start_requests(self):
        url = 'https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot&title=%E5%BE%AE%E5%8D%9A%E7%83%AD%E6%90%9C&extparam=seat%3D1%26pos%3D0_0%26dgr%3D0%26mi_cid%3D100103%26cate%3D10103%26filter_type%3Drealtimehot%26c_type%3D30%26display_time%3D1619317279&luicode=10000011&lfid=231583'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
        }
        yield Request(url=url, headers=headers)

    def parse(self, response):

        json_data = json.loads(response.text)
        data = json_data['data']
        print(data)
        tag_dict = {'hot': '热', 'fei': '沸', 'new': '新', 'jian': '荐', 'plus': '↑'}

        # 时热点，每分钟更新一次
        try:
            top_realTime_list = data['cards'][0]['card_group']
            top_up_list = data['cards'][1]['card_group']
        except KeyError:
            return []

        result = []
        for row in top_realTime_list:
            try:
                item = {}
                title = row['desc']
                if 'desc_extr' not in row.keys():
                    num = 0
                else:
                    num = row['desc_extr']

                tag = ''
                if 'icon' in row.keys():
                    tag = ''
                    for key in tag_dict.keys():
                        if key in row['icon']:
                            tag = tag_dict[key]
                            break
                # print(title, num, tag)
                item['title'] = title
                item['num'] = num
                item['tag'] = tag
                result.append(item)
            except:
                continue
        # print('#' * 50)
        # print('实时上升热点:')

        for row in top_up_list:
            try:
                item = {}
                title = row['desc']
                if 'desc_extr' not in row.keys():
                    num = 0
                else:
                    num = row['desc_extr']

                tag = ''
                if 'icon' in row.keys():
                    tag = ''
                    for key in tag_dict.keys():
                        if key in row['icon']:
                            tag = tag_dict[key]
                            break

                item['title'] = title
                item['num'] = num
                item['tag'] = tag
                result.append(item)
            except Exception as e:
                self.logger.error(e)
                continue
        print(result)
        print([row.get('title') for row in result])
        for row in result:
            yield row


if __name__ == '__main__':
    # 方便测试
    cmdline.execute("scrapy crawl weiboHotRankV2".split())
