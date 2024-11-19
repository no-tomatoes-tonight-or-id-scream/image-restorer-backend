import os

from loguru import logger
from ccrestoration import ConfigType

class Status:
    def __init__(self):
        self.pool_size = 4
        self.lock_file_prefix = "lock_"
        
    def check_lock_file(self):
        '''
        检查锁文件是否存在
        :return: 返回 True 或者 False
        '''
        lock_files = [f for f in os.listdir() if f.startswith(self.lock_file_prefix)]
        return len(lock_files) > self.pool_size
    
    def create_lock_file(self):
        '''
        创建锁文件
        :return: None
        '''
        with open(f"{self.lock_file_prefix}{os.getpid()}", "w") as f:
            f.write("lock")
            
    def remove_lock_file(self):
        '''
        删除锁文件
        :return: None
        '''
        lock_files = [f for f in os.listdir() if f.startswith(self.lock_file_prefix)]
        for f in lock_files:
            os.remove(f)
            
    def upload_status(self):
        '''
        上传图片状态
        :return: 返回 OK 或者 NO
        '''
        if self.check_lock_file():
            return {"status": "NO"}
        else:
            self.create_lock_file()
            return {"status": "OK"}