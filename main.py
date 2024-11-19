import base64
from fastapi import FastAPI
from status import Status
from uploader import Uploader
from processor import Processor
from fastapi import UploadFile, File
from fastapi.encoders import jsonable_encoder
import numpy as np

app = FastAPI()


def numpy_encoder(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Restorer Backend", "status": "OK"}


# 前端向后端发送传送图片请求，返回 OK 才可以上传图片，否则不上传
@app.post("/upload_status")
def upload_status():
    """
    上传图片状态
    :return: 返回 OK 或者 ERROR
    """
    return Status().upload_status()


def bytes_encoder(obj):
    return base64.b64encode(obj).decode('utf-8')

@app.post("/process")
async def process(
    target_scale: float, pretrained_model_name: str, image: UploadFile = File(...)
):
    """
    上传 config 字典
    :param config: 上传的配置字典
    :return: 返回 OK 或者 ERROR
    """
    config = {
        "device": "auto",
        "gh_proxy": None,
        "input_path": None,
        "output_path": None,
        "pretrained_model_name": pretrained_model_name,
        "target_scale": target_scale,
    }
    result = Processor().process(config, image)

    # 使用自定义编码器，对 bytes 进行 base64 编码
    custom_encoder = {
        bytes: bytes_encoder,
        np.ndarray: lambda x: base64.b64encode(x).decode('utf-8')
    }
    
    return jsonable_encoder(result, custom_encoder=custom_encoder)

@app.post("/get_processing_status")
def get_processing_status():
    """
    获取处理状态
    :return: 返回处理状态
    """
    return Processor().get_processing_status()
