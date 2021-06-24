# -*- ecoding: utf-8 -*-
# @ModuleName: seleniumClass
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/4/6 14:57
# @Desc:

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from spider_server import settings
class SeleniumClass():
    def __init__(self):
        options = webdriver.ChromeOptions()
        #        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # TODO 开启无头模式容易会被反爬识别
        self.timeout = settings.SELENIUM_TIMEOUT
        self.browser = webdriver.Chrome(executable_path='../../chromedriver.exe', options=options)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)
