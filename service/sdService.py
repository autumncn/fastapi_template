import asyncio
import datetime
import json
import base64
import time

import httpx
import ssl
from fastapi import Depends

import requests
from celery import shared_task
from sqlalchemy.orm import Session

from core.celeryConfig import celery_app
from db.crud.sdTasks import get_sd_task_by_uuid
from db.crud.sdToImg import get_img_by_create, get_img_by_id, modify_sdToImg
from db.database import get_db
from db.schemas.sdToImg import SdToImgModify
from service.taskService import modify_task_by_uid, get_task_result, get_task
from utils.JsonUtil import object_to_json

ssl._create_default_https_context = ssl._create_unverified_context

# api_host = 'https://stable.cloudtim.com'
# api_host = 'http://oracle2.cloudtim.com:27861'
# api_host = 'http://192.168.31.210:7861'
from db.schemas.txt2img import cnTxt2imgRequest, controlnetRequest, txt2imgRequest
from utils.DatetimeUtil import datetime_to_timestamp
from utils.ImageUtil import new_image_hw_by_maxref, image_path_to_image, cv2_base64, base64_cv2

# api_host = 'https://stable_2080super_api.cloudtim.com'
# api_host = 'https://stable_api.cloudtim.com'
# api_host = 'https://stable_2070_api.cloudtim.com'
# api_host = 'https://stable_2080super.cloudtim.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15 controlNet/1.0.1 cloudtim/0.0.1',
}

async def get_models(api_host):
    # progress_url = api_host + '/sdapi/v1/progress?skip_current_image=false'
    progress_url = api_host + '/sdapi/v1/sd-models'
    async with httpx.AsyncClient(verify=False) as client:
        result = await client.get(progress_url, headers=headers, timeout=10, auth=("stable", "stable123"))
        model_list = result.json()
        model_title_list = []
        for model in model_list:
            # print(model)
            model_title_list.append([model['title'], model['sha256']])
        # print(model_title_list)
        return model_title_list


async def get_current_model(api_host):
    progress_url = api_host + '/sdapi/v1/options'
    async with httpx.AsyncClient(verify=False) as client:
        result = await client.get(progress_url, headers=headers, timeout=10)
        result_json = result.json()
        print(result_json.get('sd_model_checkpoint'))
        return result_json

async def swtich_model(api_host, model_name):
    # progress_url = api_host + '/sdapi/v1/progress?skip_current_image=false'
    progress_url = api_host + '/sdapi/v1/options'
    async with httpx.AsyncClient(verify=False) as client:
        result = await client.post(progress_url, data=json.dumps({"sd_model_checkpoint": model_name, "CLIP_stop_at_last_layers": 2}), headers=headers, timeout=10)
        result_json = result.json()
        return result_json

async def find_controlnet_model(api_host):
    progress_url = api_host + '/controlnet/model_list'
    async with httpx.AsyncClient(verify=False) as client:
        result = await client.get(progress_url, headers=headers, timeout=10, auth=("stable", "stable123"))
        result_json = result.json()
        return result_json

async def generate_txtToImg(api_host, dataJson):
    uri = '/sdapi/v1/txt2img'
    url = api_host + uri
    async with httpx.AsyncClient(verify=False) as client:
        result = await client.post(url, headers=headers, data=dataJson, timeout=600)
        responseJson = result.json()
        # print(responseJson)
        return responseJson

@celery_app.task
def generate_txtToImg_by_id(api_host, id):
    time.sleep(1)
    get_sdToImg = get_img_by_id(next(get_db()), id=int(id))

    key_word = get_sdToImg.prompt
    image = get_sdToImg.content
    steps = get_sdToImg.step
    ai_level = get_sdToImg.cfg
    cn_mode = get_sdToImg.controlnet_mode
    # print(" modify -- 1", get_sdToImg.uri, key_word, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    new_h, new_w = new_image_hw_by_maxref(base64_cv2(image), 1024)
    if cn_mode == 'canny':
        new_cn_json = create_cn_jason(
            input_image=image,
            module="canny",
            model="control_sd15_canny [fef5e48e]",
        )
    elif cn_mode == 'depth':
        new_cn_json = create_cn_jason(
            input_image=image,
            module="depth",
            model="control_sd15_depth [fef5e48e]",
        )
    else:
        new_cn_json = create_cn_jason(
            input_image=image,
            module="mlsd",
            model="control_sd15_mlsd [fef5e48e]",
    )
    new_txt2img_json = create_txt2img_jason(
        steps=steps,
        width=new_w,
        height=new_h,
        cfg_scale=ai_level,
        # sampler_index="DPM++ SDE Karras",
        prompt=key_word,
        sd_model_checkpoint="v1-5-pruned-emaonly.safetensors [6ce0161689]",
        alwayson_scripts=new_cn_json
    )

    uri = '/sdapi/v1/txt2img'
    url = api_host + uri

    # 更改任务状态为2 进行中
    modify_task_by_uid(get_sdToImg.uri, 2, api_host)
    result = requests.post(url, headers=headers, data=new_txt2img_json, timeout=3600, auth=("stable", "stable123"))  # 请求url，传入header，ssl认证为false
    # async with httpx.AsyncClient(verify=False) as client:
    #     result = await client.post(url, headers=headers, data=new_txt2img_json, timeout=3600, auth=("stable", "stable123"))

    # task_result = get_task_result(get_sdToImg.uri)
    # if task_result['status'] == 1:
    #     modify_task_by_uid(get_sdToImg.uri, 0, "")
    #     return task_result

    # try:
    result_json = result.json()

    result_info = result_json['info']
    result_info_json = json.loads(result_info)
    new_seed = result_info_json['seed']
    new_image = result_json['images'][0]
    if new_image == '' or new_image == None:
        modify_task_by_uid(get_sdToImg.uri, -1, api_host)
        return result_json

    new_sdToImg = SdToImgModify(
        id=id,
        seed=new_seed,
        uri=get_sdToImg.uri,
        content_new=new_image,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    modify_sdToImg(next(get_db()), new_sdToImg)
    # 更改任务状态为3 完成
    modify_task_by_uid(get_sdToImg.uri, 3, api_host)
    # except Exception as e:
    #     modify_task_by_uid(get_sdToImg.uri, -1, api_host)
    #     result_json = {"status": "FAILURE", "result": str(e)}

    return result_json

def get_progress_image(api_host):
    # progress_url = api_host + '/sdapi/v1/progress?skip_current_image=False'
    progress_url = api_host + '/sdapi/v1/progress?skip_current_image=True'
    print(progress_url)
    # progress_url = api_host + '/internal/progress'
    '''
{
    "progress": 0.0,
    "eta_relative": 0.0,
    "state": {
        "skipped": false,
        "interrupted": false,
        "job": "",
        "job_count": 0,
        "job_timestamp": "20230328143708",
        "job_no": 1,
        "sampling_step": 0,
        "sampling_steps": 100
    },
    "current_image": null,
    "textinfo": null
}
    '''

    # async with httpx.AsyncClient(verify=False) as client:
    #     result = await client.get(progress_url, headers=headers, timeout=30, auth=("stable", "stable123"))
    #     # result = requests.get(progress_url, headers=headers)
    #     result_json = result.json()
    #     progress = result_json['progress']
    #     eta_relative = result_json['eta_relative']
    #     current_image = result_json['current_image']
    #     return progress, eta_relative, current_image

    result = requests.get(progress_url, headers=headers, timeout=10, auth=("stable", "stable123"))  # 请求url，传入header，ssl认证为false
    result_json = result.json()
    try:
        progress = result_json['progress']
        eta_relative = result_json['eta_relative']
        current_image = result_json['current_image']
    except Exception as e:
        progress = -1
        eta_relative = -1
        current_image = ''
    return progress, eta_relative, current_image

async def save_encoded_image(b64_image: str, output_path: str):
    """
    Save the given image to the given output path.
    """
    with open(output_path, "wb") as image_file:
        image_file.write(base64.b64decode(b64_image))

def create_cn_jason(
        input_image,
        weight=1,
        processor_res=64,
        threshold_a=0.1,
        threshold_b=0.1,
        module="mlsd",
        model="control_sd15_mlsd [fef5e48e]",
        guidance_start=0,
        guidance_end=1,
        guessmode=False
):
    '''
// stable-diffusion 渲染提交消息体说明
{
  "enable_hr": false,
  "prompt": "", // 提示词
  "negative_prompt": "", // 反向提示词
  "steps": 5, // 采样步数
  "width": 383, // 渲染图宽
  "height": 512, // 渲染图高
  "seed": -1,
  "batch_size": 1, // 单次渲染图片数
  "n_iter": 1,  // 渲染批次
  "cfg_scale": 7,
  "sampler_index": "DPM++ SDE Karras", // 采样算法，放到配置文件中
  "model": "6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa", // 渲染底层模型hash，放到配置文件中
  "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors [6ce0161689]",  // 渲染底层模型，放到配置文件中
  "alwayson_scripts": {
    "controlnet": {
      "args": [
        {
          "input_image": "（image base64）", // 图片base64串
          "mask": "",
          "weight": 1, // 该controlNet权重
          "processor_res": 512,
          "threshold_a": 0.1,
          "threshold_b": 0.1,
          "module": "mlsd", // controlNet 算法，放到配置文件中
          "model": "control_mlsd-fp16 [e3705cfa]",  // controlNet 模型，放到配置文件中
          "guidance_start": 0,
          "guidance_end": 1,
          "guessmode": false
        }
      ]
    }
  }
}
    '''
    # input_image_64base = image_to_base64(input_image_path)
    # input_image_64base = cv2_base64(input_image)

    newControlnetRequest = controlnetRequest(
        input_image=input_image,
        weight=weight,
        processor_res=processor_res,
        threshold_a=threshold_a,
        threshold_b=threshold_b,
        module=module,
        model=model,
        guidance_start=guidance_start,
        guidance_end=guidance_end,
        guessmode=guessmode
    )
    newControlnetRequest_json = newControlnetRequest.__dict__
    controlnet_json = {
        "controlnet": {
            "args": [newControlnetRequest_json]
        }
    }
    return controlnet_json

def create_txt2img_jason(
        enable_hr=False,
        prompt="",
        negative_prompt="signature, soft, blurry, drawing, sketch, poor quality, ugly, text, type, word, logo, pixelated, low resolution, saturated, high contrast, oversharpened",
        steps=25,
        width=512,
        height=512,
        seed=-1,
        batch_size=1,
        n_iter=1,
        cfg_scale=11.5,
        sampler_index="Euler a",
        sd_model_checkpoint="dvArch_-_Multi-Prompt_Architecture_Tuned_Model\\dvarchMultiPrompt_dvarch.ckpt [1ecb6b4e9c]",
        alwayson_scripts={}
):
    newTxt2img = txt2imgRequest(
        enable_hr=False,
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=steps,
        width=width,
        height=height,
        seed=seed,
        batch_size=batch_size,
        n_iter=n_iter,
        cfg_scale=cfg_scale,
        sampler_index=sampler_index,
        override_settings={
            "sd_model_checkpoint":sd_model_checkpoint
        },
        alwayson_scripts=alwayson_scripts
    )

    newTxt2img_json = newTxt2img.json()
    # new_txt2img_json_loads = json.loads(newTxt2img_json)
    # new_txt2img_json_loads['alwayson_scripts'] = alwayson_scripts
    return newTxt2img_json

if __name__ == '__main__':
    import tracemalloc

    tracemalloc.start()
    loop = asyncio.get_event_loop()
    # sd_model = loop.run_until_complete(find_controlnet_model("https://stable_api.cloudtim.com"))
    sd_model = loop.run_until_complete(get_models("https://stable_api.cloudtim.com"))

    print(sd_model)



