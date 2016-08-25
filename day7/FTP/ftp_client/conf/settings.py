import os,sys,logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log_file = os.path.join(base_dir, r"log\ftp_client.log")

LOG_LEVEL = logging.INFO

HOST = "127.0.0.1"

PORT = 20000

