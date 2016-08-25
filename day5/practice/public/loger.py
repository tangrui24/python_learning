from configs import settings
import os
def loger(log_file_path,account,tran_date,tran_type,amount=None,interest=0):
	f = open(os.path.join(settings.log_dir_path,log_file_path),'a')
	msg="%s %s %s %s %s" %(account,tran_date,tran_type,amount,interest)
	f.write(msg+"\n")
	f.close()

