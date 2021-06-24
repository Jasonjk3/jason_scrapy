# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import logging
import time

import requests
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import random

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from spider_server.libs import util
from spider_server.libs.util import cookie2str_format
from spider_server.seleniumScripts.seleniumClass import SeleniumClass

import requests

logger = logging.getLogger(__name__)


class ScrapyspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddleware(SeleniumClass):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, timeout=None):
        super().__init__()

    def __del__(self):
        self.browser.quit()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'))

    def process_request(self, request, spider):
        '''
        在下载器中间件中对接使用selenium，输出源代码之后，构造htmlresponse对象，直接返回
        给spider解析页面，提取数据
        并且也不在执行下载器下载页面动作
        htmlresponse对象的文档：
        :param request:
        :param spider:
        :return:
        '''

        logger.info('Chorme is Starting')
        self.wait = WebDriverWait(self.browser, self.timeout)
        try:
            # TODO Selenium添加自定义cookie，已知坑，selenium要先请求一次url，
            #  才能知道cookie指向;cookie中要包含name,value
            # if len(request.cookies) > 0:
            #     self.browser.get(request.url)
            #
            #     for key in request.cookies:
            #         coo = {'name': key.strip(), 'value': request.cookies[key].strip()}
            #         print(coo)
            #         self.browser.delete_cookie(key)
            #         self.browser.add_cookie(cookie_dict=coo)
            #     print(self.browser.get_cookies())
            self.browser.get(request.url)
            self.browser.implicitly_wait(5)
            body = self.browser.find_element_by_xpath("//*").get_attribute("outerHTML")
            # Cookies = self.browser.get_cookies()
            # print(Cookies)
            # cookies = {}
            # for c in Cookies:
            #     cookies[c['name']] = c['value']
            self.browser.quit()

            return HtmlResponse(url=request.url, body=body, request=request, encoding='utf-8', status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)


class CookiesMiddleware():
    """
    cookie池中间件
    """

    def __init__(self, cookies_server_ip):
        self.logger = logging.getLogger(__name__)
        self.cookies_server_ip = cookies_server_ip

    def get_cookies(self):
        """
        子类重写该方法，并调用父类_get_cookies
        e.g :
            return super()._get_cookies(name='douban_cookies')
        """
        pass

    def _get_cookies(self, name):
        """
        获取cookie
        :return:
        """
        try:
            resp = requests.get(f'http://{self.cookies_server_ip}/api_v1/spider/getCookies?type={name}')
            # cookie 需要是字典对象
            data = resp.json().get('data')
            cookie = util.cookie_format(data)
            if cookie:
                self.logger.info(f'Get Cookies : {cookie}')
            else:
                self.logger.warning(f'Get Cookies is None!')
            return cookie
        except Exception as e:
            self.logger.error(f'Get Cookies error ! {e}')
            return False

    def process_request(self, request, spider):
        self.logger.debug('Getting Cookies')
        cookies = self.get_cookies()
        if cookies:
            request.cookies = cookies
            self.logger.debug('Using Cookies {cookies}'.format(cookies=json.dumps(cookies)))

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            cookies_server_ip=settings.get('COOKIES_SERVER_IP')
        )


class WeiboCookiesMiddleware(CookiesMiddleware):
    """
    微博cookie池
    """

    def __init__(self, cookies_server_ip):
        super().__init__(cookies_server_ip)

    def get_cookies(self):
        return super()._get_cookies(name='weibo')

class ZhihuCookiesMiddleware(CookiesMiddleware):
    """
    cookie池
    """

    def __init__(self, cookies_server_ip):
        super().__init__(cookies_server_ip)

    def get_cookies(self):
        return super()._get_cookies(name='zhihu')



class DoubanCookiesMiddleware(CookiesMiddleware):
    """
    豆瓣cookie池
    """

    def __init__(self, cookies_file_path):
        super().__init__(cookies_file_path)

    def get_cookies(self):
        return super()._get_cookies(name='douban_cookies')


class ProxyMiddleware():
    """
    代理池中间件 TODO 完善代理池中间件
    """

    def __init__(self, proxy_url, proxy_fail_times):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url
        self.proxy_fail_times = proxy_fail_times

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        if request.meta.get('retry_times') >= self.proxy_fail_times:
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                self.logger.debug('Using Proxy {proxy}'.format(proxy=proxy))
                request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxy_url=settings.get('PROXY_URL'),
            proxy_fail_times=settings.get('PROXY_FAIL_TIMES', 1),
        )


class RandomUserAgent(object):
    """
    请求头 User-Agent 中间件
    """

    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent_list=crawler.settings.get('USER_AGENT_LIST')
        )

    def process_request(self, request, spider):
        # 从列表中随机抽选出一个ua值
        ua = random.choice(self.user_agent_list)

        # ua值进行当前拦截到请求的ua的写入操作
        request.headers.setdefault('User-Agent', ua)
        spider.logger.info('headers : %s' % request.headers)
