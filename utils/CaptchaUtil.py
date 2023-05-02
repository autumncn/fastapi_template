# coding:utf-8
# name:captcha_gen.py
import base64
import random
from io import BytesIO

import numpy as np
from PIL import Image
from captcha.image import ImageCaptcha


NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
LOW_CASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
UP_CASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
           'V', 'W', 'X', 'Y', 'Z']

CAPTCHA_LIST = NUMBER + LOW_CASE + UP_CASE
CAPTCHA_LEN = 5         # 验证码长度
CAPTCHA_HEIGHT = 60     # 验证码高度
CAPTCHA_WIDTH = 160     # 验证码宽度


def random_captcha_text(char_set=CAPTCHA_LIST, captcha_size=CAPTCHA_LEN):
    """
    随机生成定长字符串
    :param char_set: 备选字符串列表
    :param captcha_size: 字符串长度
    :return: 字符串
    """
    captcha_text = [random.choice(char_set) for _ in range(captcha_size)]
    return ''.join(captcha_text)


def gen_captcha_text_and_image(width=CAPTCHA_WIDTH, height=CAPTCHA_HEIGHT, save=None):
    """
    生成随机验证码
    :param width: 验证码图片宽度
    :param height: 验证码图片高度
    :param save: 是否保存（None）
    :return: 验证码字符串，验证码图像np数组
    """
    image = ImageCaptcha(width=width, height=height)
    # 验证码文本
    captcha_text = random_captcha_text()
    captcha = image.generate(captcha_text)
    # 保存
    if save:
        image.write(captcha_text, './img/' + captcha_text + '.jpg')
    captcha_image = Image.open(captcha)
    # # 转化为np数组
    # captcha_image = np.array(captcha_image)
    # 转化为base64
    captcha_image = pil_base64(captcha_image)
    return captcha_text, captcha_image

# def convert_nparray_to_base64(nparray):
#     img_str = base64.b64encode(nparray)
#     #
#     # bytesio = BytesIO()
#     # np.savetxt(bytesio, nparray)  # 只支持1维或者2维数组，numpy数组转化成字节流
#     # content = bytesio.getvalue()  # 获取string字符串表示
#     # print(content)
#     # b64_code = base64.b64encode(content)
#     return img_str
def pil_base64(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

if __name__ == '__main__':
    # t, im = gen_captcha_text_and_image(save=True)
    t, im = gen_captcha_text_and_image(save=False)
    # print(im)

    # img = convert_nparray_to_base64(im)

    print(t, im)
    # print(t, im.shape)      # (60, 160, 3)
