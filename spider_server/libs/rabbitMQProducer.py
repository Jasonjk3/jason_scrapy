import pika
import json
import logging

logger = logging.getLogger(__name__)

RABBITMQ_IP = '139.159.204.92'
RABBITMQ_PORT = 8071
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'zh1132'


class Producer():
    def __init__(self, ip, port, username, password):
        # 建立实例
        credentials = pika.PlainCredentials(username, password)  # mq用户名和密码
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=ip, port=port, credentials=credentials))

        # 声明管道
        self.channel = self.connection.channel()

    def init_exchange(self,exchange):
        if exchange=='':
            raise Exception("exchange is not declare in setting.py")
        result=self.channel.exchange_declare(exchange=exchange, exchange_type='fanout') # 扇型交换机（fanout exchange），它把消息发送给它所知道的所有队列
        logger.info(f'{exchange}交换机声明成功: {result}')

    def init_queue(self, queue='temp', durable=True):
        # 声明队列
        result = self.channel.queue_declare(queue=queue, durable=durable)  # durable确保队列持久化
        logger.info(f'{queue}队列声明成功: {result}')

    def push(self, data=None, exchange='', routing_key='', durable=False):

        if durable:
            delivery_mode = 2
        else:
            delivery_mode = None

        # 声明消息队列，消息将在这个队列传递，如不存在，则创建
        try:
            message = json.dumps(dict(data))
        except Exception as e:
            logger.error(e)
            raise e
        # 向队列插入数值 routing_key是队列名 # 注意在rabbitmq中，消息想要发送给队列，必须经过交换(exchange)，
        # 可以使用空字符串交换(exchange='')，它允许我们精确的指定发送给哪个队列(routing_key=''),
        # 参数body值发送的数据,# delivery_mode 支持数据持久化:代表消息是持久的  2
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message,
                                   properties=pika.BasicProperties(delivery_mode=delivery_mode))
        logger.info(f'exchange = {exchange} | durable = {durable} | push message to {routing_key} -> {message}')

    def close(self):
        self.connection.close()

    # def __del__(self):
    #     # 关闭连接 释放内存
    #     self.connection.close()


if __name__ == '__main__':
    pd = Producer(RABBITMQ_IP, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    # pd.init_queue('temp')
    for i in range(1, 100):
        pd.push(routing_key='python-city_code.txt', data={'index': i}, durable=True)
