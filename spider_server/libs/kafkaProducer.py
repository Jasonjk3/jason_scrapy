# -*- ecoding: utf-8 -*-
# @ModuleName: kafkaProducer
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/4/7 11:52
# @Desc:
import logging

from kafka import KafkaProducer
from kafka.errors import kafka_errors
import traceback
import json
logger = logging.getLogger(__name__)


class Producer:
    def __init__(self, ip):
        self.kafka_ip = ip
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_ip,
            key_serializer=lambda k: json.dumps(k).encode(),
            value_serializer=lambda v: json.dumps(v).encode())

    def send(self, topic, key=None, data=None, partition=None):
        # 假设生产的消息为键值对（不是一定要键值对），且序列化方式为json

        future = self.producer.send(
            topic=topic,
            key=key,
            value=data,
            partition=None,
        )  # 向分区1发送消息
        logger.info("send {}".format(str(data)))
        self.producer.flush()
        try:
            future.get(timeout=30)  # 监控是否发送成功
        except kafka_errors:  # 发送失败抛出kafka_errors
            logger.error('kafka发送失败')
            traceback.format_exc()
        logger.info("kafka 发送成功")



if __name__ == '__main__':
    p = Producer('106.15.205.23:9092')
    p.send('test', data='test')
