
import pika
import uuid

class FibonacciRpcClient(object):
    def __init__(self):
        #连接rabbitmq
        self.credentials = pika.PlainCredentials("admin", "admin")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="192.168.1.108", port=5672, credentials=self.credentials))
        #定义通道
        self.channel = self.connection.channel()
        #定义专用队列，队列名随机，断开连接时删除队列
        result = self.channel.queue_declare(exclusive=True)
        #获取队列名
        self.callback_queue = result.method.queue
        #接收服务端回应的callback_queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
    #接收消息
    def on_response(self, ch, method, props, body):
        #服务端回应的correlation_id等于请求的id 接收数据
        if self.corr_id == props.correlation_id:
            self.response = body
    #发起请求
    def call(self, n):
        self.response = None
        #生成corr_id
        self.corr_id = str(uuid.uuid4())
        #发起请求
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',#发送至rpc_queue队列
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,#回调队列 #告诉服务端从这个队列回应请求
                                         correlation_id = self.corr_id, #请求关联corr_id
                                         ),
                                   body=str(n))#消息
        #监听回应消息
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)

fibonacci_rpc = FibonacciRpcClient()
print(" [x] Requesting fib(30)")
#发送请求
print(fibonacci_rpc.call(30))
