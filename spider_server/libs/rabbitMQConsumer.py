import pika
import json
import logging

RABBITMQ_IP = '139.159.204.92'
RABBITMQ_PORT = 8071
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'zh1132'

logger = logging.getLogger(__name__)

class Consumer(object):
    def __init__(self,ip,port,username,password):
        # 建立实例
        credentials = pika.PlainCredentials(username, password)  # mq用户名和密码
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=ip, port=port, credentials=credentials))

        # 声明管道
        self.channel = self.connection.channel()


    def callback(self,ch, method, properties, body):  # 消费回调函数,四个参数为标准格式
        # print(ch)  # 打印看一下是什么
        # print(method)
        # print(properties)
        # 管道内存对象  内容相关信息  后面讲
        try:
            data = json.loads(body.decode("utf8"))
        except Exception as e:
            logger.error(e)
            raise e
        logger.info(f'pull message - > {data}')
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 告诉生成者，消息处理完成

    def pull(self,queue,durable=False):
        # 为什么又声明了一个‘hello’队列？
        # 如果确定已经声明了，可以不声明。但是你不知道那个机器先运行，所以要声明两次。
        self.channel.queue_declare(queue=queue,durable=durable)

        self.channel.basic_consume(  # 消费消息
            on_message_callback=self.callback,  # 如果收到消息，就调用callback函数来处理消息
            queue=queue)

        logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()  # 开始消费消息

    def __del__(self):
        self.connection.close()


if __name__ == '__main__':
    cs = Consumer(RABBITMQ_IP,RABBITMQ_PORT,RABBITMQ_USERNAME,RABBITMQ_PASSWORD)
    cs.pull('python')