import os,sys,logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#用户数据目录
user_data_dir = os.path.join(r"%s\db" % base_dir)

#用户数据库文件名
user_data_file = os.path.join(user_data_dir, 'user.db')

#日志文件
log_file = os.path.join(base_dir, r"log\ftp_server.log")

LOG_LEVEL = logging.INFO

HOST = "0.0.0.0"

PORT = 20000





