import os,json


def search_backends(backend):
    backends = "backend %s" % backend
    backend_flag = False
    record = []
    with open("ha.conf") as read_ret:
        for line in read_ret:
            if line.strip() == backends:
                backend_flag = True
            elif line.strip().startswith("backend"):
                backend_flag = False
            elif backend_flag and line.strip():
                record.append(line.strip())
    return record


def add_backends(dic):
    title = "backend %s" % dic.get("backend")
    record = "server %(server)s %(server)s weight %(weight)s maxconn %(maxconn)s" % dic.get('record')
    ret = search_backends(dic.get("backend"))
    if ret:
        if record not in ret:
            ret.append(record)
        else:
            print("记录已经存在")
            return
        backend_flag = False
        write_flag = False
        with open("ha.conf") as read_ret, open("ha.conf.new", "w") as write_ret:
            for line in read_ret:
                if line.strip() == title:
                    backend_flag = True
                    write_ret.write(line)
                elif line.strip().startswith("backend"):
                    backend_flag = False
                elif backend_flag and line.strip():
                    if not write_flag:
                        for item in ret:
                            temp = "\t%s\n".expandtabs(tabsize=8) % item
                            write_ret.write(temp)
                        write_flag = True
                else:
                    write_ret.write(line)
    else:
        with open("ha.conf") as read_ret, open("ha.conf.new", "w") as write_ret:
            for line in read_ret:
                write_ret.write(line)
            write_ret.write("\n"+title+"\n")
            temp = "\t%s\n".expandtabs(tabsize=8) % record
            write_ret.write(temp)
    os.rename("ha.conf", "ha.conf.bak")
    os.rename("ha.conf.new", "ha.conf")


def del_backends(dic):
    title = "backend %s" % dic.get("backend")
    record = "server %(server)s %(server)s weight %(weight)s maxconn %(maxconn)s" % dic.get('record')
    ret = search_backends(dic.get("backend"))
    if ret:
        if record not in ret:
            print("没有这条记录")
            return
        else:
            del ret[ret.index(record)]
            if not ret:
                print("删除节点[%s],删除记录[%s]" % (title, record))
            else:
                print("删除记录[%s]" % record)
                ret.insert(0, title)
        backend_flag = False
        write_flag = False
        with open("ha.conf") as read_ret, open("ha.conf.new", "w") as write_ret:
            for line in read_ret:
                if line.strip() == title:
                    backend_flag = True
                elif line.strip().startswith("backend"):
                    backend_flag = False
                elif backend_flag and ret:
                    if not write_flag:
                        for line in ret:
                            if line.strip().startswith("backend"):
                                write_ret.write(line+"\n")
                            else:
                                temp = "\t%s\n".expandtabs(tabsize=8) % line
                                write_ret.write(temp)
                        write_flag = True
                else:
                    write_ret.write(line)
    else:
        return
    os.rename("ha.conf", "ha.conf.bak")
    os.rename("ha.conf.new", "ha.conf")


def check():
    import re
    while True:
        s = input('>>>eg:{"backend": "test.oldboy.org","record":{"server": "100.1.7.999","weight": 20,"maxconn": 30}}')
        if len(s) == 0:continue
        elif s == 'back':break
        elif s.isdigit():print("你输入的格式错误")
        else:
            try:
                dic = json.loads(s)
                return dic
            except Exception as e:
                print("你输入的格式错误", e)
                return s

if __name__ == "__main__":
    while True:
        print('''please choose below options to proceed:
        1.查询ha记录
        2.添加ha记录
        3.删除ha记录
        4.退出程序
        ''')
        choice = {1: search_backends,
                  2: add_backends,
                  3: del_backends,
                  4: exit,
                  }
        # 判断用户必须输入一个整数
        try:
            option = int(input('..>').strip())
        except ValueError:
            print('only inter can acceed')
            continue
        if option in choice:
            if option == 1:
                domain = input('>>>"test.oldboy.org">>>').strip()
                ret = search_backends(domain)
                if ret:
                    for i, v in enumerate(ret, 1):
                        print(i, v.strip())
                        continue
                else:
                    print("未找到记录")
                    continue
            else:
                ret = check()
                choice[option](ret)
        else:
            print("无效")
        # if option == 1:
        #     # 此处不能使用上面的user_input,需要用户输入一个单独的节点名
        #     downmain = input('>>>"test.oldboy.org">>>').strip()
        #     ret = search_backends(downmain)
        #     if ret:
        #         for i, v in enumerate(ret, 1):
        #             print(i, v.strip())
        #     else:
        #         print("未找到记录")
        #         continue
        # elif option == 2:
        #     # 用户输入一个字典形似的字符串
        #     d = main()
        #     # 查找节点信息
        #     add_backends(d)
        # elif option == 3:
        #     # 用户输入一个字典形似的字符串
        #     d = main()
        #     # 调用删除
        #     del_backends(d)
        # elif option == 4:
        #     break