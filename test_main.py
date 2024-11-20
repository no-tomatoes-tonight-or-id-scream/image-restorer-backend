from fastapi.testclient import TestClient
from fastapi import UploadFile, File
import pytest
from main import app
import io

client = TestClient(app)


def test_read_root():
    """测试根路径接口"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Image Restorer Backend",
        "status": "OK",
    }


def test_upload_status():
    """测试上传状态接口"""
    response = client.post("/upload_status")
    assert response.status_code == 200
    # 假设 Status().upload_status() 返回 {"status": "OK"} 或 {"status": "NO"}
    assert "status" in response.json()
    assert response.json()["status"] in ["OK", "NO"]


def test_process():
    """测试处理图片接口"""
    import cv2
    import numpy as np
    import base64

    test_target_scale = 2.0
    test_pretrained_model_name = "RealESRGAN_AnimeJaNai_HD_V3_Compact_2x.pth"

    test_image_path = (
        "C:/Users/Jiarong/Pictures/890b6e72-9092-4ee8-a988-0239d41ba787.png"
    )
    test_image_type = "image/png"
    with open(test_image_path, "rb") as f:
        test_image_bytes = f.read()
        test_image = io.BytesIO(test_image_bytes)

    # 发送测试请求
    response = client.post(
        "/process",
        params={
            "target_scale": test_target_scale,
            "pretrained_model_name": test_pretrained_model_name,
        },
        files={"image": ("test.jpg", test_image, test_image_type)},
    )

    # 解析响应
    response_json = response.json()

    # 解码 base64 编码的图像数据
    result_bytes = base64.b64decode(response_json["result"])

    assert response.status_code == 200
    assert "status" in response.json()


def test_get_processing_status():
    """测试获取处理状态接口"""
    response = client.post("/get_processing_status")
    assert response.status_code == 200
    # 假设 Processor().get_processing_status() 返回处理状态信息
    assert "status" in response.json()


# 测试错误情况
def test_process_without_image():
    """测试没有图片文件的处理请求"""
    test_config = {"param1": "value1"}
    response = client.post("/process", json=test_config)
    assert response.status_code == 422  # FastAPI 的验证错误状态码


def test_process_without_config():
    """测试没有配置的处理请求"""
    test_image = io.BytesIO(b"fake image content")
    response = client.post(
        "/process", files={"image": ("test.jpg", test_image, "image/jpeg")}
    )
    assert response.status_code == 422  # FastAPI 的验证错误状态码
