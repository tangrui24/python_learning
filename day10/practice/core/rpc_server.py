import pika
import os,sys
import time
import optparse
import subprocess
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings
import common
import threading

class Client(object):
    def __init__(self, user=settings.user, password=settings.password,
                 host=settings.host, port=settings.port, timeout=15,
                 host_id=None, binding_keys=None):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.id = self.get_id()  # 设置客户端的唯一ID,一般以客户端IP为唯一ID
        if host_id:
            self.id = host_id  # 如果配置文件设置了ID属性,则以配置文件为优先
        self.binding_keys = binding_keys
        self.queue_name = None  # 队列名称
        self.exchange = "topic_os"
        self.exchange_type = "topic"
        self.response = None
        self.connection = self.connect_server()
        self.channel = self.create_chanel()
        self.create_exchange()
        self.create_queue()
        self.bind()
        self.timeout = timeout  # 设置一个任务最长执行的时间,超过这个设置时间则返回超时提示

    def get_id(self):
        import re
        self.exec_call("ip addr 2> /dev/null ||ifconfig")
        get_ip = self.response
        result = re.findall("(\d+\.\d+\.\d+\.\d+)", str(get_ip, "utf-8"))
        for ip in result:
            if ip != "127.0.0.1" and not (ip.endswith("255") or ip.startswith("255")):
                return ip

    def connect_server(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        return pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                            port=self.port,
                                                                            credentials=credentials))

    def create_chanel(self):
        return self.connection.channel()

    def create_exchange(self):
        self.channel.exchange_declare(exchange=self.exchange, type=self.exchange_type)

    def create_queue(self):
        self.queue_name = self.channel.queue_declare(exclusive=True).method.queue

    def bind(self):
        print("Routing key {}".format(self.binding_keys))
        for binding_key in self.binding_keys:
            self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=binding_key)

    def exec_call(self,cmd):
        if type(cmd) == bytes:
            cmd = str(cmd, "utf-8")
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.response = (result.stdout.read() or result.stderr.read())

    def on_request(self, ch, method, props, body):
        before = time.monotonic()
        exec_command = threading.Thread(target=self.exec_call, args=(body,))
        exec_command.start()
        exec_command.join(self.timeout)
        after = time.monotonic()
        if after - before > self.timeout:
            self.response = bytes("command exec timeout", "utf8")
        # 打印请求
        print(" [.] receive task :(%s)" % str(body, "utf8"))
        message = {"host": self.id, "data": self.response}
        # 回应请求
        ch.basic_publish(exchange="", routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=\
                                                                                                      props.correlation_id),
                         body=bytes(str(message), "utf-8"))

        ch.basic_ack(delivery_tag=method.delivery_tag)  # make message persistent

    def start(self):
        # 告诉RabbitMQ服务端当前消息还没处理完的时候就不要再给我发新消息了。
        self.channel.basic_qos(prefetch_count=1)

        # 接收客户端请求，调用on_request函数处理
        self.channel.basic_consume(self.on_request, queue=self.queue_name)
        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()  # 监听客户端请求

def main():
    try:
        from conf.settings import server, port, timeout, host_id, binding_keys
    except ImportError:
        server = "192.168.1.108"
        port = 5672
        timeout = 15
        host_id = None
        binding_keys = ["remote.call"]
    binding_list = sys.argv[1:]  # 路由KEY支持接收控制台输入,优先级最高
    if binding_list:
        binding_keys = binding_list
    client = Client(host=server, port=port, timeout=timeout, host_id=host_id, binding_keys=binding_keys)
    client.start()

if __name__ == "__main__":
    main()

