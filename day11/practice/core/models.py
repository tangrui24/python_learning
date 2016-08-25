#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sqlalchemy import create_engine,and_,or_,func,Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey,UniqueConstraint,\
    DateTime
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy_utils import ChoiceType,PasswordType
import pymysql

Base = declarative_base()  # 生成一个SqlORM 基类

#主机用户同组关联表
HostUser2Group = Table('hostuser_2_group', Base.metadata,
    Column('hostuser_id', ForeignKey('host_user.id'), primary_key=True),
    Column('group_id', ForeignKey('group.id'), primary_key=True),
)
#堡垒机用户权限同组关联
UserProfile2Group = Table('userprofile_2_group', Base.metadata,
    Column('userprofile_id', ForeignKey('user_profile.id'), primary_key=True),
    Column('group_id', ForeignKey('group.id'), primary_key=True),
)
#堡垒机用户同主机用户
UserProfile2HostUser= Table('userprofile_2_hostuser', Base.metadata,
    Column('userprofile_id',ForeignKey('user_profile.id'), primary_key=True),
    Column('hostuser_id',ForeignKey('host_user.id'), primary_key=True),
)


class Host(Base):
    """
    主机表
    """
    __tablename__ = 'host'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(64), unique=True, nullable=False)
    ip_addr = Column(String(128), unique=True, nullable=False)
    port = Column(Integer,default=22)

    def __repr__(self):
        return "<id=%s,hostname=%s, ip_addr=%s>" % (self.id,
                                                    self.hostname,
                                                    self.ip_addr)


class Group(Base):
    """
    主机组表关联主机用户和堡垒机用户
    """
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    # hostuser_list
    # userprofiles
    def __repr__(self):
        return "<id=%s,name=%s>" % (self.id, self.name)


class UserProfile(Base):
    """
    堡垒机用户表关联主机用户和主机组
    """
    __tablename__ = 'user_profile'
    id = Column(Integer,primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    hostuser_list = relationship('HostUser',
                          secondary=UserProfile2HostUser,
                          backref='userprofiles')
    groups = relationship('Group',
                          secondary=UserProfile2Group,
                          backref='userprofiles')
    def __repr__(self):
        return "<id=%s,name=%s>" % (self.id, self.username)


class HostUser(Base):
    """
    主机用户表关联主机组和堡垒机用户，外键关联主机
    """
    __tablename__ = 'host_user'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('host.id'))
    AuthTypes = [
        (u'ssh-passwd', u'SSH/Password'),
        (u'ssh-key', u'SSH/KEY'),
    ]
    auth_type = Column(ChoiceType(AuthTypes))
    username = Column(String(64), nullable=False)
    password = Column(String(255))
    groups = relationship('Group',
                          secondary=HostUser2Group,
                          backref='hostuser_list')
    hosts = relationship("Host", backref="hostuser_list")

    __table_args__ = (UniqueConstraint('host_id', 'username', name='_host_username_uc'),)

    def __repr__(self):
        return "<host_id=%s,name=%s>" % (self.host_id, self.username)

class AuditLog(Base):
    """
    日志记录表外键关联用户
    """
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True)
    userprofile_id = Column(Integer, ForeignKey('user_profile.id'))
    hostuser_id = Column(Integer, ForeignKey('host_user.id'))
    action_choices = [
        (u'cmd', u'CMD'),
        (u'login', u'Login'),
        (u'logout', u'Logout'),
        (u'getfile', u'GetFile'),
        (u'sendfile', u'SendFile'),
        (u'exception', u'Exception'),
    ]
    action_type = Column(ChoiceType(action_choices))
    cmd = Column(String(255))
    date = Column(DateTime)
    user_profile = relationship("UserProfile")

engine = create_engine("mysql+pymysql://root@localhost:3306/test", echo=False)
Base.metadata.create_all(engine) #创建所有表结构

if __name__ == "__main__":
    SessionCls = sessionmaker(bind=engine) #创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
    session = SessionCls()

    #创建主机
    #h1 = Host(hostname='h1', ip_addr='192.168.1.86')
    #h2 = Host(hostname='h2', ip_addr='192.168.1.87')
    #h3 = Host(hostname='h3', ip_addr='192.168.1.88')

    #创建主机用户
    #r1 = HostUser(auth_type=u'ssh-passwd',username='work',password='123456',host_id="2")
    #r2 = HostUser(auth_type=u'ssh-key',username='root',host_id="2")
    #r3 = HostUser(auth_type=u'ssh-passwd',username='appmon',password='123456',host_id="3")

    #创建组
    #g1 = Group(name='g1')
    #g2 = Group(name='g2')
    #g3 = Group(name='g3')

    #session.add_all([h1,h2,h3])
    #session.add_all([r1, r2, r3])
    #session.add_all([g1,g2,g3])

    #查看主机下面的用户
    #obj = session.query(HostUser).join(HostUser.hosts).filter(Host.hostname == "h1").all()
    #print(obj)
    #session.commit()
    #host = "h1"
    #user = "root"
    #host_id = session.query(Host.id).filter(Host.hostname == host).first()[0]
    #hostuser_list = session.query(HostUser).join(HostUser.hosts).filter(HostUser.username == user, Host.id == host_id).first()
    #print(hostuser_list)
    #session.commit()

    #关联组和主机用户
    #h = session.query(HostUser).filter(HostUser.host_id == 2, HostUser.username == "root").first()
    #g2 = session.query(Group).filter(Group.name == "g1").first()
    #groups = session.query(Group).all()
    #h.groups = all_groups[0:1]
    #h.groups.append(g2)
    #session.commit()

    #查看组下面的主机用户
    #hostuser_list = session.query(HostUser).join(HostUser.groups).filter(Group.name == "g1").all()
    #print(hostuser_list)
    #session.commit()

    #创建堡垒机用户
    #u1 = UserProfile(username='alex', password='123456')
    #u2 = UserProfile(username='rain', password='abc!23')
    #session.add_all([u1, u2])
    #session.commit()

    #关联堡垒机用户和组
    #all_groups = session.query(Group).all()
    #g3 = session.query(Group).filter(Group.name == "g3").first()
    #u2 = session.query(UserProfile).filter(UserProfile.id == 2).first()
    #u.groups = all_groups[0:1]
    #u2.groups.append(g3)
    #session.commit()

    #查询堡垒机用户下关联的组
    #groups = session.query(Group.name).join(UserProfile.groups).all()
    #print(groups)
    #session.commit()

    #关联堡垒机用户和特定主机的主机用户
    #u = session.query(UserProfile).filter(UserProfile.id == 1).first()
    #hostuser = session.query(HostUser).filter(HostUser.host_id == 2, HostUser.username == "root").first()
    #u.hostuser_list.append(hostuser)
    #session.commit()

    #查看堡垒机下面关联的主机用户
    #host_list = session.query(HostUser).join(HostUser.userprofiles).filter(UserProfile.id == 1).all()
    #print(host_list)
    #session.commit()

