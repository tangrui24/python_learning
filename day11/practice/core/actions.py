import os,sys
Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)
import MyException
import views
from conf import settings
from conf import template

__command__ = ["start_session", "syncdb", "create_users", "create_groups", "create_hosts", "create_remoteusers", "help"]

def exec_cmd(userobj, argvs):
    """
    :param userobj:
    :param input_command:
    :return:
    """
    # 获取命令指令
    command = argvs[1]
    if not hasattr(views, command):
        raise MyException("106")
    else:
        # 调用对应的命令
        func = getattr(views, command)
        func(userobj, argvs[1:])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise MyException("106")
    else:
        exec_cmd("userobj", sys.argv)
