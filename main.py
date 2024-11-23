import io
import os
import numpy as np
import cv2

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict, Union
from threading import Lock
import uuid

from utils import Processor
from ccrestoration import ConfigType


# device_list = ["auto", "cpu", "cuda", "mps", "xpu", "xla", "meta"]
device = "cuda"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def numpy_encoder(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Restorer Backend", "status": "OK"}


task_status: Dict[str, Dict] = {}
task_status_lock = Lock()


@app.post("/process")
async def process(
    target_scale: float,
    pretrained_model_name: Union[ConfigType, str],
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
) -> Dict:
    """
    处理图像

    :param target_scale: 目标放大倍数
    :param pretrained_model_name: 预训练模型名称
    :param image: 待处理图像文件
    :param background_tasks: 后台任务
    :return: 任务状态
    """
    # 生成唯一任务 ID
    task_id = str(uuid.uuid4())

    config = {
        "device": "cuda",
        "gh_proxy": None,
        "input_path": None,
        "output_path": None,
        "pretrained_model_name": pretrained_model_name,
        "target_scale": target_scale,
    }

    # 使用线程安全方式更新任务状态
    with task_status_lock:
        task_status[task_id] = {"status": "processing"}

    image_format = image.filename.split(".")[-1]
    image_path = f"uploads/{task_id}.{image_format}"

    try:
        # 保存文件
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)

        # 使用 OpenCV 读取图像
        source_img = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if source_img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # 添加后台任务
        background_tasks.add_task(
            process_image, task_id, config, image_format, image_path, source_img
        )

    except Exception as e:
        # 错误处理
        with task_status_lock:
            task_status[task_id]["status"] = "error"
            task_status[task_id]["error"] = str(e)

        # 清理临时文件
        if os.path.exists(image_path):
            os.remove(image_path)

        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 确保临时文件被删除
        if os.path.exists(image_path):
            os.remove(image_path)

    return {"status": "received", "task_id": task_id}


def process_image(task_id, config, image_format, image_path, source_img):
    try:
        result = Processor().process(
            config, task_id, image_format, image_path, source_img
        )
        if result["status"] != "OK":
            raise ValueError("Error processing image")
        # 使用线程安全方式更新任务状态
        with task_status_lock:
            task_status[task_id]["status"] = "completed"
    except Exception as e:
        # 捕获并记录处理过程中的错误
        print(e)
        with task_status_lock:
            task_status[task_id]["status"] = "error"
            task_status[task_id]["error"] = str(e)


@app.get("/get_status")
def get_status(task_id: str) -> Dict:
    """
    获取处理任务状态

    :param task_id: 任务 ID
    :return: 任务状态，可能为 processing, completed, error。当状态为 error 时，会包含 error 字段
    """
    
    # 使用线程安全方式获取任务状态
    with task_status_lock:
        # 检查任务是否存在
        if task_id not in task_status:
            raise HTTPException(status_code=404, detail="Task not found")

        return task_status[task_id]


@app.get("/get_result")
async def get_result(task_id: str) -> StreamingResponse:
    """
    获取处理结果

    :param task_id: 任务 ID
    :return: 处理结果
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    result_file = None
    for file in os.listdir("results"):
        if file.startswith(task_id):
            result_file = file
            break
    file_path = f"results/{result_file}"
    image_format = result_file.split(".")[-1]

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 读取文件并创建文件流
    with open(file_path, "rb") as file:
        return StreamingResponse(
            io.BytesIO(file.read()), media_type=f"image/{image_format}"
        )

@app.get("/get_model_list")
def get_model_list() -> Dict:
    """
    从 ConfigType 获取模型列表
    
    :return: 模型列表
    """
    model_list: Dict = {}
    for model in ConfigType:
        model_list[model.name] = model.value
    return model_list

def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)


if __name__ == "__main__":
    main()
