s12_day8_ftp

程序介绍：

	1.服务端提供如下功能：
          多线程连接
	  显示目录文件
	  上传文件
	  下载文件
	  用户磁盘限额
	  用户家目录切换
	  进度条
          断点续传
	  记录日志
          错误代码


FTP#程序主目录
├── ftp_client #客户端程序目录
│   ├── bin #客户端执行程序入口
│   │   ├── ftpclient_start.py #执行程序
│   │   └── __init__.py
│   ├── conf#配置文件目录
│   │   ├── __init__.py
│   │   └── settings.py #配置文件
│   ├── core#主逻辑目录
│   │   ├── Ftpclient.py #主逻辑文件
│   │   └── __init__.py
│   ├── db #数据目录
│   │   └── __init__.py
│   ├── __init__.py
│   └── log#日志目录
│       ├── ftp_client.log #日志
│       └── __init__.py
├── ftp_server#服务端程序目录
│   ├── bin#服务端执行程序入口
│   │   ├── ftpserver_start.py #执行程序
│   │   └── __init__.py
│   ├── conf#配置文件目录
│   │   ├── __init__.py
│   │   └── settings.py #配置文件
│   ├── core#主逻辑目录
│   │   ├── account.py #初始化用户信息
│   │   ├── Ftpserver.py #主逻辑文件爱你
│   │   └── __init__.py
│   ├── db#数据库
│   │   ├── akok #用户目录
│   │   │   └── test
│   │   ├── __init__.py
│   │   ├── koka #用户目录
│   │   │   ├── 1
│   │   │  │   ├── 2
│   │   │  │   │  └── __init__.py
│   │   │  │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── user.db #用户数据库文件
│   ├── __init__.py
│   └── log#日志目录
│       ├── ftp_server.log #日志
│       └── __init__.py
└── __init__.py