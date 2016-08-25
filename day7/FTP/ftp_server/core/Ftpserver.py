#!/usr/bin/env python
import os,sys,json,time,hashlib
import socket,subprocess,socketserver
import shutil
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings
from core.account import *
import logging

class FtpServer(socketserver.BaseRequestHandler):
    __database = settings.user_data_file
    response_code_list = {
        "200": "AUTH_PASS",
        "201": "USERNAME_OR_PASSWORD_ERROR",
        "300": "SERVER_READY_TO_SENT",
        "301": "SERVER_READ_TO_RECV",
        "302": "FILE_DOESNT_ESXIT_OR_WITHOUT_HOMEDIR",
        "303": "DISK_QUOTA_EXCEEDED",
        "400": "UPLOAD SUCCESS",
        "401": "UPLOAD FAILED",
        "500": "SWITCH_DIR_SUCCESS",
        "501": "SWITCH_DIR_FAILED",
        "600": "LSFILE SUCCESS",
        "601": "LSFILE FAILED"
    }

    def load_db(self):
        self.dict_user = load_data(self.__database)

    def auth(self,msg):
        #加载用户数据库
        self.load_db()
        auth_ret = False
        #获取客户端发送的用户密码
        auth_info = json.loads(msg[1])
        user = auth_info['username']
        passwd = auth_info['passwd']
        self.user = user
        if not self.check_user(user):
            #print("用户名错误")
            auth_ret = "201"
            self.logger.error(self.response_code_list["201"])
        else:
            if self.check_user_passwd(passwd):
                #print("登录成功")
                auth_ret = "200"
                self.logger.info(self.response_code_list["200"])
                self.homedir = "%s\%s" %(settings.user_data_dir,self.dict_user[self.user]["homedir"])
                self.curdir = "%s\%s" %(settings.user_data_dir,self.dict_user[self.user]["homedir"])
                self.quota = self.dict_user[user]["limit"]
            else:
                #print("密码错误")
                auth_ret = "201"
                self.logger.error(self.response_code_list["201"])
        if auth_ret:#验证成功返回客户端状态信息
            print("user: %s has passed authentication!" % self.user)
            self.logger.info("user: %s has passed authentication!" % self.user)
        ack_msg = "%s|%s" % (auth_ret, self.response_code_list[auth_ret])
        self.request.send(bytes(ack_msg, "utf8"))

    def check_user(self, user):
        """
        验证用户名
        :param user:输入用户名
        :return: True or False
        """
        if user in self.dict_user:
            return True
        else:
            return False

    def check_user_passwd(self,passwd):
        """
        验证密码
        :param passwd:
        :return:
        """
        if passwd == self.dict_user[self.user]['pwd']:
            return True
        else:
            return False

    def has_privilege(self, path):
        """
        用户是否具有操作权限
        :param path: 操作目录
        :return:
        """
        abs_path = os.path.abspath(path)
        if abs_path.startswith(self.homedir):
            return True
        else:
            return  False

    def file_dir_is_exits(self, path):
        """
        判断是否是文件或目录
        :param path:
        :return:
        """
        if os.path.isdir(path):
            return 0
        elif os.path.isfile(path):
            return 1
        else:
            return None

    def quota_check(self, path):
        #检查当前用户可用空间
        nTotalSize = 0
        #os.walk返回三个值，读取根目录，根目录下的目录，根目录下的文件
        #以根目录第一个子目录为新的根目录，读取其文件夹和文件。
        #再以第一个目录的子文件夹为根目录，读取文件夹和文件，以此类推...
        for strRoot, lsDir, lsFiles in os.walk(path):
            for strFile in lsFiles:
                nTotalSize = nTotalSize + os.path.getsize(os.path.join(strRoot, strFile))
        return self.quota - nTotalSize

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

    def put(self, msg):
        #client upload file to server
        #获取文件名和文件大小和MD5
        file_info = json.loads(msg[1])
        file_name = file_info['filename']
        file_size = file_info['filesize']
        c_md5 = file_info['filemd5']
        file_abs_path = os.path.join(self.curdir, file_name)
        self.logger.info("接收客户端上传文件请求：put|%s|%s|%s" % (file_name, file_size, c_md5))
        #默认使用临时文件存储，文件MD5一致在修改文件名，不一致删除临时文件
        temp_file = "%s.uploadtmp" % file_abs_path
         #判断临时文件是否存在，获取接收大小
        if self.file_dir_is_exits(temp_file) == 1: #返回1表示文件存在
            receive_size = os.path.getsize(temp_file)
            self.logger.warn("存在未传完的文件：fileame:%s 已经传入：%s" % (temp_file, receive_size))
        else:
            receive_size = 0
        #检查当前用户磁盘剩余配额，配额剩余-剩余文件大小
        file_free_size = file_size - receive_size
        if self.quota_check(self.homedir) >= file_free_size:
            #服务端发送准备接收状态和已接受文件大小
            server_ack_msg = bytes("301|%s" % receive_size, "utf8")
            self.logger.info(self.response_code_list["301"])
            self.request.send(server_ack_msg)
            #服务端打开文件准备接收
            #先把数据写入缓存文件，MD5验证一致再改成原文件名
            f = open(temp_file, 'a+b')
            f.seek(receive_size)
            while file_size != receive_size:
                try:
                    data = self.request.recv(1024)
                except Exception as e:#使用if not data 无法匹配到空
                    f.close()
                    self.logger.error(e)
                    break
                else:
                    f.write(data)
                    receive_size += len(data)
            else:
                f.close()
                print("---- recv file done starting check md5 -------")
                self.logger.info("---- recv file done starting check md5 -------")
                #md5值校验
                s_md5 = self.encrypt_md5(temp_file)
                if c_md5 == s_md5:
                    #文件传输成功，更改源文件名
                    shutil.move(temp_file, file_abs_path)
                    server_ack_msg = bytes("400|%s" % self.response_code_list["400"], "utf8")
                    self.logger.info(self.response_code_list["400"])
                else:
                    #文件损坏，删除文件
                    os.remove(temp_file)
                    server_ack_msg = bytes("401|%s" % self.response_code_list["401"], "utf8")
                    self.logger.warn(self.response_code_list["401"])
                print("---- check done -------")
                self.logger.info("---- check done -------")
                self.request.send(server_ack_msg)
        else:
            #服务端发送请求失败状态
            server_err_msg = bytes("303|%s" % self.response_code_list["303"], "utf8")
            self.logger.warn(self.response_code_list["303"])
            self.request.send(server_err_msg)

    def get(self, msg):
        #client download file to server
        #客户端发送 "put|filename|received_size"
        client_req_json = json.loads(msg[1])
        #获取文件名
        filename = client_req_json["file_name"]
        #获取客户端接收文件大小
        sent_size = client_req_json["received_size"]
        #获取文件绝对路径
        file_abs_path = os.path.join(self.curdir, filename)
        self.logger.info("接收客户端下载文件请求: get|%s|%s" % (filename, sent_size))
        #判断文件存在 , 用户权限
        if self.file_dir_is_exits(file_abs_path) == 1 and self.has_privilege(file_abs_path):
            filesize = os.path.getsize(file_abs_path)
            filemd5 = self.encrypt_md5(file_abs_path)
            self.logger.info("下载文件信息：文件大小：%s md5: %s" % (filesize, filemd5))
            #服务端发送确认信息：文件大小和文件MD5
            download_json = {
                "file_size": filesize,
                "file_md5": filemd5
            }
            down_file_info = json.dumps(download_json)
            #ack_msg："code|filesize|md5"
            server_ack_msg = bytes("300|%s" % down_file_info, "utf8")
            self.logger.info(self.response_code_list["300"])
            #服务端发送确认信息
            self.request.send(server_ack_msg)
            #接收客户端确认信息
            client_ack_msg = self.request.recv(100)
            if str(client_ack_msg, "utf8") == "CLIENT_READY_TO_RECV":
                f = open(file_abs_path,"rb")
                f.seek(sent_size)
                #判断文件大小不等于发送数
                while filesize != sent_size:
                    #文件下载传输过程：打开文件，读入字符，传输字符 直至文件读完
                    try:#传输中断打印错误
                        data = f.read(1024)
                        self.request.send(data)
                        sent_size += len(data)
                    except Exception as e:
                        f.close()
                        self.logger.error(e)
                        break
                else:
                    f.close()
                    print("---- sent file done -------")
                    self.logger.info("---- sent file done -------")
        else:#发送失败状态
            server_err_msg = bytes("302|%s" % self.response_code_list["302"], "utf8")
            self.logger.warn(self.response_code_list["302"])
            self.request.send(server_err_msg)

    def help(self, msg):
        #client request command help
        help_msg = ("""the available commands are:
                    put file : upload the data to server
                    get file : upload the data to server
                    cd dir :  switch the current dir
                    lsfile dir : view the file in the current dir
                    exit : exit
                    help : Print this message""")
        #客户端发送 ？或 help 服务端响应help_msg
        if msg[1] == "?" or msg[1] == "help":
            self.request.send(bytes(help_msg, "utf8"))

    def switch_dir(self,msg):
        #The client switch in the home directory
        #设定切换标志False
        switch_ret = False
        #获取客户端切换路径
        dir_path = msg[1]
        #客户端输入一个cd指令，则切换至用户家目录
        if dir_path == self.user or dir_path == "\\" or dir_path == "~":
            dir_abs_path = self.homedir
        #. 返回当前目录
        elif dir_path == ".":
            dir_abs_path = self.curdir
        #.. 返回上一级
        elif dir_path == "..":
            dir_abs_path = os.path.dirname(self.curdir)
        else:#切换指定目录
            dir_abs_path = os.path.join(self.curdir,dir_path)
        #判断是否有权限，目录是否存在
        if self.has_privilege(dir_abs_path) and self.file_dir_is_exits(dir_abs_path) == 0:
            #改变当前目录
            self.curdir = dir_abs_path
            cd_path = dir_abs_path.split(self.homedir)[1]
            switch_ret = True
        else:
            switch_ret = False
        #判断切换状态
        if switch_ret:
            server_ack_msg = bytes("500|%s" % cd_path, "utf8")
            self.logger.info("%s:%s" % (cd_path, self.response_code_list["500"]))
        else:
            server_ack_msg = bytes("501|%s" % self.response_code_list["501"], "utf8")
            self.logger.warn(self.response_code_list["501"])
        self.request.send(server_ack_msg)

    def lsfile(self,msg):
        #Check the current directory files
        #获取绝对路径
        dir_path = os.path.join(self.curdir, msg[1])
        #判断目录是否存在
        if self.file_dir_is_exits(dir_path) == 0:
            #显示当前目录下的文件和目录
            ret = os.listdir(dir_path)
            file_list = json.dumps(ret)
            cmd_size = len(file_list)
            #服务端发送的确认信息:标记和命令结果大小
            server_ack_msg = bytes("600|%s" % cmd_size, "utf8")
            #服务端发送确认信息
            self.request.send(server_ack_msg)
            #接收客户端确认信息
            client_ack_msg = self.request.recv(50)
            #判断客户端信息是否开始接收标志
            if str(client_ack_msg,"utf8") == "CLIENT_READY_TO_RECV":
                self.request.send(bytes(file_list,"utf8"))
        else:
            server_err_msg = bytes("601|%s" % self.response_code_list["601"], "utf8")
            self.logger.warn(self.response_code_list["601"])
            self.request.send(server_err_msg)

    def exit(self,msg):
        #client close the session
        #接收客户端发送退出请求
        if msg[0] == "exit":
            ack_msg = bytes("exit|success", "utf8")
            self.logger.info("client %s close the session" % self.client_add)
            self.request.send(ack_msg)
            self.request.close()

    def handle(self):#socketserve必须有一个handle函数注意别写错了。。。
        #接收客户端请求，交给指令转发处理
        self.client_add = self.client_address[0]
        self.log(self.client_add)
        self.logger.info("welcome %s client to connet" % self.client_add)
        while True:
            try:
                client_req = self.request.recv(1024)
            except Exception as e:
                self.logger.error(e)
                break
            instructions = str(client_req, "utf8")
            self.instructions(instructions)

    def instructions(self,instructions):
        #指令转发器，接收客户端传入格式为"instructions|[args...]"
        instructions = instructions.split("|")
        function_str = instructions[0] # 客户端发过来的指令中,第一个参数都必须在服务器端有相应的方法处理
        if hasattr(self,function_str): #判断指令是否在对象中存在
            func = getattr(self,function_str)#获取指令的内存地址
            func(instructions)#调用指令

    def log(self, client):
        self.logger = logging.getLogger(client)
        self.logger.setLevel(settings.LOG_LEVEL)
        # 创建一个handler，用于写入日志文件
        self.fh = logging.FileHandler(settings.log_file,encoding="utf-8")
        self.fh.setLevel(settings.LOG_LEVEL)

        # 定义handler的输出格式formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.fh.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(self.fh)



def run():
    ftpserver = socketserver.ThreadingTCPServer((settings.HOST,settings.PORT),FtpServer)
    print("ftp server waiting...")
    ftpserver.serve_forever()

if __name__ == "__main__":
    run()
