import asyncio
import base64
import datetime
import json
import time
from typing import List, Optional

from celery import shared_task
from fastapi import Request,Query

from fastapi.params import Form
from fastapi import Depends, APIRouter,HTTPException
from sqlalchemy.orm import Session

from core.celeryConfig import celery_app
from db.crud.items import get_items, create_user_item, get_item
from db.crud.nodes import get_nodes_type, modify_node
from db.crud.sdToImg import get_img_by_id, create_sdToImg
from db.crud.users import get_user_by_email, create_user
from db.database import get_db
from db.redis import init_redis_pool, MyRedis, get_redis
from db.schemas.items import Item, ItemCreate
from db.schemas.nodes import Node, NodeModify
from db.schemas.sdToImg import SdToImgCreate
from db.schemas.txt2img import txt2imgRequest, cnTxt2imgRequest
from db.schemas.users import User, UserCreate
from service.sdService import generate_txtToImg, create_cn_jason, create_txt2img_jason, get_progress_image
from utils.CyptoUtil import mycrypt, aescrypt
from utils.DatetimeUtil import datetime_to_timestamp
from utils.ImageUtil import new_image_hw_by_maxref
from utils.JsonUtil import model_list, object_to_json
from utils.ResponseUtil import JsonResponse
from logs.logger import logger

router = APIRouter()


@router.get("/item")
async def api_read_item(id: str,db: Session = Depends(get_db)):
    # print(id)
    item = get_item(db, item_id=int(id))
    # json_compatible_item_data = jsonable_encoder(item)
    json_compatible_item_data = object_to_json(item)
    return JsonResponse(data=json_compatible_item_data, code=200, message="Success")

@router.get("/item_list", response_model=List[Item])
async def api_read_item_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    item_list_json = model_list(items)
    return JsonResponse(code=200, data=item_list_json, message="Success")

@router.post("/item/create", response_model=Item)
async def api_create_item(
    owner_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    # print(owner_id, title, description)
    new_item = ItemCreate(
            title=title,
            description=description
        )
    create_user_item(db=db, item=new_item, user_id=owner_id)
    return JsonResponse(code=200, data=new_item.json(), message="Success")

@router.get("/get_time")
async def api_read_time():
    get_time = datetime.datetime.now()
    logger.info(f"{datetime.datetime.now()} --> 获取时间")
    return JsonResponse(code=200, data=str(get_time), message="Success")

@router.post("/save_sd_to_img")
async def api_save_sd_to_img(
        seed: int = Form(...),
        uri: str = Form(...),
        type: str = Form(...),
        prompt: str = Form(...),
        content: str = Form(...),
        db: Session = Depends(get_db)
):

    new_sdToImg = SdToImgCreate(
            seed=seed,
            uri=uri,
            type=type,
            prompt=prompt,
            content=content,
    )
    new_sdToImg_json = object_to_json(new_sdToImg)
    create_sdToImg(db=db, sdToImg=new_sdToImg)

    return JsonResponse(code=200, data=new_sdToImg_json, message="Success")

@router.get("/get_sd_to_img")
async def api_get_sd_to_img(id: int, db: Session = Depends(get_db)):
    item = get_img_by_id(db,id)
    item_json = object_to_json(item)
    return JsonResponse(code=200, data=item_json, message="Success")

@router.post("/create_txt_to_img")
async def api_create_txt_to_img(
        prompt: str = Form(...),
        db: Session = Depends(get_db)
):
    # newTxt2img = txt2imgRequest(sd_model='dvarchMultiPrompt_dvarch.ckpt', prompt=prompt)
    newTxt2img = txt2imgRequest(override_settings={"sd_model_checkpoint":"dvArch_-_Multi-Prompt_Architecture_Tuned_Model\\dvarchMultiPrompt_dvarch.ckpt [1ecb6b4e9c]"}, prompt=prompt)
    txt2ImgResult = generate_txtToImg(newTxt2img.json())
    for i in range(len(txt2ImgResult['images'])):
        print(i)
        txt2ImgResult_info = txt2ImgResult['info']
        txt2ImgResult_info_json = json.loads(txt2ImgResult_info)
        new_seed = txt2ImgResult_info_json['seed']
        new_uri = datetime_to_timestamp() + '_' + str(new_seed) + '_' + str(i) + '.png'
        new_type = 'txt2img'
        new_create_by = 'test'
        new_prompt = txt2ImgResult_info_json['prompt']
        new_content = txt2ImgResult['images'][i]
        print(new_seed, new_uri, new_type, new_create_by, new_prompt, new_content)
        api_save_sd_to_img(new_seed, new_uri, new_type, new_prompt, new_content, db)

    return JsonResponse(code=200, data=str(txt2ImgResult), message="Success")

@router.post("/create_controlnet_txt_to_img")
async def api_create_contelnet_txt_to_img(
        prompt: str = Form(...),
        db: Session = Depends(get_db)
):
    newTxt2img = cnTxt2imgRequest(override_settings={"sd_model_checkpoint":"dvArch_-_Multi-Prompt_Architecture_Tuned_Model\\dvarchMultiPrompt_dvarch.ckpt [1ecb6b4e9c]"}, prompt=prompt)
    txt2ImgResult = generate_txtToImg(newTxt2img.json())
    for i in range(len(txt2ImgResult['images'])):
        print(i)
        txt2ImgResult_info = txt2ImgResult['info']
        txt2ImgResult_info_json = json.loads(txt2ImgResult_info)
        new_seed = txt2ImgResult_info_json['seed']
        new_uri = datetime_to_timestamp() + '_' + str(new_seed) + '_' + str(i) + '.png'
        new_type = 'ctrlnet-txt2img'
        new_create_by = 'test'
        new_prompt = txt2ImgResult_info_json['prompt']
        new_content = txt2ImgResult['images'][i]
        print(new_seed, new_uri, new_type, new_create_by, new_prompt, new_content)
        api_save_sd_to_img(new_seed, new_uri, new_type, new_prompt, new_content, db)

    return JsonResponse(code=200, data=str(txt2ImgResult), message="Success")

async def apt_get_img_content(img_id):
    request_result = api_get_sd_to_img(img_id, next(get_db()))
    request_json = object_to_json(request_result)
    request_body = request_json.get('body')
    request_body_json = json.loads(request_body)
    request_data = request_body_json['data']
    request_seed = request_data['seed']
    request_content = request_data['content']
    img_name = datetime_to_timestamp() + '_' + str(request_seed) + '.png'
    with open(img_name, "wb") as image_file:
        image_file.write(base64.b64decode(request_content))
    return request_content

# @shared_task
@celery_app.task
def get_divide(x, y):
    logger.info("get_divide start")
    result = float(x)/float(y)
    time.sleep(10)
    logger.info("get_divide end", result)
    return result


@router.get("/celery")
async def calc(x, y):
    result = get_divide.delay(x, y)
    uuid = result.id
    print(uuid)
    # print(result)
    # result_json = {
    #     "result": result
    # }
    return JsonResponse(code=200, data=uuid, message="Success")

@router.get("/get_redis")
async def get_redis_by_key(key: str, redis: MyRedis = Depends(get_redis)):
    redis_result = await redis.list_loads(key,10)
    # redis_result_list = await new_redis.list_loads(key, 10)

    return JsonResponse(code=200, data=redis_result, message="Success")

@router.post("/set_redis")
async def set_redis_by_key(key: str, value: str, redis: MyRedis = Depends(get_redis)):
    await redis.cus_lpush(key)
    redis_result = {
        "action": "add",
        "key": key,
        "value": value
    }
    # redis_result_list = await new_redis.list_loads(key, 10)

    return JsonResponse(code=200, data=redis_result, message="Success")

@router.post("/delete_redis")
async def delete_redis_by_key(key: str, value: Optional[str] = None, redis: MyRedis = Depends(get_redis)):
    if value is None:
        await redis.delete(key)
    else:
        await redis.delete(key, value)
    redis_result = {
        "action": "delete",
        "key": key,
    }

    return JsonResponse(code=200, data=redis_result, message="Success")

@router.get("/redis_test", summary="测试redis")
async def test_redis(request: Request, num: int=Query(123, title="参数num")):
    # 等待redis写入  await异步变同步 如果不关心结果可以不用await，但是这里下一步要取值，必须得先等存完值 后再取值
    await request.app.state.redis.set("aa", num)
    # 等待 redis读取
    v = await request.app.state.redis.get("aa")
    print(v, type(v))
    return {"msg": v}

@router.post("/user/create", response_model=User)
def create_user_detail(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.get("/nodes_check", response_model=Node)
def check_available_node(request: Request, node_type: str, db: Session = Depends(get_db)):
    nodes = get_nodes_type(db, node_type=node_type)
    available_nodes = []
    for node in nodes:
        node_name = node.name
        print(node_name)
        # if node_name.startswith("http://"):
        #     node_status = is_port_open(node_name.replace("http://","").replace("/",""), 80)
        # else:
        #     node_status = is_port_open(node_name.replace("https://","").replace("/",""), 443)
        # if node_status:
        #     node.status = 1
        try:
            progress, eta_relative, current_image = get_progress_image(node_name)
            if progress == 0.0 and eta_relative == 0.0:
                node.status = 1 # 1:available
                available_nodes.append(node_name)
            else:
                node.status = 2 # 2:busy
        except Exception as e:
                node.status = -1 # -1:unavailable

        new_node = NodeModify(
            id=node.id,
            status=node.status,
            name=node.name,
            type=node.type,
        )

        modify_node(db=db, node=new_node)

    return JsonResponse(code=200, data=available_nodes, message="Success")

if __name__ == '__main__':
    # MyRedis = Depends(get_redis)
    # MyRedis.cus_lpush("1", "Union[str, list, dict]")

    import tracemalloc

    tracemalloc.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(calc(1, 2))





