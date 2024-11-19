import json
from fastapi import File
import cv2
import numpy as np

from Final2x_core import CCRestoration, SRConfig
from util import calculate_image_similarity, compare_image_size

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

        config_json_str = json.dumps(config, indent=4)  
        parsed_config = SRConfig.from_json_str(config_json_str)
        SR = CCRestoration(config=parsed_config)
        image_bytes = image.file.read()  # 获取上传文件的字节数据
        source_img = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        result_img = SR.process(source_img)
        assert calculate_image_similarity(source_img, result_img)
        assert compare_image_size(source_img, result_img, parsed_config.target_scale)
        
        self._processing = False
        return result_img
        
        
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
        
