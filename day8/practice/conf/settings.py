#!/usr/bin/env python
# coding:utf-8
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RSA_DIR = '%s/var/rsas' % BASE_DIR  # 秘钥文件目录

LOG_FILE = '%s/var/log/manager.var' % BASE_DIR  # 日志文件目录

MULT_NUM = 5  # 进程数

# 分组
GROUPS = {
    "group1": ['web1'],
    "group2": ['web1', 'web2'],
}
# 主机
HOSTS = {
    "web1": {
        "hostname": "192.168.1.108",
        "username": "root",
        "password": "123456",
        "port": 22,
        "pkey": os.path.join(BASE_DIR, 'id_rsa'),
    },
    "web2":
    {
        "hostname": "192.168.1.115",
        "username": "root",
        "password": "123456",
        "port": 22,
    }
}

# 错误码和错误信息
CODE_LIST = {
    "101": "Group %s is not exit!",
    "102": "Host is not exit!",
    "103": "Options is error, please use -h to see the help doc!",
    "104": "Commend execute fail",
    "105": "Module %s is not exit!",
    "106": "Destination file or directory %s is not exit!",
    "107": "Source file or directory %s is not exit!",
}
