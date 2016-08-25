import shelve
import os,sys
import pickle
basic_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basic_dir)
from conf.settings import *

data ={
    'koka':{'pwd':"123456",
            'limit':10240000000,
            'homedir':'koka'},
    'akok':{'pwd':"123456",
            'limit':102400000,
            'homedir':'akok'}
}

def dump_data(data, file_path):
    # 把更改后的信息写入数据库文件
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)

def load_data(file_path):
    # 用于加载数据文件的数据并赋值给变量
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        return data

#初始化数据库
dump_data(data,user_data_file)