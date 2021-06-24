# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


import json
import logging

import pymongo
import pymysql
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from spider_server import settings
from scrapy_redis.pipelines import RedisPipeline

from spider_server.libs.rabbitMQProducer import Producer
from spider_server.libs.kafkaProducer import Producer as KafkaProducer

logger = logging.getLogger(__name__)


class ScrapyspiderPipeline:
    def process_item(self, item, spider):
        pass
        return item


class UrlRedisPipeline(RedisPipeline):
    """
    适用于主爬虫只需要传递url的redis队列管道
    """

    def process_item(self, item, spider):
        # 队列key xx:start_urls
        if hasattr(spider, 'redis_name'):  # 判断是否指定了redis队列名
            key = f'{spider.redis_name}:start_urls'
        else:
            key = f'{spider.name}:start_urls'

        if item['url']:
            self.server.lpush(key, item['url'])  # push data in redis queue
            logger.info(f'redis rpush to {key} 成功')
        else:
            logger.error(f'redis rpush to {key} 失败,item 为空')
        return item


class ItemRedisPipeline(RedisPipeline):
    """
    适用于主爬虫需要传递url及其他参数（对象形式）的redis队列管道
    """

    def process_item(self, item, spider):
        # 队列key xx:start_urls
        if hasattr(spider, 'redis_name'):  # 判断是否指定了redis队列名
            key = f'{spider.redis_name}:start_urls'
        else:
            key = f'{spider.name}:start_urls'
        if isinstance(item, dict):
            if item:
                self.server.lpush(key, json.dumps(item))  # push data in redis queue
                logger.info(f'redis rpush to {key} 成功')
            else:
                logger.error(f'redis rpush to {key} 失败,item 为空')
        else:
            self.server.lpush(key, json.dumps(dict(item)))  # push data in redis queue
            logger.info(f'redis rpush to {key} 成功')
        return item


class RabbitMQPipeline():
    def __init__(self, username, password, ip, port, queue, exchange):
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port
        self.queue = queue
        self.exchange = exchange

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            username=crawler.settings.get('RABBITMQ_USERNAME'),
            password=crawler.settings.get('RABBITMQ_PASSWORD'),
            ip=crawler.settings.get('RABBITMQ_IP'),
            port=crawler.settings.get('RABBITMQ_PORT'),
            queue=crawler.settings.get('QUEUE_NAME'),
            exchange=crawler.settings.get('EXCHANE_NAME'),
        )

    def open_spider(self, spider):
        """
        爬虫启动时
        :param spider:
        :return:
        """
        self.producer = Producer(username=self.username, password=self.password,
                                 ip=self.ip, port=self.port)
        self.producer.init_exchange(exchange=self.exchange)
        self.producer.init_queue(queue=self.queue)

    def _process_item(self, item, spider):
        self.producer.push(item, exchange=self.exchange, routing_key=self.queue, durable=True)
        return item

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def close_spider(self, spider):
        """
        爬虫关闭时
        :param spider:
        :return:
        """
        self.producer.close()


class MongoDBPipeline(object):
    """
    mongodb中间件
    """

    def __init__(self, mongodb_uri, mongodb_database):
        self.mongodb_uri = mongodb_uri
        self.mongodb_database = mongodb_database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_database=crawler.settings.get('MONGODB_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.database = self.client[self.mongodb_database]

    def _process_item(self, item, spider):
        allowed_spiders = item.mongodb_spiders  # 允许xx爬虫调用该方法
        allowed_collections = item.mongodb_collections  # 集合名
        if allowed_spiders and spider.name in allowed_spiders:
            for allowed_collection in allowed_collections:
                self.database[allowed_collection].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # _process_item主要实现了一个deferToThread方法，该方法作用是返回一个deferred对象,
        # 不过回调函数在另一个线程处理,主要用于数据库/文件异步读写操作。
        return deferToThread(self._process_item, item, spider)


class MySQLPipeline():
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8',
                                  port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def _process_item(self, item, spider):
        allowed_spiders = item.mongodb_spiders
        allowed_tables = item.mongodb_tables
        if allowed_spiders and spider.name in allowed_spiders:
            for allowed_table in allowed_tables:
                data = dict(item)
                keys = ', '.join(data.keys())
                values = ', '.join(['%s'] * len(data))
                sql = 'insert into %s (%s) values (%s)' % (allowed_table, keys, values)
                self.cursor.execute(sql, tuple(data.values()))
                self.db.commit()
        return item

    def process_item(self, item, spider):
        # _process_item主要实现了一个deferToThread方法，该方法作用是返回一个deferred对象,
        # 不过回调函数在另一个线程处理,主要用于数据库/文件异步读写操作.
        return deferToThread(self._process_item, item, spider)


class MyMongoDBPipeline(MongoDBPipeline):
    """
    自定义mongodb中间件
    """

    def _process_item(self, item, spider):
        allowed_spiders = getattr(item, 'mongodb_spiders')
        allowed_collections = getattr(item, 'mongodb_collections')
        action = getattr(item, 'mongodb_action')
        primary_key = getattr(item, 'primary_key', None)

        if allowed_spiders and spider.name in allowed_spiders:
            for allowed_collection in allowed_collections:
                if action == 'insert':
                    self.database[allowed_collection].insert(dict(item))
                    logger.info('mongodb insert 成功')

                elif action == 'update' and primary_key:
                    self.database[allowed_collection].update({primary_key: item[primary_key]}, {'$set': dict(item)},
                                                             True)
                    logger.info('mongodb update 成功')
                else:
                    logger.error('mongodb 插入数据失败...')
        return item

    def process_item(self, item, spider):
        # _process_item主要实现了一个deferToThread方法，该方法作用是返回一个deferred对象,
        # 不过回调函数在另一个线程处理,主要用于数据库/文件异步读写操作。
        return deferToThread(self._process_item, item, spider)


class KafkaMQPipeline():
    def __init__(self, ip):
        self.ip = ip

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            ip=crawler.settings.get('KAFKA_IP')
        )

    def open_spider(self, spider):
        """
        爬虫启动时
        :param spider:
        :return:
        """
        self.producer = KafkaProducer(self.ip)

    def _process_item(self, item, spider):
        if hasattr(item, 'kafka_topic'):
            topic = item.kafka_topic
        else:
            topic = 'test'
        if hasattr(item, 'kafka_key'):
            key = item.kafka_key
        else:
            key = None
        self.producer.send(topic, key=key, data=dict(item))
        return item

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    # def close_spider(self, spider):
    #     """
    #     爬虫关闭时
    #     :param spider:
    #     :return:
    #     """
    #     pass
