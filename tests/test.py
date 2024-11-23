import requests
import base64

# 基础 URL
BASE_URL = "https://img.jrhim.com"


def test_root():
    """测试根路径"""
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint test:")
    print(response.json())
    assert response.status_code == 200


# def test_upload_status():
#     """测试上传状态"""
#     response = requests.post(f"{BASE_URL}/upload_status")
#     print("\nUpload status test:")
#     print(response.json())
#     assert response.status_code == 200


def test_process_image():
    """测试图像处理"""
    # 准备测试图像
    image_data = open("test_image.jpg", "rb").read()

    # 准备文件
    files = {"image": ("test_image.jpg", image_data, "image/jpeg")}

    # 准备其他参数（需要作为表单数据发送）
    params = {
        "target_scale": 2.0,
        "pretrained_model_name": "RealESRGAN_AnimeJaNai_HD_V3_Compact_2x.pth",
    }

    # 发送处理请求
    response = requests.post(f"{BASE_URL}/process", files=files, params=params)
    print("\nProcess image test:")
    print(response.json())

    # 确保响应中包含 task_id
    assert response.status_code == 200
    assert "task_id" in response.json()

    # 获取任务 ID
    task_id = response.json()["task_id"]

    # 等待并获取结果
    import time

    max_attempts = 10
    for _ in range(max_attempts):
        time.sleep(2)  # 每 2 秒检查一次
        result_response = requests.post(
            f"{BASE_URL}/get_result", params={"task_id": task_id}
        )
        result = result_response.json()

        print("\nTask status:", result["status"])

        if result["status"] == "completed":
            # {'status': 'completed', 'result': {'path': 'results/cf9c7c28-74f5-4d77-86cc-7fe71dc5c355.jpg', 'status_code': 200, 'filename': None, 'media_type': 'image/jpeg', 'background': None, 'raw_headers': [['content-type', 'image/jpeg'], ['accept-ranges', 'bytes']], '_headers': {'content-type': 'image/jpeg', 'accept-ranges': 'bytes'}, 'stat_result': None}}
            print("Result:", result["result"])
            break

        time.sleep(2)  # 每 2 秒检查一次

    assert result["status"] == "completed"


def main():
    test_root()
    # test_upload_status()
    test_process_image()


if __name__ == "__main__":
    main()
