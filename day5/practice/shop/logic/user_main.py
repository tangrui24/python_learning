import os,sys,collections
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)
from configs import settings
from public import login,dump_file,loger

def print_shop_menu(username,products):
    #格式化购物菜单
    width = 105
    price_width = 50
    item_width = width - price_width*2
    header_format = '%-*s%*s%*s'
    format = '%-*s%*s%*d'
    print("Welcome \033[1;32;0m[%s]\033[0m  to ATM Mall ".rjust(115,"=") %username)
    print(" Shopping List: ".center(width,"*"))
    print(''.ljust(105,'='))
    print(header_format % (item_width,'ID',price_width,'Item',price_width,'Price'))
    print(''.ljust(105,'='))
    #重新生成一个带商品ID的字典
    d = collections.OrderedDict()
    for i,z in enumerate(products.items(),1):
        d[str(i)] = z
        print(format % (item_width,i,price_width,z[0],price_width,z[1]))
    print(''.ljust(105,'='))
    return d

def print_shopping_cart(arg):
    global total
    # 打印购物车内的商品信息调用的模块
    total = 0
    print("{0}{1}".format( "商品名称".center(20), "价格".rjust(20),))
    for i in arg:
        print(str(arg.index(i) + 1).ljust(3) + i[0].center(17) + str(i[1]).rjust(25))
        goods_total = int(i[1])
        total += goods_total
    print("*" * 60)
    print("金额合计：{0}".format(total))
    return total

@login.fiter(settings.shop_user_data,settings.shop_user_file_path)
def go_shopping(username):
    # 用户选择开始购物时调用的模块
    bool_value = True
    while bool_value:
        ret = print_shop_menu(username,settings.goods_data)
        F_choice = input("请输入想要购买的商品编号:".ljust(20))
        if len(F_choice) == 0: #输入为空继续输入
            continue
        elif F_choice in ret: #商品是否包含
            buy_goods_name = ret[F_choice][0]
            buy_goods_price = int(ret[F_choice][1])
            settings.shopping_cart.append([buy_goods_name,buy_goods_price])
            print("购物车内已选购物品")
            print_shopping_cart(settings.shopping_cart)
            user_choice = input("非关键字的任意键:返回上一级\tq:退出购物车并结账\tc：更改购物车\t\t  :")
            if user_choice == 'q':
                bool_value = False
                settlement()
            elif user_choice == 'c':
                bool_value = False
                change_shopping_cart(settings.shopping_cart)
            else:
                continue
        else:#商品不在购物菜单，请输入正确的商品编号
            print("请输入正确的商品标号")
            continue

def change_shopping_cart(shopping_cart):
    # 购物车内商品操作入口
    bool_value = True
    while bool_value:
        print_shopping_cart(shopping_cart)
        user_choice = input("d：删除商品\tq:退出，结账！")
        if user_choice == 'd':
            del_shopping_cart(settings.shopping_cart)
            if len(shopping_cart) == 0:
                bool_value = False
                print("购物车已空")
        elif user_choice == 'q':
            bool_value = False
            settlement()
        else:
            print("请根据提示输入正确的选项！")

def del_shopping_cart(data_list):
    # 删除模块
    goods_id = input("请输入要删除商品的ID：")
    if len(data_list) != 0:
        del data_list[int(goods_id)-1]

@login.fiter(settings.atm_user_data,settings.atm_user_file_path)
def settlement(username):
    # 结算时调用的接口
    bool_value = True
    while bool_value:
        #total = print_shopping_cart(settings.shopping_cart)
        user_balance = int(settings.atm_user_data[username]['balance'])
        if total > user_balance:
            print("余额：{0}".format(user_balance))
            print("余额不足，请充值：")
            bool_value = False
        else:
            print("购物成功")
            settings.atm_user_data[username]['balance'] = int(user_balance - total)
            bool_value = False
            dump_file.dump_file(settings.atm_user_data, settings.atm_user_file_path)
            #print(settings.shopping_cart)
            for i in settings.shopping_cart:
                loger.loger(username,username,settings.time_now,i[0],"-"+str(i[1]))
                loger.loger('ATM.var',username,settings.time_now,"-","info",'buy '+i[0])
        loger.loger('ATM.var',username,settings.time_now,'-','info','Exit MALL')
        settings.shopping_cart.clear()

