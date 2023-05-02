import asyncio
import base64
import datetime
import json
import time
from typing import List, Optional

from celery import shared_task
from fastapi import Request, Query

from fastapi.params import Form
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from core.celeryConfig import celery_app
from db import redis
from db.crud.items import get_items, create_user_item, get_item
from db.crud.sdToImg import get_img_by_id, create_sdToImg
from db.database import get_db
from db.redis import init_redis_pool, MyRedis, get_redis
from db.schemas.items import Item, ItemCreate
from db.schemas.sdToImg import SdToImgCreate
from db.schemas.txt2img import txt2imgRequest, cnTxt2imgRequest
from service.sdService import generate_txtToImg, create_cn_jason, create_txt2img_jason
from utils.DatetimeUtil import datetime_to_timestamp
from utils.ImageUtil import new_image_hw_by_maxref
from utils.JsonUtil import model_list, object_to_json
from utils.ResponseUtil import JsonResponse
from logs.logger import logger


async def get_redis_keys(pattern:str = '*'):
    redis = await init_redis_pool()
    # print(redis)
    keys_list = await redis.get_keys(pattern)
    return keys_list

async def get_redis_value_by_key(key:str):
    redis = await init_redis_pool()
    # print(redis)
    key_value = await redis.get_value_by_key(key)
    return {key:key_value}

async def get_redis_by_key(key: str, num = int, redis: MyRedis = Depends(get_redis)):
    redis_result = await redis.list_loads(key,num)
    return JsonResponse(code=200, data=redis_result, message="Success")

async def set_redis_by_key(key: str, value: str, redis: MyRedis = Depends(get_redis)):
    await redis.cus_lpush(key)
    redis_result = {
        "action": "add",
        "key": key,
        "value": value
    }
    return JsonResponse(code=200, data=redis_result, message="Success")

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


if __name__ == '__main__':
    import tracemalloc

    tracemalloc.start()
    loop = asyncio.get_event_loop()
    # sd_model = loop.run_until_complete(get_redis_keys("*"))
    # sd_model = loop.run_until_complete(get_redis_value_by_key('celery-task-meta-afeafd96-f32e-4bd4-86b4-f53886ca35ba'))
    sd_model = loop.run_until_complete(get_redis_value_by_key('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5MkBob3QuY29tIiwiZXhwIjoxNjgyNjA4MzQ3fQ.1wzA4d85UptpaAf08NOKfeNRUbESwVTDXlxCTWgyAzk'))

    print(sd_model)



