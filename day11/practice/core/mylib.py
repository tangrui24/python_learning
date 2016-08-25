import yaml
import time,sys,os,datetime
import hashlib

def yaml_parser(yml_filename):
    '''
    load yaml file and return
    :param yml_filename:
    :return:
    '''
    #yml_filename = "%s/%s.yml" % (settings.StateFileBaseDir,yml_filename)
    try:
        yaml_file = open(yml_filename,'r')
        data = yaml.load(yaml_file)
        return data
    except Exception as e:
        print(e)

def color_print(msg, color='red', exits=False):
    """
    Print colorful string.
    颜色打印字符或者退出
    """
    color_msg = {'blue': '\033[1;36m%s\033[0m',
                 'green': '\033[1;32m%s\033[0m',
                 'yellow': '\033[1;33m%s\033[0m',
                 'red': '\033[1;31m%s\033[0m',
                 'title': '\033[30;42m%s\033[0m',
                 'info': '\033[32m%s\033[0m'}
    msg = color_msg.get(color, 'red') % msg
    print(msg)
    if exits:
        time.sleep(2)
        sys.exit()
    return msg

def pagination(li, max_per_page, page = 1):
    '''
    列表分页
    :param li: 要分页的列表
    :param max_per_page: 每页多少多个元素
    :param page: 页码
    :return: page指定页的子列表及最多可以分多少页，如果页码不存在，返回空列表
    '''
    li_count = len(li) # 列表元素的数量
    page_div = divmod(li_count, max_per_page) #返回页数与剩余数
    max_page = page_div[0] if page_div[1] == 0 else page_div[0] + 1 # 计算需要多少页
    if page <= max_page:
        start = ((page - 1) * max_per_page)
        end = start + max_per_page
        return li[start:end], max_page
    else:
        return [], max_page

def process_bar(start, end, width = 50):
    str_num = "{:.2f}".format(start / end * 100)
    front = int(start * width / end)
    front_tag = "#" * front
    end_tag = " " * (width - front)
    tag = "{}{}".format(front_tag, end_tag)
    str_tag = "{:<7} [{}] {:,}\r".format(str_num, tag, end)
    sys.stdout.write(str_tag)
    sys.stdout.flush()
    #time.sleep(0.1)
    if len(str_tag) == width:
        sys.stdout.write('\n')
        sys.stdout.flush()

def MD5_encrypt(string):
    hash = hashlib.md5()
    hash.update(string.encode("utf8"))
    str_md5 = hash.hexdigest()
    return hash

def write_log(content):
    """
    写错误日志
    :param content: 日志信息
    :return: 无返回，写入文件 error.log
    """
    _content = "\n{0} : {1} ".format(datetime.now().strftime("%Y-%m-%d %X"), content)

def myljust(str1, width, fillchar = None):
    '''
    中英文混合左对齐
    :param str1: 欲对齐字符串
    :param width: 宽度
    :param fillchar: 填充字符串
    :return: 新的经过左对齐处理的字符串对象
    '''
    if fillchar == None:
        fillchar = ' '
    length = len(str1.encode('gb2312'))
    fill_char_size = width - length if width >= length else 0
    return "%s%s" %(str1, fillchar * fill_char_size)


def myrjust(str1, width, fillchar = None):
    '''
    中英文混合右对齐
    :param str1: 欲对齐字符串
    :param width: 宽度
    :param fillchar: 填充字符串
    :return: 新的经过右对齐处理的字符串对象
    '''
    if fillchar == None:
        fillchar = ' '
    length = len(str1.encode('gb2312'))
    fill_char_size = width - length if width >= length else 0
    return "%s%s" %(fillchar * fill_char_size, str1)

def mycenter(str1, width, fillchar = None):
    '''
    中英文混合居中对齐
    :param str1: 欲对齐字符串
    :param width: 宽度
    :param fillchar: 填充字符串
    :return: 新的经过居中对齐处理的字符串对象
    '''
    if fillchar == None:
        fillchar = ' '
    length = len(str1.encode('gb2312'))
    fill_char_size = width - length if width >= length else 0
    if length%2 == 0:
        return "%s%s%s" %(fillchar * (fill_char_size //2), str1, fillchar* (fill_char_size // 2))
    else:
        return "%s%s%s" %(fillchar * (fill_char_size //2 + 1), str1, fillchar* (fill_char_size // 2))
