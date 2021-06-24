# -*- ecoding: utf-8 -*-
# @ModuleName: kafkaConsumer
# @Author: jason
# @Email: jasonforjob@qq.com
# @Time: 2021/4/7 11:52
# @Desc:
import json

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'kafka_demo',
    bootstrap_servers='106.15.205.23:9092',
    group_id='kafka_demo'
)
for message in consumer:
    print("receive, key: {}, value: {}".format(
        json.loads(message.key.decode()),
        json.loads(message.value.decode())
        )
    )

# producer.close()

