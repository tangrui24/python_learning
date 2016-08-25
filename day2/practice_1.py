import sys
db = {
    "admin": {"password": "123", "money": 0, "identify": 0, "counter": 0, "status": True},
    "jack": {"password": "123", "money": 10000, "identify": 1, "counter": 0, "status": True},
    "tom": {"password": "123", "money": 15000, "identify": 1, "counter": 0, "status": True}
}

goods = [
    {"name": "电脑", "price": 1999},
    {"name": "鼠标", "price": 10},
    {"name": "游艇", "price": 20},
    {"name": "美女", "price": 998},
]

goods_list = []
login_status = {"user": None, "user_login": False}


def check_login(func):
    def wrapper(*args, **kwargs):
        if not login_status["user_login"]:
            ret = login()
            if ret:
                return func(ret, *args, **kwargs)
            else:
                return False
        else:
            return func(login_status["user"], *args, **kwargs)
    return wrapper


def login():
    exit_flag = False
    while not exit_flag:
        username = input("username:").strip()
        if username == 0:
            continue
        password = input("password:").strip()
        if password == 0:
            continue
        ret = auth(db, username, password)
        if ret:
            print("welcome to login")
            login_status["user"] = username
            login_status["user_login"] = True
            return username
        else:
            if not ret:
                print("the user is invalid")
            else:
                user_counter = counting(db, username)
                if user_counter >= 3:
                    lockuser(db, username)
                    print("the user has locked")
                    return False
                else:
                    print("user or password error!")


def auth(db, user, password):
    if user in db and password == db[user]["password"]:
        flag = True
    elif user in db and password != db[user]["password"]:
        flag = False
    else:
        flag = None
    return flag


def counting(db, user):
    db[user]["counter"] += 1
    return db[user]["counter"]


def lockuser(db,user):
    db[user]["status"] = False


def shop_list():
    width = 105
    price_width = 50
    item_width = width - price_width*2
    header_format = '%-*s%*s%*s'
    format = '%-*s%*s%*d'
    shoplist = {}
    print("Shopping List:".center(width, "#"))
    print(''.ljust(105, '='))
    print(header_format % (item_width, 'ID', price_width-1, 'Item', price_width, 'Price'))
    print(''.ljust(105, '='))
    for i, z in enumerate(goods, 1):
        print(format % (item_width, i, price_width-3, z["name"], price_width, z["price"]))
        shoplist[i] = z
    print(''.ljust(105, '='))
    return shoplist


@check_login
def shopping(user):
    # user = login_status["user"]
    while True:
        money = db[user]["money"]
        shop_lists = shop_list()
        F_choice = input("Enter the products of \033[1mID\033[0m  you want buy something:").strip()
        if len(F_choice) == 0:continue
        elif F_choice == 'quit':
            sys.exit("you have bought these things: %s" % ''.join(goods_list))
        elif int(F_choice) in shop_lists:  # 商品是否包含
            F_choice = int(F_choice)
            prices = shop_lists[F_choice]["price"]
            if money >= prices:  # 金额是否大于商品价格
                print('added \033[1;32;0m[%s]\033[0m your shop_list' % shop_lists[F_choice]["name"])
                goods_list.append(shop_lists[F_choice]["name"])  # 添加购物车
                user_choice(prices)
                # print("current balance:\033[1;31;0m ￥%s\033[0m" % money)
                print('you have bought things:\033[1;34;0m%s\033[0m' % goods_list)
            else:  # 金额不足，继续购物
                print("\033[1;31;40m sorry,you can't buy it,please buy others\033[0m")
                print("current balance: \033[1;31;0m ￥%s\033[0m" % money)
                print('you have bought things:\033[1;34;0m%s\033[0m' % goods_list)
                user_choice(prices)

        else:  # 商品不在购物菜单，请输入正确的商品编号
            print("请输入正确的商品标号，或者输入quit退出程序")
            continue


@check_login
def recharge(user):
    # user = login_status["user"]
    try:
        recharge_money = int(input("充值金额：").strip())
        db[user]["money"] += recharge_money
        print(db[user]["money"])
    except Exception as e:
        print(e)


@check_login
def paymoney(user, price):
    # user = login_status["user"]
    if db[user]["money"] >= price:
        db[user]["money"] -= price  # 扣除商品价格
        return True
    else:
        recharge()


@check_login
def user_choice(user, price):
    choice = {"1": recharge,
              "2": shopping,
              "3": paymoney,
              }
    select = input("充值请输入1，继续购物输入2，结算输入3:").strip()
    if select in choice:
        if select == "3":
            # print("执行的paymoney")
            choice["3"](price)
        else:
            # print("执行的其他")
            choice[select]()
    else:
        choice["2"]()

if __name__ == "__main__":
    shopping()
