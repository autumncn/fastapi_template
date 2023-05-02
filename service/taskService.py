import asyncio
import datetime
import json
import base64
import socket
import time

import httpx
import requests
import ssl
from starlette.requests import Request

from db.redis import get_redis, MyRedis, init_redis_pool

ssl._create_default_https_context = ssl._create_unverified_context
from core.celeryConfig import celery_app

from core.security import create_uid
from utils.JsonUtil import dict_to_json, object_to_json, jsonResponse_to_json

from fastapi import Depends

from db.crud.sdTasks import create_sdTask, get_sd_task_by_uuid, modify_sdTask, get_sd_tasks
from db.schemas.sdTasks import SdTaskCreate, SdTaskModify
from utils.DatetimeUtil import datetime_to_timestamp
from utils.ResponseUtil import JsonResponse
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from db.database import get_db

def create_task(uid, content, status, type, create_by):
    new_task = SdTaskCreate(
        status=status,
        uid=uid,
        type=type,
        content=content,
        create_by=create_by,
        )
    new_sdTask = create_sdTask(db=next(get_db()), sdTask=new_task)
    task_json = object_to_json(new_sdTask)
    return JsonResponse(code=200, data=task_json, message="Success")

def get_task(uid):
    new_task = get_sd_task_by_uuid(db=next(get_db()), sdTask_uid=uid)
    task_json = object_to_json(new_task)
    return JsonResponse(code=200, data=task_json, message="Success")

def modify_task_by_uid(uid, status, content):
    # time.sleep(1)
    old_task = get_sd_task_by_uuid(db=next(get_db()), sdTask_uid=uid)
    # print(uid, status, content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # print(old_task.id)

    new_task = SdTaskModify(
        id=old_task.id,
        status=status,
        content=content,
        update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    new_sdTask = modify_sdTask(db=next(get_db()), sdTask=new_task)
    task_json = object_to_json(new_sdTask)
    return JsonResponse(code=200, data=task_json, message="Success")

def update_task_status():
    tasks = get_sd_tasks(db=next(get_db()), skip=0, limit=100)
    '''
    NOT READY: 0
    PENDING: 1
    STARTED: 2
    SUCCESS: 3
    FAILURE: -1
    UNKONWN: -2
    '''
    for task in tasks:
        # print(task.uid, task.status, task.content)
        task_uid = task.uid
        if task.status == 0 or task.status == 1 or task.status == 2 or task.status == -2:
            task_result = object_to_json(get_task_result(task_uid))['body']
            task_result_body = json.loads(task_result)['data']
            if task_result is None:
                task.status = -1
                modify_sdTask(db=next(get_db()), sdTask=task)
            else:
                if task_result_body['state'] == 'PENDING':
                    if task.status != 1:
                        task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        task.status = 1
                        modify_sdTask(db=next(get_db()), sdTask=task)
                elif task_result_body['state'] == 'STARTED':
                    if task.status != 2:
                        task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        task.status = 2
                        modify_sdTask(db=next(get_db()), sdTask=task)
                elif task_result_body['state'] == 'FAILURE':
                    if task.status != -1:
                        task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        task.status = -1
                        modify_sdTask(db=next(get_db()), sdTask=task)
                else:
                        task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        task.status = -2
                        modify_sdTask(db=next(get_db()), sdTask=task)

        # task_result = object_to_json(get_task_result(task_uid))['body']
        # task_result_body = json.loads(task_result)['data']
        # # print(task_result_body, task_result_body['ready'], task_result_body['state'])
        # if task_result is not None:
        #     if task_result_body['ready'] == False:
        #         # if task.status != 0:
        #         #     task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #         #     task.status = 0
        #         #     modify_sdTask(db=next(get_db()), sdTask=task)
        #         if task_result_body['state'] == 'PENDING':
        #             if task.status != 1:
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 task.status = 1
        #                 modify_sdTask(db=next(get_db()), sdTask=task)
        #         elif task_result_body['state'] == 'STARTED':
        #             if task.status != 2:
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 task.status = 2
        #                 modify_sdTask(db=next(get_db()), sdTask=task)
        #         else:
        #             if task.status != -2:
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 task.status = -2
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 modify_sdTask(db=next(get_db()), sdTask=task)
        #     else:
        #         if task_result_body['state'] == 'SUCCESS':
        #             if task.status != 3:
        #                 # print("taskss", task.status)
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 task.status = 3
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 modify_sdTask(db=next(get_db()), sdTask=task)
        #         elif task_result_body['state'] == 'FAILURE':
        #             if task.status != -1:
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 task.status = -1
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 modify_sdTask(db=next(get_db()), sdTask=task)
        #         else:
        #             if task.status != -2:
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 task.status = -2
        #                 task.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #                 modify_sdTask(db=next(get_db()), sdTask=task)

    return JsonResponse(code=200, data=object_to_json(tasks), message="Success")



def get_task_result(uuid):
    res = celery_app.AsyncResult(id=uuid)
    # print(res)
    task_state = res.state
    # print(task_state)
    task_result = res.result
    # print(res.ready())
    result = {
        "state": task_state,
        "ready": res.ready(),
    }
    '''
SUCCESS
FAILURE
STARTED
PENDING

2.0
{'status_code': 200, 'background': None, 'body': '{"code":200,"message":"SUCCESS","data":2.0}', 'raw_headers': [['content-length', '43'], ['content-type', 'application/json']]}    
    '''
    return JsonResponse(code=200, data=result, message=task_state)

def task_complete_notice(task_id):
    res = celery_app.AsyncResult(id=task_id)
    if res.ready():
        return True
    else:
        return False

if __name__ == '__main__':
    # new_task = create_task('abc')
    # new_task_json = jsonResponse_to_json(new_task)
    # uri = new_task_json['uid']
    # print(uri)

    result = get_task_result('d71f2779-54a1-43fe-96c8-5ae8786a6265')
    request_json = object_to_json(result)
    # print(request_json)

    # modify_task_by_uid('f7e2911d-c5c7-495f-abf1-b699eace04e7', 2, "content")




