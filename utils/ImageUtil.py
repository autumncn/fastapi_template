import cv2
import base64
from PIL import Image
from io import BytesIO
import numpy as np

async def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        s = base64_data.decode()
    return s

async def image_path_to_image(image_path):
    image = cv2.imread(image_path)
    return image

async def image_hw(image):
    # img = cv2.imread(image)
    height, width = image.shape[:2]
    return height, width

async def new_image_hw_by_maxref(image, maxref=512):
    h, w = image_hw(image)
    max_hw = max(w, h)
    if max_hw == h:
        new_h = maxref
        new_w = int(w * new_h / h)
    else:
        new_w = maxref
        new_h = int(h * new_w / w)

    return new_h, new_w


async def cv2_base64(image):
    base64_str = cv2.imencode('.jpg',image)[1].tobytes()
    base64_str = base64.b64encode(base64_str)
    # print(base64_str)
    return base64_str

async def base64_cv2(base64_str):
    imgString = base64.b64decode(base64_str)
    nparr = np.fromstring(imgString,np.uint8)
    image = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    return image

if __name__ == '__main__':
    # image = '/Users/lucas/Downloads/684D-Woodlands-Drive-73-Admiralty-Woodlands-Singapore.jpg'
    # image_path = '/Users/lucas/Downloads/Xnip2023-03-27_14-53-23.jpg'
    image_path = '/Users/lucas/Downloads/421324230_A_dream_of_a_distant_galaxy__concept_art__matte_painting__HQ__4k.png'
    image = image_path_to_image(image_path)
    cv2_base64(image)
    print(image_hw(image))
    print(new_image_hw_by_maxref(image, 1024))