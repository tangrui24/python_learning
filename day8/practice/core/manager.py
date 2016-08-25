import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings
import paramiko
import optparse
from  multiprocessing import Process,Pool,freeze_support
import time
import logging


def run_cmd(host, command):
    ssh = get_ssh(host)
    stdin, stdout, stderr = ssh.exec_common(command)
    stdout_msg = stdout.read().decode()
    stderr_msg = stderr.read().decode()
    print("[%s] : [%s]" % (host['hostname'], command))
    if not stderr_msg:
        msg = 'info|[%s] : [%s] is successful' % (host['hostname'], command)
        print(stdout_msg)
    else:
        msg = 'error|[%s] : [%s] is fail [%s]' % (host['hostname'], command, stderr_msg)
        print(stderr_msg)
    return msg


def put_file(host, arg):
    src = arg[0]
    dst = arg[1]
    dst_file = os.path.join(dst, os.path.basename(src))
    t, sftp = get_sftp(host)
    try:
        sftp.put(src, dst_file)
        t.close()
        success_info = 'put file %s to %s is successful' % (arg[0], dst_file,)
        msg = 'info|[%s] : %s' % (host['hostname'], success_info)
        print(success_info)
    except Exception as e:
        error_info = e
        t.close()
        print(error_info)
        msg = 'error|[%s] : put file %s is fail [%s]' % (host['hostname'], arg[0], error_info)
    return msg


def get_file(host, arg):
    src_file = arg[0]
    dst_dir = arg[1]
    try:
        dst_path = os.path.join("%s, %s/%s" % (dst_dir, time.strftime("%Y%m%d%H%M%S", time.localtime()), host['hostname']))
        os.mkdir(dst_path)
        dst_file = os.path.join(dst_path, os.path.basename(src_file))
    except Exception as e:
        error_info = e
        print(error_info)
        msg = 'error|[%s] : get file %s is fail [%s]' % (host['hostname'], arg[0], error_info)
        return msg
    ssh = get_ssh(host)
    stdin, stdout, stderr = ssh.exec_common("ls -l %s" % src_file)
    if not stderr:
        t, sftp = get_sftp(host)
        try:
            sftp.get(src_file, dst_file)
            t.close()
            success_info = 'get file %s to %s is successful' % (src_file, dst_file,)
            msg = 'info|[%s] : %s' % (host['hostname'], success_info)
            print(success_info)
        except Exception as e:
            error_info = e
            t.close()
            print(error_info)
            msg = 'error|[%s] : get file %s is fail [%s]' % (host['hostname'], arg[0], error_info)
    else:
        error_info = stderr.read().decode()
        print(error_info)
        msg = 'error|[%s] : get file %s is fail [%s]' % (host['hostname'], arg[0], error_info)
    return msg


def get_ssh(host):
    if "password" in host.keys():
        transport = paramiko.Transport((host['hostname'], host['port']))
        transport.connect(username=host['username'], password=host['password'])
        ssh = paramiko.SSHClient()
        ssh._transport = transport
    else:
        private_key = paramiko.RSAKey.from_private_key_file(host['pkey'])
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host['hostname'], port=host['port'], username=host['usrename'], pkey=private_key)
    return ssh


def get_sftp(host):
    if "password" in host.keys():
        t = paramiko.Transport((host["hostname"], 22))
        t.connect(username=host["username"], password=host["password"])
        sftp = paramiko.SFTPClient.from_transport(t)
    else:
        pravie_key_path = host["pkey"]
        key = paramiko.RSAKey.from_private_key_file(pravie_key_path)
        t = paramiko.Transport((host["hostname"], 22))
        t.connect(username=host["username"], pkey=key)
        sftp = paramiko.SFTPClient.from_transport(t)
    return t, sftp


def multi_run(hosts, arg, func):
    """
    :param hosts:  主机列表
    :param arg:   命令或者是src，dst
    :param func:  执行函数
    :return:
    """
    freeze_support()
    pool = Pool(5)
    for host in hosts:
        host_obj = settings.HOSTS[host]
        pool.apply_async(func=func, args=(host_obj, arg), callback=write_log)
    pool.close()
    pool.join()  # 进程池中进程执行完毕后再关闭，如果注释，那么程序直接关闭。


def write_log(msg):
    level, msg = msg.split('|')  # 由于只能有一个参数，所以都是用|分割日志级别及正文
    import logging
    file_handler = logging.FileHandler(settings.LOG_FILE, "a", encoding="UTF-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s", '%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    try:
        if level == 'info':  # 根据不同的日志级别输出日志
            root_logger.info(msg)
        elif level == 'error':
            print(level)
            root_logger.error(msg)
    except IOError as e:
        print(e)


def main():
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
                multi_run(hosts, option.cmd, run_cmd)
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
                    exit()
            else:
                print(settings.CODE_LIST["101"] % option.group)
                exit()
        else:
            print(settings.CODE_LIST["103"])
            exit()
        # 可变项 put or get
        if option.action == "put":
            if os.path.exists(option.src):
                multi_run(hosts, [option.src, option.dst], put_file)
            else:
                print(settings.CODE_LIST['107'] % option.src)
                exit()
        elif option.action == "get":
            if not os.path.isdir(option.dst):
                dst_path = os.path.abspath('.')
            else:
                dst_path = option.dst
            multi_run(hosts, [option.src, dst_path], get_file)
        else:
            print(settings.CODE_LIST['103'])
            exit()
    else:
        print(settings.CODE_LIST["105"] % option.module)
        exit()