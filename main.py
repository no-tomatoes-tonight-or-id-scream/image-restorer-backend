from fastapi import FastAPI
from status import Status
from uploader import Uploader
from processor import Processor
from fastapi import UploadFile, File

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Restorer Backend", "status": "OK"}


# 前端向后端发送传送图片请求，返回 OK 才可以上传图片，否则不上传
@app.post("/upload_status")
def upload_status():
    """
    上传图片状态
    :return: 返回 OK 或者 NO
    """
    return Status().upload_status()


# # 前端上传图片，返回 OK
# @app.post("/upload_image")
# def upload_image():
#     """
#     上传图片
#     :return: 返回 OK 或者 NO
#     """
#     return Uploader().upload_image()


# # 前端删除图片，路径从数据库删除，返回 OK
# @app.post("/remove_image")
# def remove_image():
#     """
#     删除图片
#     :return: 返回 OK 或者 NO
#     """
#     return Uploader().remove_image()


# 获取前端请求中负载的 config 字典
# 调用方法：requests.post("http://root:8000/process", files={"config_file": open("config.yaml", "rb")})
@app.post("/process")
async def process(config: dict, image: UploadFile = File(...)):
    """
    上传 config 字典
    :param config: 上传的配置字典
    :return: 返回 OK 或者 NO
    """
    return Processor().process(config, image)

@app.post("/get_processing_status")
def get_processing_status():
    """
    获取处理状态
    :return: 返回处理状态
    """
    return Processor().get_processing_status()