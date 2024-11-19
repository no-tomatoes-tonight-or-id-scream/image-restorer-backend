from fastapi.testclient import TestClient
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


# def test_upload_image():
#     """测试上传图片接口"""
#     response = client.post("/upload_image")
#     assert response.status_code == 200
#     # 假设 Uploader().upload_image() 返回 {"status": "OK"} 或 {"status": "NO"}
#     assert "status" in response.json()
#     assert response.json()["status"] in ["OK", "NO"]


# def test_remove_image():
#     """测试删除图片接口"""
#     response = client.post("/remove_image")
#     assert response.status_code == 200
#     # 假设 Uploader().remove_image() 返回 {"status": "OK"} 或 {"status": "NO"}
#     assert "status" in response.json()
#     assert response.json()["status"] in ["OK", "NO"]


def test_process():
    """测试处理图片接口"""
    # 创建测试用的配置字典和图片文件
    test_config = {"param1": "value1", "param2": "value2"}

    # 创建一个模拟的图片文件
    test_image = io.BytesIO(b"fake image content")

    # 发送测试请求
    response = client.post(
        "/process",
        json=test_config,
        files={"image": ("test.jpg", test_image, "image/jpeg")},
    )

    assert response.status_code == 200
    # 假设 Processor().process() 返回某种处理结果
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
