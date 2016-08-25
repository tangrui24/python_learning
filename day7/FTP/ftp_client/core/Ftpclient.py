import socket,hashlib,json,os,sys,time,shutil,logging
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from conf import settings


class FtpClient(object):
    ip_port = (settings.HOST,settings.PORT)
    request_code_list = {
        "100": "INTSTRUCTIONS_NOT_FOUND",
        "200": "AUTH_PASS",
        "201": "USERNAME_OR_PASSWORD_ERROR",
        "202": "TOO_MANY_TRYING_LOGING",
        "300": "CLIENT_READY_TO_RECV",
        "301": "CLIENT_READY_TO_SENT",
        "302": "FILE_DOESNT_ESXIT_OR_WITHOUT_HOMEDIR",
        "303": "CLIENT_RECV_DONE",
        "400": "FILE_MD5_AGREEMENT DOWNLOAD OK",
        "401": "FILE_MD5_NOT_CONSISTENT DOWNLOAD ERR",
        "500": "SWITCH_DIR_SUCCESS",
    }

    def __init__(self):
        self.log(settings.HOST)
        self.connect()
        if self.auth():
            self.handle()
        else:
            sys.exit("bye")

    def connect(self):
        #建立连接
        try:
            self.sk = socket.socket()
            self.sk.connect(self.ip_port)
        except socket.error as e:
            self.logger.error(e)
            sys.exit(e)

    def auth(self):
        #用户认证
        try_time = 0
        while try_time < 3:
            username = input("请输入用户名：").strip()
            if len(username) == 0 : continue
            passwd = input("请输入密码：").strip()
            if len(passwd) == 0 : continue
            user_dic = {
                "username":username,
                "passwd":passwd
            }
            #发送请求信息
            user_info = json.dumps(user_dic)
            req_msg = bytes("auth|%s" % user_info, "utf8")
            self.sk.send(req_msg)
            #服务端返回状态码
            server_reply = self.sk.recv(50)
            server_reply_ret = str(server_reply,"utf8").split("|")
            if server_reply_ret[0] == "200":
                print(server_reply_ret[1])
                self.user = username
                self.cur_path = ""
                self.logger.info(server_reply_ret[1])
                return True
            else:
                print(server_reply_ret[1])
                self.logger.info(server_reply_ret[1])
                try_time += 1
        else:
            print(self.request_code_list["202"])
            self.logger.error(self.request_code_list["202"])

    def handle(self):
        while True:
            #用户输入命令
            user_input = input("ftp:%s%s>>>" % (self.user, self.cur_path)).strip()
            if len(user_input) == 0:continue
            if user_input == 'q':break
            if user_input == '?':user_input = user_input.replace("?", "help")
            if user_input.startswith('cd'):user_input = user_input.replace("cd", "switch_dir")
            self.instructions(user_input)

    def instructions(self,instructions):
        #客户端发起指令 统一转发
        instructions = instructions.split()
        function_str = instructions[0]  # 客户端传入的指令,第一个参数必须在服务器端有相应的方法处理
        if hasattr(self,function_str):
            func = getattr(self,function_str)
            func(instructions)
        else:
            print("%s failed" % instructions[0])
            self.logger.warn(self.request_code_list["100"])

    def help(self,msg):
        #获取帮助信息
        if len(msg) > 1:
            print("请输入help或?查看帮助")
        else:
            req_msg = bytes("help|%s" % msg[0], "utf8")
            self.sk.send(req_msg)
            server_reply = self.sk.recv(1024)
            data = str(server_reply, "utf8")
            print(data)

    def encrypt_md5(self, file):
        """
        获取文件的MD5值，用于MD5校验
        :param file: 文件名
        :return: MD5值
        """
        fmd = hashlib.md5()
        file = open(file, 'rb')
        byte = file.read(2048)
        while byte != b'':
            fmd.update(byte)
            byte = file.read(2048)
        file.close()
        md5_value = fmd.hexdigest()
        return md5_value

    def get(self,msg):
        #客户端下载文件名
        filename = msg[1]
        if filename.count("\\"):
            filename = filename.split("\\")[-1]
        temp_file = "%s.downloadtmp" % filename
        if os.path.exists(temp_file):
            received_size = os.path.getsize(temp_file)
            self.logger.warn("存在下载未完成文件 文件名：%s|下载大小：%s" % (temp_file, received_size))
        else:
            received_size = 0
            self.logger.info("开始下载文件 %s" % filename)
        #请求信息
        client_req_info = {
            "file_name": filename,
            "received_size": received_size
        }
        client_req_json = json.dumps(client_req_info)
        req_msg = bytes("get|%s" % client_req_json, "utf8")
        self.sk.send(req_msg)
        #接收服务器标志信息格式为bytes
        server_ack_msg = self.sk.recv(200)
        server_ack_info = str(server_ack_msg, "utf8").split("|")
        if server_ack_info[0] == "300":#"SERVER_READY_TO_SENT"
            server_ack_dic = json.loads(server_ack_info[1])
            s_md5 = server_ack_dic["file_md5"]
            file_size = int(server_ack_dic["file_size"])
            #发送客户端确认接收信号 ，处理服务端连包问题
            self.sk.send(bytes("%s" % self.request_code_list["300"], "utf8"))  # "CLIENT_READY_TO_RECV"
            #判断数据是否接收完
            try:
                f = open(temp_file, "ab")
                f.seek(received_size)
                while received_size != file_size:
                    data = self.sk.recv(1024)
                    f.write(data)
                    received_size += len(data)
                    self.processbar(file_size, received_size)
                else:
                    f.close()
                    print("---- recv file done and start check md5 -------")
                    c_md5 = self.encrypt_md5(temp_file)
                    print("------- check md5 result -------")
                    if c_md5 == s_md5:
                        shutil.move(temp_file, filename)
                        print(self.request_code_list["400"])
                        self.logger.info(self.request_code_list["400"])
                    else:
                        os.remove(temp_file)
                        print(self.request_code_list["401"])
                        self.logger.warn(self.request_code_list["401"])
            except Exception as e:
                f.close()
                self.logger.error(e)
                sys.exit()
        elif server_ack_info[0] == "302":
            print(server_ack_info[1])
            self.logger.warn(server_ack_info[1])

    def put(self,msg):
        #获取文件名
        file_name = msg[1]
        #检查文件是否存在
        if os.path.isfile(file_name):
            #获取文件大小
            file_size = os.path.getsize(file_name)
            file_md5 = self.encrypt_md5(file_name)
            file_json = json.dumps({
                'filename': file_name,
                'filesize': file_size,
                'filemd5': file_md5
            })
            #发送请求：文件名和文件大小
            req_msg = bytes("put|%s" % file_json, "utf8")
            self.sk.send(req_msg)
            #服务端返回状态码
            server_reply = self.sk.recv(100)
            server_reply_ret = str(server_reply, "utf8").split("|")
            if server_reply_ret[0] == "301":#"SERVER_READ_TO_RECV"
                #客户端边读边发
                f = open(file_name, "rb")
                #server_reply 返回已接受文件大小
                sent_size = int(server_reply_ret[1])
                f.seek(sent_size)
                self.logger.info("开始上传文件 文件名：%s|已传输：%s" % (file_name, sent_size))
                try:
                    while file_size != sent_size:
                        data = f.read(1024)
                        self.sk.send(data)
                        sent_size += len(data)
                        self.processbar(file_size, sent_size)
                    else:
                        f.close()
                        #接收服务端返回文件是否成功状态信息
                        upload_msg = self.sk.recv(200)
                        upload_ret = str(upload_msg, "utf8").split("|")
                        print(upload_ret[1])
                        self.logger.info(upload_ret[1])
                except Exception as e:
                    self.logger.error(e)
                    sys.exit()
            elif server_reply_ret[0] == "303":  # "DISK_QUOTA_EXCEEDED"
                print(server_reply_ret[1])
                self.logger.warn(server_reply_ret[1])
        else:
            print("The filename error, please check the input")
            self.logger.error("The filename error, please check the input")

    def lsfile(self,msg):
        #显示用户当前目录
        #判断用户输入lsfile or lsfile dir
        if len(msg) == 1:
            req_msg = bytes("lsfile|.", "utf8")
        else:
            req_msg = bytes("lsfile|%s" % msg[1], "utf8")
        self.sk.send(req_msg)
        #服务器状态信息
        #ack_msg:code|code_status"
        server_ack_msg = self.sk.recv(100)
        server_res_msg = str(server_ack_msg,"utf8").split("|")
        if server_res_msg[0] == "600":
            server_res_size = int(server_res_msg[1])
            #发送客户端确认信号，处理服务端连包问题
            self.sk.send(bytes("CLIENT_READY_TO_RECV","utf8"))
            #定义默认接收为0
            received_size = 0
            #判断数据是否接收完
            try:
                while received_size < server_res_size:
                    #接收数据
                    data = self.sk.recv(2048)
                    #接收数据可能有丢失,需要接收后统计接收到的数据
                    received_size += len(data)
                else:
                    dir_data = str(data, "utf8")
                    dir_file = json.loads(dir_data)
                    print("---- lsfile ---- ")
                    for k,v in enumerate(dir_file):
                        print("%s\t" %v,end='\n')
            except Exception as e:
                self.logger.error(e)
                pass
        else:
            print(server_res_msg[1])
            self.logger.error(server_res_msg[1])

    def switch_dir(self,msg):
        """
        用户家目录下，目录切换
        :param msg:
        :return:
        """
        if len(msg) == 1:
            req_msg = bytes("switch_dir|%s" % self.user, "utf8")
        else:
            req_msg = bytes("switch_dir|%s" % msg[1], "utf8")
        #发送请求
        self.sk.send(req_msg)
        server_ack_msg = self.sk.recv(100)
        server_ack_ret = str(server_ack_msg, "utf8").split("|")
        if server_ack_ret[0] == "500":
            self.cur_path = server_ack_ret[1]
            self.logger.info("cd %s ok" % server_ack_ret[1])
        else:
            print(server_ack_ret[1])
            self.logger.warn(server_ack_ret[1])

    def processbar(self, total_size, current_size):
        """
        :param totalsize:
        :param curr_size:
        :return:
        """
        c = int(current_size / total_size * 50)
        p = current_size / total_size * 100
        j = "=" * c
        sys.stdout.write("\r已完成：[ %.2f%% ] || [%s>]\r" % (p, j))
        sys.stdout.flush()
        if p == 100:
            print("\n")

    def log(self, client):
        self.logger = logging.getLogger(client)
        self.logger.setLevel(settings.LOG_LEVEL)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(settings.log_file,encoding="utf-8")
        fh.setLevel(settings.LOG_LEVEL)

        # 定义handler的输出格式formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)

    def exit(self,msg):
        #程序退出
        req_msg = bytes("exit|exit", "utf8")
        self.sk.send(req_msg)
        server_ret = self.sk.recv(50)
        self.sk.close()
        self.logger.info("client [%s] close the session")
        sys.exit("bye")

if __name__ == "__main__":
    ftp_client = FtpClient()




