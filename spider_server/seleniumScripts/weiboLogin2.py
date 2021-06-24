# -*- ecoding: utf-8 -*-
# @ModuleName: weiboLogin2
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/4/29 10:34
# @Desc:

# -*- coding:utf-8 -*-
import requests
import time
import rsa
import binascii
import math
import random
from urllib import parse
from base64 import b64encode


class Login(object):
    def __init__(self, username, password):
        self.sess = requests.session()
        self.username = username
        self.password = password
        self.headers = {
            'Referer': 'https://weibo.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }

    @property
    def get_username(self):
        su = b64encode(parse.quote(self.username).encode('utf8')).decode('utf8')
        return su

    def get_pubkey(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            # 'callback':'sinaSSOController.preloginCallBack',
            'su': self.get_username,
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': round(time.time() * 1000)
        }
        try:
            response = self.sess.get(url=url, headers=self.headers, params=params).json()
            return response
        except Exception:
            print("获取公钥失败!")

    def get_password(self, public_key_json):
        pubkey = public_key_json['pubkey']
        servertime = public_key_json['servertime']
        nonce = public_key_json['nonce']
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        password_str = str(servertime) + '\t' + str(nonce) + '\n' + self.password
        password = binascii.b2a_hex(rsa.encrypt(password_str.encode('utf8'), public_key)).decode('utf8')
        return password

    def pre_login(self, public_key_json, password):
        """
        获取通行证
        :param public_key: get_pubkey()函数获得的json数据
        :param password: 加密后的密码
        :return:
        """
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        servertime = public_key_json['servertime']
        pcid = public_key_json['pcid']
        nonce = public_key_json['nonce']
        rsakv = public_key_json['rsakv']
        # 验证码
        img_code = self.sess.get(
            url=f'https://login.sina.com.cn/cgi/pin.php?r={math.floor(random.random() * 1e8)}&s=0&p={pcid}',
            headers=self.headers).content
        with open('./a.png', 'wb') as fp:
            fp.write(img_code)
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': "",
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pcid': pcid,
            'door': input("code>>>").strip(),
            'vsnf': '1',
            'su': self.get_username,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': password,
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': '207',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT',
        }
        response = self.sess.post(url=url, headers=self.headers, data=data).json()
        return response

    def login(self, ticket_json):
        """
        :param ticket_json: 获得通行证的json数据
        :return:
        """
        url = 'https://passport.weibo.com/wbsso/login'
        try:
            tket = ticket_json['ticket']
        except KeyError:
            raise KeyError("验证码输错啦")
        data = {
            'ticket': tket,
            'ssosavestate': round(time.time()),
            'callback': 'sinaSSOController.doCrossDomainCallBack',
            'scriptId': 'ssoscript0',
            'client': 'ssologin.js(v1.4.19)',
            '_': round(time.time() * 1000)
        }
        response = self.sess.post(url=url, headers=self.headers, data=data)
        print(response.text)

    def main(self):
        """
        主函数
        :return:
        """
        public_key_json = self.get_pubkey()  # 第一次发请求，检测账号，获取公钥等相关数据
        password = self.get_password(public_key_json)  # 对密码进行加密
        ticket = self.pre_login(public_key_json, password)  # 发请求获取通行证
        self.login(ticket)
        # response = self.sess.get('https://weibo.com/u/7453607229/home').text # 携带登录的数据去测试能否得到正确的页面

if __name__ == '__main__':

    user = Login('13027931774','jasonforjob')
    user.main()
