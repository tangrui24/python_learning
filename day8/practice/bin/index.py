import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core import manager
from conf import settings
import optparse
if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-g", "--group", dest="group", help='group name', type="string")
    parser.add_option("-c", "--command", dest="cmd", help='commend', type="string")
    parser.add_option("-m", "--module", dest="module", help='module', type="string")
    parser.add_option("-s", "--src", dest="src", help='source file or path', type="string")
    parser.add_option("-d", "--dst", dest="dst", help='destination file or path', type="string")
    parser.add_option("-a", "--action", dest="action", help='action for module file, [get/put]', type="string")
    (option, arg) = parser.parse_args()
    if option.module == "shell":
        if option.cmd and option.group:
            if option.group in settings.GROUPS:
                hosts = settings.GROUPS[option.group]
                manager.multi_run(hosts, option.cmd, manager.run_cmd())
            else:
                print(settings.CODE_LIST["101"] % option.group)
        else:
            print(settings.CODE_LIST["103"])
    elif option.module == "file":
        # 必填项判断
        if option.action and option.group:
            if option.group in settings.GROUPS:
                if option.src and option.dst:
                    hosts = settings.GROUPS[option.group]
                else:
                    print(settings.CODE_LIST['106'], settings.CODE_LIST['107'] % (option.dst, option.src))
                    exit(1)
            else:
                print(settings.CODE_LIST["101"] % option.group)
                exit(1)
        else:
            print(settings.CODE_LIST["103"])
            exit(1)
        # 可变项 put or get
        if option.action == "put":
            if os.path.exists(option.src):
                manager.multi_run(hosts, [option.src, option.dst], manager.put_file)
            else:
                print(settings.CODE_LIST['107'] % option.src)
                exit()
        elif option.action == "get":
            if not os.path.isdir(option.dst):
                dst_path = os.path.abspath('.')
            else:
                dst_path = option.dst
            manager.multi_run(hosts, [option.src, dst_path], manager.get_file)
        else:
            print(settings.CODE_LIST['103'])
            exit()
    else:
        print(settings.CODE_LIST["105"] % option.module)
        exit()