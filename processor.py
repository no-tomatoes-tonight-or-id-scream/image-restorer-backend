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
        pass

    def final2x_core(self, config: dict, source_img):
        """
        调用 final2x_core 方法，返回处理的图像
        :param config: 上传的配置字典
        :param image_path: 图片路径
        :param image_format: 图片格式
        :return: 返回处理的图像
        """
        json_str = json.dumps(config)
        print(json_str)
        SRconfig = SRConfig.from_json_str(json_str)
        SR = CCRestoration(config=SRconfig)
        result_img = SR.process(source_img)
        return result_img

    def process(
        self, config: dict, task_id, image_format: str, image_path: str, source_img
    ):
        """
        上传 config 字典
        :param config: 上传的配置字典
        :return:
            - status: 返回 OK 或者 NO
            - result: 返回处理的图像
        """
        # print(source_img)
        # 调用 final2x_core 方法，返回处理的图像
        result = self.final2x_core(config, source_img)
        print(result.shape)
        cv2.imwrite(
            f"results/{task_id}.{image_format}", result
        )
        return {"status": "OK"}


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
