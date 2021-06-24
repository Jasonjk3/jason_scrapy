# -*- ecoding: utf-8 -*-
# @ModuleName: redis
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/3/26 18:55
# @Desc:
"""
配置redis
"""
import json
import redis

from spider_server import settings


class MyRedis(object):
    def __init__(self, host, port, password=None, db=1):
        self.host = host
        self.port = port
        self.password = password
        self.r = redis.Redis(host=self.host, port=self.port, password=self.password, db=db)


    def write(self, key, value, expire=None):
        """
        写入键值对
        """
        try:
            value = json.dumps(value, ensure_ascii=False)
        except Exception as e:
            print(e)
        self.r.set(key, value, ex=expire)

    def read(self, key):
        """
        读取键值对内容
        """
        value = self.r.get(key)
        if value is None:
            return None
        try:
            value = value.decode('utf-8')
            value = json.loads(value, encoding='utf-8')
        except Exception as e:
            print(e)
        return value

    def hset(self, name, key, value):
        """
        写入hash表
        """
        self.r.hset(name, key, value)

    def hmset(self, key, *value):
        """
        读取指定hash表的所有给定字段的值
        """
        value = self.r.hmset(key, *value)
        return value

    def hget(self, name, key):
        """
        读取指定hash表的键值
        """
        value = self.r.hget(name, key)
        return value.decode('utf-8') if value else value

    def hgetall(self, name):
        """
        获取指定hash表所有的值
        """
        return self.r.hgetall(name)

    def delete(self, *names):
        """
        删除一个或者多个
        """
        r = self.r
        r.delete(*names)

    def hdel(self, name, key):
        """
        删除指定hash表的键值
        """
        r = self.r
        r.hdel(name, key)

    def expire(self, name, expire=None):
        """
        设置过期时间
        """
        r = self.r
        r.expire(name, expire)

    def lpush(self,key,value):
        """
        push list in redis queue
        :param key:
        :param data:
        :return:
        """
        self.r.lpush(key,value)

if __name__ == '__main__':
    rs = MyRedis(settings.REDIS_HOST,settings.REDIS_PORT,db=0)
    aa= ["https://www.bilibili.com","https://www.bilibili.com"]
    for url in aa:
        rs.lpush('city_code.txt:start_urls',url)