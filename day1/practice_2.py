import threading
def lookup(data):
    ret = []
    if isinstance(data, dict):
        for k, v in data.items():
            v = v.strip()
            if v.startswith("a") or v.startswith("A"):
                if v.endswith("c"):
                    ret.append(v)
    else:
        try:
            for v in data:
                v = v.strip()
                if v.startswith("a") or v.startswith("A"):
                    if v.endswith("c"):
                        ret.append(v)
        except Exception as e:
            print(e)
    print(ret)

if __name__ == "__main__":
    li = ["alec", " aric", "Alex", "Tony", "rain"]
    tu = ("alec", " aric", "Alex", "Tony", "rain")
    dic = {'k1': "alex", 'k2': ' aric',  "k3": "Alex", "k4": "Tony"}
    j = []
#   lookup(dic)
    a = [li, tu, dic]
    for i in a:
        t = threading.Thread(target=lookup, args=(i,))
        t.start()
        j.append(t)
    for k in j:
        k.join()

# def init():
#     import collections
#     li = ["手机", "电脑", '鼠标垫', '游艇']
#     dic = collections.OrderedDict()
#     for k, v in enumerate(li, 1):
#         dic[str(k)] = v
#     return dic
#
# def show():
#     shop_goods = init()
#     print("买买买")
#     print(shop_goods)
#     return shop_goods
#
# def shop(dic):
#     choice = input("你买啥呢:")
#     if choice in dic:
#         print(dic[choice])
#     else:
#         print("没得")
#
# if __name__ == "__main__":
#     goods = show()
#     shop(goods)

from day1 import citylist
import sys

def init():
    area = {}
    province = {}
    city = {}
    for i, a in enumerate(citylist.CityList, 1):
        area[i] = a
        province.setdefault(a, {})
        for i, p in enumerate(citylist.CityList[a].keys(), 1):
            province[a].setdefault(i, p)
            city.setdefault(p, {})
            for i, c in enumerate(citylist.CityList[a][p], 1):
                city[p].setdefault(i, c)
    print(area)
    print(province)
    print(city)
    return area, province, city

def show():
    print("welcome to China map".center(40, "*"))
    area, province, city = init()
    exit_flag = True
    while exit_flag:
        for i, a in area.items():
            print(i, a)
        ret = user_choice(area)
        if ret:
            print("your choice:", area[ret])
            for i, p in province[area[ret]].items():
                print(i, p)
            ret = user_choice(province, area[ret])
            if ret:
                print("your choice:", ret)
                for i, c in city[ret].items():
                    print(i, c)
                ret = user_choice(city, ret)
                if ret:
                    print("your choice:", ret)
                    exit_flag = False

def user_choice(data,area=None):
    try:
        choice = input("lookup：").strip()
        if int(choice) not in data:
            if int(choice) not in data.get(area, None):
                return False
            else:
                return data[area][int(choice)]
        else:
            return int(choice)
    except ValueError:
        if choice == "b":
            return "back"
        elif choice == "q":
            sys.exit("欢迎下次使用")
        print("input inter num")
    except TypeError:
        return False

if __name__ == "__main__":
    show()