import io
import json
import os
from fastapi import File, UploadFile
import cv2
import numpy as np

from Final2x_core import CCRestoration, SRConfig
from util import calculate_image_similarity, compare_image_size


class Processor:
    def __init__(self):
        self._processing = False

    def final2x_core(self, config: dict, image_path: str, image_format: str):
        """
        调用 final2x_core 方法，返回处理的图像
        :param config: 上传的配置字典
        :param image_path: 图片路径
        :param image_format: 图片格式
        :return: 返回处理的图像
        """
        print(config)
        json_str = json.dumps(config)
        print(json_str)
        SRconfig = SRConfig.from_json_str(json_str)
        SR = CCRestoration(config=SRconfig)
        source_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # img: np.ndarray
        result_img = SR.process(source_img)

        _, encoded_img = cv2.imencode(f".{image_format}", result_img)
        return encoded_img.tobytes()

    def process(self, config: dict, image: File):
        """
        上传 config 字典
        :param config: 上传的配置字典
        :return:
            - status: 返回 OK 或者 NO
            - result: 返回处理的图像
        """

        # give a hash then save the image
        image_format = image.filename.split(".")[-1]
        image_hash = self.calculate_image_hash(image.filename.encode())
        image.file.seek(0)
        image_path = f"upload/{image_hash}.{image_format}"
        with open(image_path, "wb") as f:
            f.write(image.file.read())

        # 调用 final2x_core 方法，返回处理的图像
        self._processing = True
        result = self.final2x_core(config, image_path, image_format)
        self._processing = False

        os.remove(image_path)
        # 返回请求的结果
        return {"status": "OK", "result": result}

    def get_processing_status(self):
        """
        获取处理状态
        :return: 返回处理状态
        """
        if self._processing:
            return {"status": "OK"}
        else:
            return {"status": "NO"}

    @staticmethod
    def calculate_image_hash(image_filename_bytes: bytes):
        """
        计算图片的哈希值
        :param image_filename_bytes: 图片名称的字节数据
        :return: 返回图片的哈希值
        """
        import hashlib
        import random

        file_name = hashlib.md5(
            image_filename_bytes + str(random.random()).encode()
        ).hexdigest()
        return file_name


def main():
    processor = Processor()
    config = {
        "device": "auto",
        "gh_proxy": None,
        "input_path": None,
        "output_path": None,
        "target_scale": 2.0,
        "pretrained_model_name": "RealESRGAN_AnimeJaNai_HD_V3_Compact_2x.pth",
    }
    with open(
        "C:/Users/Jiarong/Pictures/890b6e72-9092-4ee8-a988-0239d41ba787.png", "rb"
    ) as f:
        file_bytes = f.read()
        file_obj = UploadFile(
            filename="890b6e72-9092-4ee8-a988-0239d41ba787.png",
            file=io.BytesIO(file_bytes),
        )

    response = processor.process(config, file_obj)
    print(response["status"])


if __name__ == "__main__":
    main()
