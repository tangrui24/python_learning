import os,sys,time
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)
from configs import settings
from public import dump_file,login,loger
import datetime

#取款还款转账
def transact_amount(account,tran_type):
    if tran_type == 1:
        withdraw = int(input("取钱：").strip())
        user_balance = int(settings.atm_user_data[account]['balance'])
        if withdraw > user_balance:
            print("余额：{0}".format(user_balance))
            print("余额不足，请充值：")
            loger.loger('ATM.var',account,settings.time_now,'-','error','withdraw Balance Insufficient')
        else:
            settings.atm_user_data[account]['balance'] = int(user_balance - (withdraw*1.05))
            dump_file.dump_file(settings.atm_user_data, settings.atm_user_file_path)
            loger.loger(account,account,settings.time_now,'withdraw',"-"+str(withdraw),withdraw*0.05)
            loger.loger('ATM.var',account,settings.time_now,'-','info','withdraw'+"-"+str(withdraw))
    elif tran_type == 2:
        repay = int(input("还款：").strip())
        user_balance = int(settings.atm_user_data[account]['balance'])
        settings.atm_user_data[account]['balance'] = int(user_balance + repay)
        dump_file.dump_file(settings.atm_user_data, settings.atm_user_file_path)
        loger.loger(account,account,settings.time_now,'repay',"+"+str(repay))
        loger.loger('ATM.var',account,settings.time_now,'-','info','repay'+"+"+str(repay))
    elif tran_type == 3:
        transfer = input("转入帐号").strip()
        if transfer in settings.atm_user_data:
            trans_money = int(input("转入金额").strip())
            user_balance = int(settings.atm_user_data[account]['balance'])
            if trans_money > user_balance:
                print("余额：{0}".format(user_balance))
                print("余额不足，请充值：")
                loger.loger('ATM.var',account,settings.time_now,'-','error','transfer Balance Insufficient')
            else:
                transfer_balance = int(settings.atm_user_data[transfer]['balance'])
                withdraw_balance = int(settings.atm_user_data[account]['balance'])
                if  settings.atm_user_data[transfer] == settings.atm_user_data[account]:
                    print("**********转账人与收账人不能相同**********")
                    loger.loger('ATM.var',account,settings.time_now,'-','error','Transfer and accounts can not be the same')
                else:
                    settings.atm_user_data[transfer]['balance'] = int(user_balance + trans_money)
                    settings.atm_user_data[account]['balance'] = int(user_balance - trans_money)
                    dump_file.dump_file(settings.atm_user_data, settings.atm_user_file_path)
                    loger.loger(account,account,settings.time_now,'transfer',"-"+str(trans_money))
                    loger.loger(transfer,transfer,settings.time_now,'transfer',"+"+str(trans_money))
                    loger.loger('ATM.var',account,settings.time_now,'-','info','transfer'+"-"+str(trans_money))
                    loger.loger('ATM.var',transfer,settings.time_now,'-','info','transfer'+"-"+str(trans_money))
        else:
            print("转入帐号不存在")
            loger.loger('ATM.var',account,settings.time_now,'-','error','transfer account nonexistent')

def audit_account(username):
    if os.path.exists(os.path.join(settings.log_dir_path,username)):
        with open(os.path.join(settings.log_dir_path,username),'r') as files:
            accountinfo_list = files.readlines()
        total = 0
        print("{0} {1} {2} {3} {4}".format( "帐号".ljust(3), "时间".center(16),"操作".center(2),"金额".rjust(3),"利息".rjust(3)))
        for i in accountinfo_list:
            line = i.strip().split()
            new = line[1].split('-')
            if username  == line[0] and new[1] == str(datetime.date.today()).split('-')[1]:
                print(' '.join(line))
                consume = int(line[4])
                total += consume
        print("*" * 50)
        print("当月消费金额合计：{0}".format(total))
        loger.loger('ATM.var',username,settings.time_now,'-',"info",'audit_account')
    else:
        print("该用户%s当前没有生成账单记录" %username)
        loger.loger('ATM.var',username,settings.time_now,'-','error','The user currently has no billing record')


