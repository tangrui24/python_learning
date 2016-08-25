import os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from core import Ftpclient

if __name__ == "__main__":
    ftp_obj =Ftpclient.FtpClient()

