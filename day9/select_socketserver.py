import select
import queue
import socket
import sys

# 生成服务端socket实例
server = socket.socket()
# 设置非阻塞 传入bool类型
server.setblocking(0)

# 设置绑定的ip地址和端口
server_address = ('localhost', 10000)
print(sys.stderr, 'starting up on %s port %s' % server_address)
server.bind(server_address)

# 监听客户端最大连接数
server.listen(5)

# 初始化读取数据的监听列表,最开始时希望从server这个套接字上读取数据
inputs = [server, ]

# 初始化写入数据的监听列表，最开始并没有客户端连接进来，所以列表为空
outputs = []

# 消息队列用字典表示 键为客户端socket对象，值为发送内容 可能有多个客户端连接，发送多条信息，将消息先存入队列而不是直接发送
message_queues = {}

# inputs列表默认存放server 即服务端的socket对象用于等待客户端接入
while inputs:
    print(sys.stderr, '\nwaiting for the next event')
    # 注：select能够监控 f=open()，obj=socket(),sys.stdin,sys.stdout终端输入输出(所有带fileno()方法的文件句柄)
    # 文件操作是python无法检测的,windows也不支持终端输入输出的文件句柄（OSError:应用程序没有调用 WSAStartup，或者 WSAStartup 失败。）
    readable, writeable, exceptional = select.select(inputs, outputs, inputs)
    # 一旦客户端连接，server的内容将改变，select检测到server的变化，将其返回给readable
    for s in readable:
        # 默认只有server，等待客户端连接，但是有了client的socket对象后，等待的可能是客户端发送的消息，这里需要判断是socket还是消息
        if s is server:
            # 创建客户端socket连接 connection 服务端为客户端生成的socket对象，client_address 客户端地址
            connection, client_address = s.accept()
            print(sys.stderr, 'new connection from', client_address)
            # 客户端socket设置非阻塞
            connection.setblocking(0)
            # 因为有读操作发生，所以将此连接加入inputs
            inputs.append(connection)
            # 为每个连接创建一个queue队列，数据并不是立即发送需要放入队列，等待outputs队列有数据才发送，同时确保每个连接接收到正确的数据。
            message_queues[connection] = queue.Queue()
        # 等待的将是客户端发送的数据
        else:
            # 接收客户端数据
            data = s.recv(1024)
            if data:
                print(sys.stderr, 'received "%s" from %s' % (data, s.getpeername()))
                # 将收到的数据放入队列中
                message_queues[s].put(data)
                if s not in outputs:
                    # 将socket客户端的连接加入outputs中，并且用来给客户端返回数据。
                    outputs.append(s)
            else:  # 连接已经断开
                print(sys.stderr, 'closing', client_address, 'after reading no data')
                if s in outputs:
                    # 因为连接已经断开，无需再返回消息，这时候如果这个客户端的连接对象还在outputs列表中，就把它删掉。
                    outputs.remove(s)
                # 连接已经断开，在inputs中select也不用感知
                inputs.remove(s)
                # 关闭会话
                s.close()
                # 从字典中删除服务端为客户端建立连接的socket对象
                del message_queues[s]
    # 一旦有参数，将一直为客户端返回数据
    for s in writeable:
        try:
            # 读取客户端请求信息，采用非阻塞的方式get_nowait() 没有读取到数据抛出异常
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:  # 引发队列空异常
            print(sys.stderr, 'output queue for', s.getpeername(), 'is empty')
            # 没有读取到数据，无需为客户端返回消息，将其从outputs中删除，否则 select将一直感知，并传给writeable
            outputs.remove(s)
        else:# 没有任何异常
            print(sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername()))
            # 此处是服务端原样返回接收到的信息
            s.send(next_msg)
    # 如果服务端或客户端连接发生错误，exceptional将会有内容
    for s in exceptional:
        print(sys.stderr, 'handling exceptional condition for', s.getpeername())
        # 将客户端连接删除
        inputs.remove(s)
        # 如果还有数据未发完
        if s in outputs:
            # 但是连接已经断开，只好从outputs删除
            outputs.remove(s)
        # 关闭会话
        s.close()
        # 删除该客户端连接队列，无须在发送数据了。
        del message_queues[s]