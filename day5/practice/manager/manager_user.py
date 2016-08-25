import os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from configs import settings
from public import dump_file,login,loger

def check_user_select():
    try:
        select = int(input("""请选择用户类型：
            1.shop 用户
            2.atm 用户
            3.退出
        输入你的选择：""").strip())
        if select == 1:
            return select
        elif select == 2:
            return select
        elif select == 3:
            return False
    except ValueError:
        print('\033[1;31;0m请选择输入1或2\033[0m')

def add_user(user_type,userinfo,user_path,try_times=0,credit=None,balance=None):
    break_flag = True
    while break_flag:
        new_user = input("请输入新用户名称：").strip()
        if len(new_user) == 0:
            continue
        if new_user in userinfo:
            print("用户名{0}已经存在，请重新输入！".format(new_user))
        else:
            new_user_login_pwd = input("请输入新用户密码：")
            if len(new_user_login_pwd) == 0:continue
            confirm_new_user_login_pwd = input("请再次新用户输入密码：")
            if len(confirm_new_user_login_pwd) == 0:continue
            if new_user_login_pwd == confirm_new_user_login_pwd:
                if user_type == 1:
                    userinfo[new_user]={"pwd":new_user_login_pwd,"try_times":0}
                    loger.loger('ATM.var','root',settings.time_now,'-','info',"add_shop_user:%s"%new_user)
                    break_flag = False
                elif user_type == 2:
                    credit = int(input("请输入新用户额度：").strip())
                    userinfo[new_user]={"pwd":new_user_login_pwd,"try_times":0,'credit':credit,'balance':credit}
                    loger.loger('ATM.var','root',settings.time_now,'-','info',"add_atm_user:%s"%new_user)
                    break_flag = False
                print("用户%s添加成功" %new_user)
                dump_file.dump_file(userinfo,user_path)
            else:
                print("两次输入登录密码不一致，请重新输入")

def del_user(userinfo,user_path):
    while True:
        user = input("请输入用户名:").strip()
        if user in userinfo:
            if len(userinfo)> 1:
                del userinfo[user]
                print("用户%s已删除" %user)
                dump_file.dump_file(userinfo,user_path)
                loger.loger('ATM.var','root',settings.time_now,'-','warning',"del_user:%s"%user)
                return True
            else:
                print("没有更多的用户可删除")
        else:
             print("查无此用户,请重新输入")

def search_user(user_type,userinfo,user_path):
    user = input("请输入用户名:").strip()
    if user in userinfo:
        if user_type == 1:
            print("用户名：%s\n密码：%s\n登录次数：%s\n" %(user,userinfo[user]['pwd'],userinfo[user]['try_times']))
            loger.loger('ATM.var','root',settings.time_now,'-','info',"search_shop_user:%s"%user)
        elif user_type == 2:
            print("用户名：%s\n密码：%s\n登录次数：%s\n信用额度：%s\n余额：%s" %(user,userinfo[user]['pwd'],userinfo[user]['try_times'],userinfo[user]['credit'],userinfo[user]['balance']))
            loger.loger('ATM.var','root',settings.time_now,'-','info',"search_atm_user:%s"%user)
    else:
        print("查无此用户,请重新输入")

def lock_user(userinfo,user_path):
    while True:
        user = input("请输入用户名:").strip()
        if user in userinfo:
            userinfo[user]['try_times']=3
            print("用户%s已锁定" %user)
            dump_file.dump_file(userinfo,user_path)
            loger.loger('ATM.var','root',settings.time_now,'-','warning',"lock_user:%s"%user)
            return True
        else:
            print("查无此用户,请重新输入")

def unlock_user(userinfo,user_path):
    while True:
        user = input("请输入用户名:").strip()
        if user in userinfo:
            userinfo[user]['try_times']=0
            print("用户%s已解锁" %user)
            dump_file.dump_file(userinfo,user_path)
            loger.loger('ATM.var','root',settings.time_now,'-','warning',"unlock_user:%s"%user)
            return True
        else:
            print("查无此用户,请重新输入")

def change_pwd(userinfo,user_path):
    while True:
        user=input("请输入用户：").strip()
        if user in userinfo:
            old_pwd = input("请输入旧密码：").strip()
            if old_pwd ==userinfo[user]['pwd']:
                new_pwd = input("请输入新密码：").strip()
                confirm_pwd = input("请再输入一遍新密码：").strip()
                if new_pwd == confirm_pwd:
                    userinfo[user]['pwd'] = new_pwd
                    print("密码修改成功！")
                    dump_file.dump_file(userinfo,user_path)
                    loger.loger('ATM.var','root',settings.time_now,'-','warning',"chang_user_pwd:%s"%user)
                    return True
                else:
                    print("新密码前后输入不一致！请重新输入！")
            else:
                print("旧密码错误，请重新输入！")
        else:
            print("查无此用户,请重新输入")

def chang_creadit(userinfo,user_path):
    while True:
        user = input("请输入用户名:").strip()
        if user in userinfo:
            credit = input("请输入用户额度:").strip()
            userinfo[user]['credit']=credit
            print("用户%s额度已经调整" %user)
            dump_file.dump_file(userinfo,user_path)
            loger.loger('ATM.var','root',settings.time_now,'-','warning',"chang_atm_user_credit:%s"%user)
            return True
        else:
            print("查无此用户")

def audit_atm_record(log_file_path='ATM.var'):
    with open(os.path.join(settings.log_dir_path,log_file_path),'r') as files:
        atm_info_list = files.readlines()
    for i in atm_info_list:
        line = i.strip().split()
        print(' '.join(line))
    loger.loger('ATM.var','root',settings.time_now,'-','info','audit_atm_record')

@login.fiter(settings.manager_user_data,settings.manager_user_file_path)
def user_main(username):
    while True:
        print(""" 请选择以下操作项：  欢迎超级管理员\033[0;32;0m[%s]\033[0m登录
            1.修改用户密码
            2.添加用户
            3.锁定用户
            4.解锁用户
            5.查看用户信息
            6.删除用户
            7.修改用户信用额度
            8.查看ATM操作记录
            9.退出
        """ %username)
        try:
            your_choice = int(input("请输入上述菜单中的选项，进入操作界面:").strip())
            if your_choice == 1:
                ret = check_user_select()
                if ret == 1:
                    change_pwd(settings.shop_user_data,settings.shop_user_file_path)
                elif ret ==2:
                    change_pwd(settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 2:
                ret = check_user_select()
                if ret == 1:
                    add_user(ret,settings.shop_user_data,settings.shop_user_file_path)
                elif ret == 2:
                    add_user(ret,settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 3:
                ret = check_user_select()
                if ret == 1:
                    lock_user(settings.shop_user_data,settings.shop_user_file_path)
                elif ret ==2:
                    lock_user(settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 4:
                ret = check_user_select()
                if ret == 1:
                    unlock_user(settings.shop_user_data,settings.shop_user_file_path)
                elif ret ==2:
                    unlock_user(settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 5:
                ret = check_user_select()
                if ret == 1:
                    search_user(ret,settings.shop_user_data,settings.shop_user_file_path)
                elif ret ==2:
                    search_user(ret,settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 6:
                ret = check_user_select()
                if ret == 1:
                    del_user(settings.shop_user_data,settings.shop_user_file_path)
                elif ret ==2:
                    del_user(settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 7:
                chang_creadit(settings.atm_user_data,settings.atm_user_file_path)
            elif your_choice == 8:
                audit_atm_record()
            elif your_choice == 9:
                loger.loger('ATM.var','root',settings.time_now,'-','info','Exit Manager')
                break
        except ValueError:
            print("请输入以上一个操作项：")
