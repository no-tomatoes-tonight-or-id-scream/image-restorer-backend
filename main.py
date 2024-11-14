from fastapi import FastAPI
from status import Status
from uploader import Uploader

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Restorer Backend"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# 前端向后端发送传送图片请求，返回 OK 才可以上传图片，否则不上传
@app.post("/upload_status")
def upload_status():
    """
    上传图片状态
    :return: 返回 OK 或者 NO
    """

    # 检查锁文件是否存在
    # 如果存在，返回 NO
    # 如果不存在，返回 OK

    return Status().upload_status()


# 前端上传图片，返回 OK
@app.post("/upload_image")
def upload_image():
    """
    上传图片
    :return: 返回 OK 或者 NO
    """
    return Uploader().upload_image()

# 前端删除图片，路径从数据库删除，返回 OK
@app.post("/remove_image")
def remove_image():
    """
    删除图片
    :return: 返回 OK 或者 NO
    """
    return Uploader().remove_image()

# 获取前端的 config，处理图像，返回处理后的图像
@app.post("/process")
def process():
    """
    处理图像
    :return: 返回处理后的图像
    """
    pass
