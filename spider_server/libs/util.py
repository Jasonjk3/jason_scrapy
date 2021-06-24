# -*- ecoding: utf-8 -*-
# @ModuleName: util
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2020/12/15 12:18
# @Desc: 工具类
from urllib.request import quote, unquote

def write(path, data, type='a'):
    with open(path, type, encoding='utf-8') as f:
        f.writelines(data)


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read().split("\n")
    return data


def cookie_format(input_cookie):
    """
    cookie 字符串 反序列化成字典
    :param input_cookie:
    :return:
    """
    cookie = {}
    for line in input_cookie.split(';'):
        key, value = line.split('=', 1)
        cookie[key] = value
    return cookie

def cookie2str_format(input_cookie):
    """
    cookie 字典对象序列化成字符串
    :param input_cookie:
    :return:
    """
    temp= ';'.join([f"{key}={input_cookie[key]}"for key in input_cookie])
    return temp



def url_encode(text,encoding='utf-8'):
    """
    url 编码
    :return:
    """
    result = quote(text,encoding=encoding)
    return result
def url_decode(text,encoding='utf-8'):
    """
    url 解码
    :param text:
    :param encoding:
    :return:
    """
    result = unquote(text, encoding=encoding)
    return result


if __name__ == '__main__':
    a = """bid=nDIo3PKbJQQ; douban-fav-remind=1; gr_user_id=551c181c-761a-46f1-97c8-535f78ffc9cd; _vwo_uuid_v2=D3A1E1DA514C0B1FE8A2EE1A51B21F88B|1bae357f755cea4a74b8026226f1fbcd; ll="118282"; _ga=GA1.2.1893574906.1608195403; __utmc=30149280; __utmz=30149280.1618223641.17.15.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ap_v=0,6.0; __utma=30149280.1893574906.1608195403.1618223641.1618281525.18; __utmt=1; _pk_ref.100001.2939=%5B%22%22%2C%22%22%2C1618281661%2C%22https%3A%2F%2Fmusic.douban.com%2F%22%5D; _pk_ses.100001.2939=*; viewed="30333540_26916947_30150912_20390695_30325325_1195590_1418999_34464674_35080873_26836970"; _pk_id.100001.2939=93e441ee7847d5bb.1618223661.2.1618282030.1618223761.; __utmb=30149280.28.9.1618282030927"""
    print(cookie_format(a))

    b = {'bid': 'nDIo3PKbJQQ', ' douban-fav-remind': '1', ' gr_user_id': '551c181c-761a-46f1-97c8-535f78ffc9cd', ' _vwo_uuid_v2': 'D3A1E1DA514C0B1FE8A2EE1A51B21F88B|1bae357f755cea4a74b8026226f1fbcd', ' ll': '"118282"', ' _ga': 'GA1.2.1893574906.1608195403', ' __utmc': '30149280', ' __utmz': '30149280.1618223641.17.15.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/', ' ap_v': '0,6.0', ' __utma': '30149280.1893574906.1608195403.1618223641.1618281525.18', ' __utmt': '1', ' _pk_ref.100001.2939': '%5B%22%22%2C%22%22%2C1618281661%2C%22https%3A%2F%2Fmusic.douban.com%2F%22%5D', ' _pk_ses.100001.2939': '*', ' viewed': '"30333540_26916947_30150912_20390695_30325325_1195590_1418999_34464674_35080873_26836970"', ' _pk_id.100001.2939': '93e441ee7847d5bb.1618223661.2.1618282030.1618223761.', ' __utmb': '30149280.28.9.1618282030927'}

    print(cookie2str_format(b))
