import base64
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from processor import Processor
from fastapi import UploadFile, File
from fastapi.encoders import jsonable_encoder
import numpy as np
import cv2
from fastapi import BackgroundTasks
from typing import Dict
from threading import Lock
import uuid

app = FastAPI()


def numpy_encoder(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Restorer Backend", "status": "OK"}


def bytes_encoder(obj):
    return base64.b64encode(obj).decode("utf-8")


task_status: Dict[str, Dict] = {}
task_status_lock = Lock()


@app.post("/process")
async def process(
    target_scale: float,
    pretrained_model_name: str,
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
):
    # 生成唯一任务 ID
    task_id = str(uuid.uuid4())

    config = {
        "device": "auto",
        "gh_proxy": None,
        "input_path": None,
        "output_path": None,
        "pretrained_model_name": pretrained_model_name,
        "target_scale": target_scale,
    }

    # 使用线程安全方式更新任务状态
    with task_status_lock:
        task_status[task_id] = {"status": "processing", "result": None, "error": None}

    image_format = image.filename.split(".")[-1]
    image_path = f"upload/{task_id}.{image_format}"

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
            # task_status[task_id]["result"] = FileResponse(f"results/{task_id}.{image_format}")
    except Exception as e:
        # 捕获并记录处理过程中的错误
        print(e)
        with task_status_lock:
            task_status[task_id]["status"] = "error"
            task_status[task_id]["error"] = str(e)


@app.post("/get_result")
def get_result(task_id: str):
    """
    获取处理结果
    """
    # 使用线程安全方式获取任务状态
    with task_status_lock:
        # 检查任务是否存在
        if task_id not in task_status:
            raise HTTPException(status_code=404, detail="Task not found")

        if task_status[task_id]["status"] == "completed":
            # 查找结果文件，目录里为 uuid 的文件名，后缀未知
            result_file = None
            for file in os.listdir("results"):
                if file.startswith(task_id):
                    result_file = file
                    break            
            # 返回处理结果
            return {
                "status": "completed",
                "result": FileResponse(f"results/{result_file}")
            }
        # 返回任务状态
        return {"status": task_status[task_id]["status"]}


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)


if __name__ == "__main__":
    main()
