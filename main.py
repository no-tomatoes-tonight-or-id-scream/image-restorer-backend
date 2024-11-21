import base64
from fastapi import FastAPI
from status import Status
from uploader import Uploader
from processor import Processor
from fastapi import UploadFile, File
from fastapi.encoders import jsonable_encoder
import numpy as np
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
    return base64.b64encode(obj).decode('utf-8')

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
    image_data = await image.read()
    background_tasks.add_task(process_image, task_id, config, image_data)

    return {"status": "received", "task_id": task_id}

def process_image(task_id, config, image_data):
    result = Processor().process(config, image_data)

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