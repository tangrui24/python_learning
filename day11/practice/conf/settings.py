import os,sys
import pymysql
Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)

#mysql连接
DB_CONN = "mysql+pymysql://root@127.0.0.1:3306/test"

