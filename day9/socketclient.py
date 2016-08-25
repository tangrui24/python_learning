import socket
import sys

# 消息列表
messages = ['this is the message. ',
            'It will be sent ',
            'in parts.',
            ]
# ip_port
server_address = ('localhost', 10000)

# socket对象
socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
         socket.socket(socket.AF_INET,socket.SOCK_STREAM),
          ]

print(sys.stderr, 'connecting to %s port %s' % server_address)
# 发起连接
for s in socks:
    s.connect(server_address)
# 发送消息
for message in messages:
    for s in socks:
        print(sys.stderr, '%s: sending "%s"' % (s.getsockname(), message))
        # 发送请求
        s.send(bytes(message, "utf8"))
    for s in socks:
        try:
            # 接收信息
            data = s.recv(1024)
            print(sys.stderr, '%s: received "%s"' % (s.getsockname(), data))
        except Exception as e:
            print(e, 'closing socket', s.getsockname())
            # 未收到回应，连接终止
            s.close()