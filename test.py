import requests
import base64

# 基础 URL
BASE_URL = "http://127.0.0.1:8000"

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
    import cv2
    # 准备测试图像
    image_data = cv2.imread("test_image.jpg")

    # 准备文件
    files = {
        'image': ('test_image.jpg', image_data, 'image/jpeg')
    }

    # 准备其他参数（需要作为表单数据发送）
    params = {
        'target_scale': 2.0,
        'pretrained_model_name': 'RealESRGAN_AnimeJaNai_HD_V3_Compact_2x.pth'
    }

    # 发送处理请求
    response = requests.post(f"{BASE_URL}/process", files=files, params=params)
    print("\nProcess image test:")
    print(response.json())
    
    # 确保响应中包含 task_id
    assert response.status_code == 200
    assert 'task_id' in response.json()

    # 获取任务 ID
    task_id = response.json()['task_id']
    
    # 等待并获取结果
    import time
    max_attempts = 10
    for _ in range(max_attempts):
        result_response = requests.post(f"{BASE_URL}/get_result", json={"task_id": task_id})
        result = result_response.json()
        
        print("\nTask status:", result['status'])
        
        if result['status'] == 'completed':
            # 如果结果是 base64 编码的图像，可以保存
            if result['result']:
                decoded_image = base64.b64decode(result['result'])
                with open('processed_image.jpg', 'wb') as f:
                    f.write(decoded_image)
                print("Processed image saved successfully!")
            break
        
        time.sleep(2)  # 每 2 秒检查一次
    
    assert result['status'] == 'completed'

def main():
    test_root()
    # test_upload_status()
    test_process_image()

if __name__ == '__main__':
    main()
