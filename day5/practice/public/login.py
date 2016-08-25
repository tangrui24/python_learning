import os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from public import load_file,dump_file,loger
from configs import settings

def login(user_info_dict,user_file):
	while True:
		#global username
		username = input('请输入用户名：').strip()
		#用户名为空
		if len(username) == 0:
			print("用户名不能为空")
		# 用户名不存在
		elif username not in user_info_dict.keys():
			print('用户名不存在，请重新输入！')
		# 用户名存在
		else:
		# 判断登录次数
			if user_info_dict[username]['try_times'] >=3:
				print('账户已经冻结,请联系管理员.')
				return False
			else:
				pwd = input('请输入密码：').strip()
				if user_info_dict[username]['pwd'] == pwd:
				# 如果登录成功，将登录次数重置为 0
					user_info_dict[username]['times'] = 0
					print('恭喜您 %s，登录成功' % username)
					dump_file.dump_file(user_info_dict,user_file)
					return username
				else:
				# 如果登录失败，登录次数加1
					user_info_dict[username]['try_times'] += 1
					times = user_info_dict[username]['try_times']
					left_times = 3 - times
					if left_times == 0:
						print('账户已经冻结，请联系管理员')
						dump_file.dump_file(user_info_dict,user_file)
						return False
					else:
						print("密码输入错误，您还有 %s 次尝试机会..." %left_times)
"""
def out1(func):
	def wrapper(*args,**kwargs):
		login(settings.shop_user_data,settings.shop_user_file_path)
		return func(*args,**kwargs)
	return wrapper

def out2(func):
	def wrapper(*args,**kwargs):
		ret = login(settings.atm_user_data,settings.atm_user_file_path)
		return func(ret)
	return wrapper
"""

def fiter(arg1,arg2):
	def out(func):
		def wrapper(*args):
			ret = login(arg1,arg2)
			if ret:
				loger.loger('ATM.var',ret,settings.time_now,'-','info','logging')
				return func(ret,*args)
		return wrapper
	return out
