import os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from public import dump_file
from configs import settings

dump_file.dump_file(settings.atm_user,settings.atm_user_file_path)
dump_file.dump_file(settings.shop_user,settings.shop_user_file_path)
dump_file.dump_file(settings.manager_user,settings.manager_user_file_path)

