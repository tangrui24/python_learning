import pickle
def load_file(file_path):
    # 用于加载数据文件的数据并赋值给变量
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        return data