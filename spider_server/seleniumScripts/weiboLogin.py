# -*- ecoding: utf-8 -*-
# @ModuleName: weiboLogin
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/3/27 12:31
# @Desc:
from spider_server.seleniumScripts.seleniumClass import SeleniumClass


class Weibo(SeleniumClass):
    """
    TODO 微博模拟登录，登录成功后将cookie写入到cookie池中
    """
    def __init__(self):
        super(Weibo, self).__init__()
        self.login_url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https%3A%2F%2Fweibo.cn%2F%3Fluicode%3D10000011%26lfid%3D102803_ctg1_8999_-_ctg1_8999_home&backTitle=%CE%A2%B2%A9&vt='

    def __del__(self):
        self.browser.quit()

    def login(self):
        self.browser.get(self.login_url)
        self.browser.implicitly_wait(5)
        if 'login' in self.browser.current_url:
            self.browser.find_element_by_id('loginName').send_keys('13517596501')
            self.browser.find_element_by_id('loginPassword').send_keys('mark19970912')
            self.browser.find_element_by_id('loginAction').click()
            input("please input any key to continue...")
            print(self.browser.current_url)
            if 'login' not in self.browser.current_url:
                return True
            else:
                return False
        else:
            return False

    def search(self):
        self.browser.get('https://weibo.cn/search/mblog?advanced=mblog&f=s')
        self.browser.implicitly_wait(2)
        self.browser.find_element_by_xpath('//input[@name="keyword"]').send_keys('火星')
        self.browser.find_element_by_xpath('//input[@name="starttime"]').send_keys('20210401')
        # self.browser.find_element_by_xpath('//input[@name="endtime"]').send_keys('火星')
        self.browser.find_element_by_xpath('//input[@name="smblog"]').click()

    def home_page(self):
        self.login()
        self.search()
        input("please input any key to continue...")


if __name__ == '__main__':
    Weibo().home_page()
