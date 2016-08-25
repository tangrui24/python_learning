import logging
import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def set_log():
    try:
        from conf.settings import output_console, log_file, encoding, log_level, \
            console_log_level, file_log_level, formatter
    except:
        output_console = True
        log_file = None
        log_level = logging.DEBUG
        console_log_level = logging.INFO
        encoding = "utf8"
        file_log_level = logging.INFO
        formatter = logging.Formatter("%(asctime)s  -  %(name)s   -  %(levelname)s  - %(message)s")
    logger = logging.getLogger(__name__)  # 创建日志对象
    logger.setLevel(log_level)  # 设置日志记录级别
    if output_console:
        console_handler = logging.StreamHandler()  # 创建控制台日志输出对象
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(formatter)
        logger.addFilter(console_handler)
    if log_file:
        console_handler = logging.FileHandler(filename=log_file, encoding=encoding)  # 创建控制台日志输出对象
        console_handler.setLevel(file_log_level)
        console_handler.setFormatter(formatter)
        logger.addFilter(console_handler)
    return logger