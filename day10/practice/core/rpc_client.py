import pika
import os,sys
import time
import uuid
import optparse
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings
import common

class Client_Controll(object):
    def __init__(self, user=settings.user, password=settings.password, host=settings.host, port=settings.port, logger=None, timeout=16):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.response = []
        self.queue_name = None  # 队列名称
        self.log = logger
        self.correlation_id = None  # 任务ID
        self.exchange = "topic_os"
        self.exchange_type = "topic"
        self.connection = self.connect_server()
        self.channel = self.create_chanel()
        self.create_exchange()
        self.create_queue()
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.queue_name)
        self.timeout = timeout + 1  # 设置一个任务最长执行的时间,超过这个设置时间则不继续等待任务返回结果

    def connect_server(self):
        self.log.info("Connecting to {}:{}".format(self.host, self.port))
        credentials = pika.PlainCredentials(self.user, self.password)
        return pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port,
                                                                 credentials=credentials))

    def create_chanel(self):
        return self.connection.channel()

    def create_exchange(self):
        self.channel.exchange_declare(exchange=self.exchange, type=self.exchange_type)

    def create_queue(self):
        self.queue_name = self.channel.queue_declare(exclusive=True).method.queue
        self.log.debug("Create queue {}".format(self.queue_name))

    def call(self, cmd, routing_key="remote.call"):
        self.response = []
        # 生成corr_id
        self.corr_id = str(uuid.uuid4())  # 任务ID
        # 发起请求
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                         reply_to=self.queue_name,  # 回调队列 #告诉服务端从这个队列回应请求
                                         correlation_id=self.corr_id,  # 请求关联corr_id
                                         ),
                                   body=cmd)
        # 监听回应消息
        before = time.monotonic()
        after_len = 0
        while True:
            if len(self.response) != after_len:
                before_len = len(self.response)  # 当接收的数据不为空,则计算当前接收的数据长度
            else:
                # 为了避免网络延时造成发出去的任务与收到的任务回复不完整,则休眠一小会,如果网络环境很差,这个值可能需要增大
                before_len = after_len
                time.sleep(0.5)
            self.connection.process_data_events()  # 处理数据事件,检查是否有消息发回到此队列
            if len(self.response) == before_len and before_len:  # 消息接收完了
                break
            after = time.monotonic()  # 纪录执行完一个任务后的时间
            if (after - before) > self.timeout:  # 当执行时间大于16s,则判定任务超时返回
                break
        return self.response

    def on_response(self, ch, method, props, body):
        self.response.append(body)  # 将接收的消息追加到队列


def main():
    try:
        from conf.settings import server, port, timeout
    except ImportError:
        server = "192.168.1.108"
        port = 5672
        timeout = 16
    usage = """
        该工具可用于控制绑定了不同路由KEY的主机处理不同的事件
        usage: %prog [options]
        """
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-e", "--exec", type="string", help="input command")
    parser.add_option("-g", "--bind", type="string", help="input bind_keys")
    (option, arg) = parser.parse_args()
    cmd = option.exec
    bind_key = option.bind
    if not cmd:
        parser.error("\033[31;1m the following arguments are requires: command\033[0m")
    if not bind_key:
        bind_key = "remote.call"
    logger = common.set_log()
    server = Client_Controll(host=server, port=port, logger=logger, timeout=timeout)
    response = server.call(cmd=cmd, routing_key=bind_key)
    for message in response:
        message = eval(str(message, "utf-8"))
        host_id = message["host"]
        data = message["data"]
        print("\n{}\n[\033[33;1m{}\033[0m]\n{}\n{}".format(
            "".ljust(60, "-"), host_id, str(data, "utf-8"), "".ljust(60, "-")))

if __name__ == "__main__":
    main()

