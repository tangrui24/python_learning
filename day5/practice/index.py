from configs import settings
from public import login,loger
from shop.logic import user_main as shop_user_main
from atm.logic import user_main as atm_user_main
from manager import manager_user

if __name__ == "__main__":
    while True:
        print(""" 请选择以下操作项：
            1.ATM
            2.shop
            3.manager
            4.exit
        """)
        your_choice = input("请输入上述菜单中的选项，进入操作界面:")
        if your_choice == '1':
            loger.loger('ATM.var','localhost',settings.time_now,'-','info','entering ATM')
            atm_user_main.user_option()
        elif your_choice == '2':
            loger.loger('ATM.var','localhost',settings.time_now,'-','info','entering Mall')
            shop_user_main.go_shopping()
        elif your_choice == '3':
            loger.loger('ATM.var','localhost',settings.time_now,'-','info','entering Manager')
            manager_user.user_main()
        elif your_choice == '4':
            loger.loger('ATM.var','localhost',settings.time_now,'-','info','exit')
            break
        else:
            print("请输入正确的选项。")