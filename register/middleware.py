# -*- coding: utf-8 -*-
import json
import time
import uuid
from datetime import timedelta
from typing import List

from fastapi import FastAPI, Request
from sqlalchemy.exc import OperationalError
from aioredis.exceptions import ConnectionError
from starlette import status

# 权限验证 https://www.cnblogs.com/mazhiyong/p/13433214.html
# 得到真实ip https://stackoverflow.com/questions/60098005/fastapi-starlette-get-client-real-ip
# nginx 解决跨域请求 https://segmentfault.com/a/1190000019227927
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
# from fastapi_babel import _  # noqa
# from fastapi_babel import Babel, BabelConfigs
from db.database import get_db
from libs.fastapi_babel import _

from core import i18n
from core.i18n import configs, babel
from core.config import settings
from dependencies import templates
from logs.logger import logger
from register.exception import resp_500_error_page, resp_403_error_page
from service.menuService import get_menu_list, find_parent_menu, get_menu_list_by_user_permission, get_menu_path_by_user_permission
from utils.JsonUtil import check_list_in_str, obj_as_json

trust_hosts = [
    "suai.cloudtim.com",
    "stable_2080super_api.cloudtim.com",
    "stable_2080super.cloudtim.com",
    "localhost",
    "127.0.0.1",
    "0.0.0.0"
]



def register_middleware(app: FastAPI):
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trust_hosts
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    """ 请求拦截与响应拦截 -- https://fastapi.tiangolo.com/tutorial/middleware/ """
    @app.middleware("http")
    async def intercept(request: Request, call_next):
        if '/static/' in request.url.path:
            return await call_next(request)
        logger.info(f"访问记录:IP:{request.client.host}-method:{request.method}-url:{request.url}")
        try:
            await request.app.state.redis.incr('request_num')  # redis 请求数量 (自增 1)
            return await call_next(request)  # 返回请求(跳过token)
        except ConnectionError as e:
            logger.error(f'redis连接失败！-- {e}')
            # return resp_500(msg=f'redis连接失败！')
            request.session["error"] = _("redis_connect_error")
            return resp_500_error_page(request, "500_error_message")

        except OperationalError as e:
            logger.error(f'数据库连接失败！-- {e}')
            request.session["error"] = _("database_connect_error")
            return resp_500_error_page(request, "500_error_message")
            # return resp_500(msg=f'数据库连接失败！')

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    @app.middleware("http")
    async def add_tracing_header(request: Request, call_next):
        trace_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response

    @app.middleware("http")
    async def check_cookie(request: Request, call_next):
        if check_list_in_str(['api', 'captcha', 'login', 'logout', 'register', '/static/', 'favicon.ico', 'forget_password'], request.url.path):
            return await call_next(request)
        cookies = request.cookies
        if 'token' not in cookies:
            request.session["error"] = _("not_auth_please_login_401")
            return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)
        else:
            user_token = cookies.get('token')
            get_user = await request.app.state.redis.get(user_token)
            try:
                if get_user is not None:
                    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                    await request.app.state.redis.set(user_token, get_user, access_token_expires)
                    return await call_next(request)  # 返回请求(跳过token)
                else:
                    request.session["error"] = _("token_expired_please_relogin_401")
                    return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)
            except Exception as e:
                # return handle_exception(request, e)
                return resp_500_error_page(request, e)

    @app.middleware("http")
    async def exception_handling(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # return handle_exception(request, e)
            return resp_500_error_page(request, e)

    @app.middleware("http")
    async def language_processor(request: Request, call_next):
        locale = request.cookies.get("language")
        if not locale:
            accept_language = request.headers.get("Accept-Language")
            if accept_language:
                locale = accept_language.split(";")[0].split("-")[0]
            else:
                locale = 'en'
            babel.locale = locale
            response = await call_next(request)
            response.set_cookie(key="language", value=locale)

        else:
            babel.locale = locale
            response = await call_next(request)
        return response

    # 加载菜单到request.state中
    @app.middleware("http")
    async def add_menu_items_to_request(request: Request, call_next):
        if check_list_in_str(['api', 'error_page','captcha', 'login', 'logout', 'register', '/static/', 'favicon.ico', 'forget_password'], request.url.path):
            return await call_next(request)

        uri = str(request.url)
        current_menu = uri.split('/')[3]
        # print(current_menu)

        login_as = request.cookies.get("login")
        if login_as is None:
            request.session["error"] = _("token_expired_please_relogin_401")
            return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)

        user_allow_menu_path_json = await request.app.state.redis.get(login_as + '_user_allow_menu_path')
        # print(user_allow_menu_path_json)
        if user_allow_menu_path_json is None:
            request.session["error"] = _("token_expired_please_relogin_401")
            return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)
        user_allow_menu_path = json.loads(user_allow_menu_path_json)
        user_allow_menu_path.append('/profile')
        # print(user_allow_menu_path)
        menu_path_items_json = await request.app.state.redis.get(login_as + '_menu_items')
        if menu_path_items_json is None:
            request.session["error"] = _("token_expired_please_relogin_401")
            return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)
        # print(menu_path_items_json)
        menu_path_items = json.loads(menu_path_items_json)
        # print(menu_path_items)
        #     user_allow_menu_path = get_menu_path_by_user_permission(user_login_email=login_as ,db=next(get_db()))
        #     print(login_as, current_menu, uri, user_allow_menu_path)
        if '/' + current_menu not in user_allow_menu_path:
            request.session["error"] = _("menu_is_not_accessible_403")
            return resp_403_error_page(request, "403_error_message")

            # return templates.TemplateResponse(
            #     "errors/error-403.html", status_code=status.HTTP_403_FORBIDDEN, context={"request": request}
            # )
            # return resp_403(msg=f'menu_is_not_accessible！')

        currenty_menus = find_parent_menu('/' + current_menu, db=next(get_db()))
        request.state.currenty_menus = currenty_menus

        # menu_items = get_menu_list(skip=0, limit=100, db=next(get_db()))
        # menu_items = get_menu_list_by_user_permission(user_login_email=login_as, skip=0, limit=100, db=next(get_db()))
        menu_items = menu_path_items
        # print(menu_items)
        request.state.menu_items = menu_items
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def login_info(request: Request, call_next):
        login_as = request.cookies.get("login")

        request.state.login_as = login_as
        response = await call_next(request)
        return response

    # this must add at bottom of the configuration !!!
    # https://github.com/tiangolo/fastapi/discussions/6358
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=60*60*24*3)
