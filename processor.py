import yaml
import argparse
import os
from fastapi import File

class Processor:
    def __init__(self):
        self.process_object = {
            "config": None,
            "image": None
        }
        self._processing = False
    
    def final2x_core(self, config: dict, image: File):
        '''
        调用 final2x_core 方法，返回处理的图像
        :param config: 上传的配置字典
        :param image: 图片
        :return: 返回处理的图像
        '''
        self._processing = True
        self._processing = False
        
        pass
        
    def process(self, config: dict, image: File):
        '''
        上传 config 字典
        :param config: 上传的配置字典
        :return: 返回 OK 或者 NO
        '''
        self.process_object["config"] = config
        self.process_object["image"] = image
        
        # 调用 final2x_core 方法，返回处理的图像
        return self.final2x_core(config, image)
    
    def get_processing_status(self):
        '''
        获取处理状态
        :return: 返回处理状态
        '''
        if self._processing:
            return {"status": "OK"}
        else:
            return {"status": "NO"}
        