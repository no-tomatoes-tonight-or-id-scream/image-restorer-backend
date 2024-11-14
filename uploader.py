import os
from fastapi import UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Form

from loguru import logger

class Uploader:
    def __init__(self):
        self.upload_folder = "upload"
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def upload_image(self, image: UploadFile = Form(...)):
        '''
        上传图片
        :param image: 图片
        :return: 返回 OK 或者 NO
        '''
        with open(f"{self.upload_folder}/{image.filename}", "wb") as f:
            f.write(image.file.read())
        return JSONResponse(content={"status": "OK"})
    
    def remove_image(self, image_name: str = Form(...)):
        '''
        删除图片
        :param image_name: 图片名
        :return: 返回 OK 或者 NO
        '''
        try:
            os.remove(f"{self.upload_folder}/{image_name}")
            return JSONResponse(content={"status": "OK"})
        except Exception as e:
            logger.error(e)
            return JSONResponse(content={"status": "NO"})
        
    def get_image_list(self):
        '''
        获取图片列表
        :return: 返回图片列表
        '''
        return os.listdir(self.upload_folder)
    
    def get_image(self, image_name: str):
        '''
        获取图片文件
        :param image_name: 图片名
        :return: 返回图片文件
        '''
        return FileResponse(f"{self.upload_folder}/{image_name}")
    