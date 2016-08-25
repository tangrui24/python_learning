class MyException(Exception):
    """
    记录异常信息
    """
    __errcodes = {
        "103": "堡垒机用户不存在",
        "104": "主机或主机用户不存在",
        "105": "主机组不存在",
        "106": "无效的命令,输入help查看帮助",
        "202": "尝试次数过多"
    }

    def __init__(self, errcode):
        self._errcode = errcode

    def __str__(self):
        return self.__errcodes[self._errcode]

