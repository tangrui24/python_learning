import pickle
def dump_file(data, file_path):
    # 把更改后的信息写入数据库文件
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)