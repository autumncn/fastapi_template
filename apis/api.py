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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.celeryConfig import celery_app
from db.crud.users import get_user_by_email, create_user, get_user, get_users
from db.database import get_db
from db.redis import init_redis_pool, MyRedis, get_redis
from db.schemas.users import User, UserCreate
from utils.CyptoUtil import mycrypt, aescrypt
from utils.DatetimeUtil import datetime_to_timestamp
from utils.ImageUtil import new_image_hw_by_maxref
from utils.JsonUtil import model_list, object_to_json
from utils.ResponseUtil import JsonResponse
from logs.logger import logger

router = APIRouter()


@router.get("/user")
async def api_read_user(id: str,db: AsyncSession = Depends(get_db)):
    # print(id)
    item = get_user(db, item_id=int(id))
    # json_compatible_item_data = jsonable_encoder(item)
    json_compatible_item_data = object_to_json(item)
    return JsonResponse(data=json_compatible_item_data, code=200, message="Success")

@router.get("/item_list", response_model=List[User])
async def api_read_user_list(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    items = get_users(db, skip=skip, limit=limit)
    item_list_json = model_list(items)
    return JsonResponse(code=200, data=item_list_json, message="Success")

@router.get("/get_time")
async def api_read_time():
    get_time = datetime.datetime.now()
    logger.info(f"{datetime.datetime.now()} --> 获取时间")
    return JsonResponse(code=200, data=str(get_time), message="Success")

# @shared_task
@celery_app.task
async def get_divide(x, y):
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
async def create_user_detail(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

if __name__ == '__main__':
    # MyRedis = Depends(get_redis)
    # MyRedis.cus_lpush("1", "Union[str, list, dict]")

    import tracemalloc

    tracemalloc.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(calc(1, 2))





