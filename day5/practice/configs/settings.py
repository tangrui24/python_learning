import os,sys,time
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from public import load_file,dump_file

atm_user = {
	'001':{'pwd':'12345678','try_times':0,'credit':15000,'balance':15000},
	'002':{'pwd':'12345678','try_times':0,'credit':15000,'balance':15000}
}

shop_user = {
    'haha':{'pwd':'12345678','try_times':0},
    'hehe':{'pwd':'12345678','try_times':0}
}

manager_user = {
    'root':{'pwd':'12345678','try_times':0},
}

products = {
    'Iphone':4988,
    'Coffee':35,
    'notebooks':6666,
    'clothers':300,
    'Bicyle':800,
    'package':120,
    'fruit':10,
    'paper':1
}

shopping_cart = []
log_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),r'atm\log')
time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
atm_user_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r'atm\db\user.db')
shop_user_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r'shop\db\user.db')
goods_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r'shop\db\goods.db')
manager_user_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r'manager\db\user.db')
atm_user_data = load_file.load_file(atm_user_file_path)
shop_user_data =  load_file.load_file(shop_user_file_path)
goods_data = load_file.load_file(goods_file_path)
manager_user_data = load_file.load_file(manager_user_file_path)
print(log_dir_path)
print(os.stat(log_dir_path).st_size)





