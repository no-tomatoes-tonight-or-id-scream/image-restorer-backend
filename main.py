import base64
import os
from fastapi import FastAPI, HTTPException
from status import Status
from uploader import Uploader
from processor import Processor
from fastapi import UploadFile, File
from fastapi.encoders import jsonable_encoder
import numpy as np
import cv2
from fastapi import BackgroundTasks
import uuid

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
    return base64.b64encode(obj).decode("utf-8")


task_status = {}


@app.post("/process")
async def process(
    target_scale: float,
    pretrained_model_name: str,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
):
    """
    Receive the processing request, start processing in background, and return confirmation.
    """
    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    config = {
        "device": "auto",
        "gh_proxy": None,
        "input_path": None,
        "output_path": None,
        "pretrained_model_name": pretrained_model_name,
        "target_scale": target_scale,
    }

    task_status[task_id] = {"status": "processing", "result": None}
    image_format = image.filename.split(".")[-1]
    image_path = f"upload/{task_id}.{image_format}"
    try:
        # 保存文件
        filename = os.path.join("upload", image_path)
        with open(filename, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # 使用 OpenCV 读取图像
        source_img = cv2.imread(filename, cv2.IMREAD_COLOR)
        
        if source_img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
    except Exception as e:
        # 错误处理
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 可选：清理临时文件
        if os.path.exists(image_path):
            os.remove(image_path)
    # image_data = await image.read() # await 将异步函数转换为同步函数
    # nparr = np.fromstring(image_data, np.uint8)
    # source_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # background_tasks.add_task(
    #     process_image, task_id, config, image_format, image_path, source_img
    # )

    return {"status": "received", "task_id": task_id}


def process_image(task_id, config, image_format, image_path, source_img):

    result = Processor().process(config, task_id, image_format, image_path, source_img)

    task_status[task_id]["status"] = "completed"
    task_status[task_id]["result"] = result


@app.post("/get_result")
def get_result(task_id: str):
    """
    获取处理结果
    :return: 返回处理结果
    """
    return task_status[task_id]


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)


if __name__ == "__main__":
    main()
