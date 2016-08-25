#_*_coding:utf-8_*_
import os,sys
Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)
import models
import MyException
import mylib
from conf import settings
from conf import template
from sqlalchemy import create_engine,Table
from  sqlalchemy.orm import sessionmaker

#连接数据库
engine = create_engine(settings.DB_CONN,echo=False)
SessionCls = sessionmaker(bind=engine)
session = SessionCls()


def auth():
    '''
    堡垒机登录验证
    :return:
    '''
    count = 0
    while count <3:
        username = input("\033[32;1mUsername:\033[0m").strip()
        if len(username) ==0:continue
        password = input("\033[32;1mPassword:\033[0m").strip()
        if len(password) ==0:continue
        # 查询堡垒机用户和密码
        user_obj = session.query(models.UserProfile).filter(models.UserProfile.username == username,
                                                            models.UserProfile.password == password).first()
        if user_obj:
            return user_obj
        else:
            count += 1
            print("wrong username or password, you have %s more chances." % (3-count-1))
    else:
        raise MyException("201")


def start_session(userobj, argvs):
    """
    开启堡垒机
    :param userobj:
    :return:
    """
    print('going to start sesssion ')
    #认证
    user = auth()
    if user:
        print(template.welcome % user)
        print(user.groups)
        exit_flag = False
        while not exit_flag:
            # 显示当前用户管理组和特定主机
            if user.hostuser_list:
                print('\033[32;1mz.\tungroupped hosts (%s)\033[0m' % len(user.hostuser_list) )
            for index, group in enumerate(user.groups,1):
                print('\033[32;1m%s.\t%s (%s)\033[0m' % (index, group.name, len(group.hostuser_list)))


def create_users(userobj, argvs):
    '''
    创建堡垒机用户
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        # 获取userprofile配置文件
        user_file = argvs[argvs.index("-f") + 1]
    else:
        raise Exception("106")
    source = mylib.yaml_parser(user_file)
    if source:
        for key, val in source.items():
            print(key, val)
            # 添加堡垒机用户
            obj = models.UserProfile(username=key, password=val.get('password'))
            # 添加堡垒机用户关联组
            if val.get('groups'):
                # 数据库查询组过滤组名是[xxx]
                groups = session.query(models.Group).filter(models.Group.name.in_(val.get('groups'))).all()
                if not groups:
                    raise MyException("105")
                # 关联堡垒机用户和组
                obj.groups = groups
            # 添加堡垒机用户关联绑定主机用户
            if val.get("hostuser_list"):
                for i in val.get("hostuser_list"):
                    user, host = i.split("@")
                    #查询已经关联的主机和主机用户
                    hostuser_list = session.query(models.HostUser).join(models.HostUser.hosts).filter(models.Host.hostname == host, models.HostUser.username == user).first()
                    if not hostuser_list:
                        raise MyException("104")
                    obj.hostuser_list.append(hostuser_list)
            session.add(obj)
        session.commit()

def create_groups(userobj, argvs):
    '''
    创建主机组
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        group_file = argvs[argvs.index("-f") + 1]
    else:
        raise Exception("106")
    source = mylib.yaml_parser(group_file)
    if source:
        for key,val in source.items():
            print(key,val)
            obj = models.Group(name=key)
            if val.get('hostuser_list'):
                #添加主机用户
                for i in val.get("hostuser_list"):
                    # [ root@h1, appmon@h2 ]
                    user, host = i.split("@")
                    #查询主机和主机用户关联 条件为user, host
                    hostuser_list = session.query(models.HostUser).join(models.HostUser.hosts).filter(models.Host.hostname == host, models.HostUser.username == user).first()
                    if not hostuser_list:
                        raise MyException("104")
                    obj.hostuser_list.append(hostuser_list)
            if val.get('user_profiles'):
                #查询堡垒机用户是否存在
                user_profiles = session.query(models.UserProfile).filter(models.UserProfile.username.in_(val.get('user_profiles'))).all()
                if not user_profiles:
                    raise MyException("103")
                obj.userprofiles = user_profiles
            session.add(obj)
        session.commit()

def create_hosts(userobj, argvs):
    '''
    添加主机
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        hosts_file = argvs[argvs.index("-f") + 1]
    else:
        raise MyException("106")
    source = mylib.yaml_parser(hosts_file)
    if source:
        for key,val in source.items():
            print(key,val)
            #添加主机信息
            obj = models.Host(hostname=key,ip_addr=val.get('ip_addr'), port=val.get('port') or 22)
            session.add(obj)
        session.commit()

def create_remoteusers(userobj, argvs):
    '''
    添加主机用户
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        remoteusers_file = argvs[argvs.index("-f") + 1]
    else:
        raise MyException("106")
    source = mylib.yaml_parser(remoteusers_file)
    if source:
        for key,val in source.items():
            print(key, val)
            # 此处必须关联主机
            if val.get('hostname'):
                for i in val.get('hostname'):
                    # 查询被关联主机是否存在
                    obj = session.query(models.Host.id).filter(models.Host.hostname == i).first()[0]
                    if not obj:
                        raise MyException("104")
                    # 添加主机用户
                    host_user = models.HostUser(username=key, auth_type=val.get('auth_type'), password=val.get('password'), host_id=obj)
                session.add(host_user)
            else:
                raise MyException("104")
        session.commit()

def syncdb(userobj, argvs):
    """
    初始化表结构
    :param userobj:
    :param argvs:
    :return:
    """
    print("start Syncing DB....")
    models.Base.metadata.create_all(engine) #创建所有表结构

def help(userobj,nothing):
    print(template.help_str)
