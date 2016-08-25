import os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)
from configs import settings
from atm.logic import handles
from public import login,loger

@login.fiter(settings.atm_user_data,settings.atm_user_file_path)
def user_option(username):
    while True:
        print("""请选择以下选项进行操作：
        1.取款
        2.还款
        3.转账
        4.查看账单
        5.退出
    """)
        try:
            user_choice = int(input('请输入你的操作项：').strip())
            if user_choice == 1:
                handles.transact_amount(username,user_choice)
            elif user_choice == 2:
                handles.transact_amount(username,user_choice)
            elif user_choice == 3:
                handles.transact_amount(username,user_choice)
            elif user_choice == 4:
                handles.audit_account(username)
            elif user_choice == 5:
                loger.loger('ATM.var','root',settings.time_now,'-','info','Exit ATM')
                break
        except ValueError:
            print("请输入正确的操作项")

