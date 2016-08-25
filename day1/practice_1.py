# i = 0
# li = [1, 2, 3, 4, 5, 6, " ", 8, 9, 10]
# while i != len(li):
#     print(li[i])
#     i += 1

# sum = 0
# for i in range(1, 101):
#     sum += i
# print(sum)

# jisum = 0
# ousum = 0
# for i in range(1, 101):
#     if i % 2 != 0:
#         jisum += i
#     else:
#         ousum += i
# print(jisum-ousum)

# username = "tr"
# password = "123"
counter = 0
# while counter < 3:
#     name = input("username:")
#     passwd = input("password")
#     if name == username and passwd == password:
#         print("welcome to login")
#     else:
#         print("error login")
#         counter += 1
#         if (3-counter) != 0:
#             print("剩余%s次登录机会" % int(3-counter))

# db = [["tom", 123, 0, 0], ["jack", 123, 0, 0]]
#
# flag = False
# while not flag:
#     name = input("username:").strip()
#     if len(name) == 0:continue
#     passwd = input("password:").strip()
#     if passwd == 0:continue
#     for i in db:
#         if name == i[0] and i[-1] == 0:
#             username, password, counter, status = i
#             if name == username and passwd == password:
#                 print("welcome to login")
#                 flag = True
#             else:
#                 db[db.index(i)][2] += 1
#                 print(db)
#                 counter += 1
#                 if counter == 3:
#                     flag = True
#                 else:
#                     print("the user [%s] has %s time to try login" % (username, int(3-counter)))
#             break
#     else:
#         print("用户不存在")


def init():
    db = {
       "tom": {"password": "123", "counter": 0, "status": True},
       "jack": {"password": "123", "counter": 0, "status": True},
       "john": {"password": "123", "counter": 0, "status": True}
    }
    return db


def login():
    db = init()
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
            exit_flag = True
        else:
            if ret == None:
                print("the user is invalid")
            else:
                user_counter = counting(db, username)
                print(db)
                if user_counter >= 3:
                    lockuser(db, username)
                    print(db)
                    exit_flag = True
                    print("the user has locked")
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


def unlockuser(db,user):
    db[user]["status"] = True


def clearcounter(db, user):
    init()

if __name__ == "__main__":
    login()




